import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { createHash, randomUUID } from "node:crypto";
import { TRPCError } from "@trpc/server";
import { z } from "zod";
import { COOKIE_NAME } from "@shared/const";
import type { DermatologicalImage } from "../drizzle/schema";
import { getSessionCookieOptions } from "./_core/cookies";
import { ENV } from "./_core/env";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router, protectedProcedure } from "./_core/trpc";
import { storageGet, storagePut } from "./storage";
import {
  getUserDiagnosisHistory,
  getDiagnosisById,
  getAllModelMetrics,
  getModelMetrics,
  getAnalysisRunsByImage,
  getImageById,
  insertAnalysisRun,
  insertDiagnosis,
  insertDermatologicalImage,
} from "./db";
import { classificationService } from "./services/ClassificationService";

const imageMimeTypes = ["image/jpeg", "image/png"] as const;
const uploadRoot = path.resolve(
  process.env.ML_UPLOAD_ROOT || path.join(process.env.ML_PROJECT_ROOT || process.cwd(), "runtime", "uploads"),
);
const persistentStorageConfigured = Boolean(ENV.forgeApiUrl && ENV.forgeApiKey);

type HeatmapPaths = { cnnHeatmapPath: string; vitHeatmapPath: string; hybridHeatmapPath: string; ensembleHeatmapPath: string };

type MaterializedImage = { localPath: string; cleanup: boolean };

type RateLimitEntry = { windowStartedAt: number; count: number };
const rateLimitWindowMs = 10 * 60 * 1000;
const rateLimitStore = new Map<string, RateLimitEntry>();
const maxConcurrentInference = Math.max(Number.parseInt(process.env.ML_MAX_CONCURRENT_INFERENCE || "", 10) || 1, 1);
let activeInferences = 0;
const localImages = new Map<number, DermatologicalImage>();
let nextLocalImageId = 1;

function isLocalInferenceMode(): boolean {
  return ENV.isLocalDemoMode && !ENV.isProduction;
}

function requesterKey(req: { ip?: string; headers?: Record<string, unknown>; socket?: { remoteAddress?: string } }, userId: number, action: string): string {
  const forwarded = typeof req.headers?.["x-forwarded-for"] === "string" ? req.headers["x-forwarded-for"].split(",")[0]?.trim() : undefined;
  return `${action}:${userId}:${forwarded || req.ip || req.socket?.remoteAddress || "unknown"}`;
}

function enforceRateLimit(req: Parameters<typeof requesterKey>[0], userId: number, action: string, maxRequests: number): void {
  const now = Date.now();
  const key = requesterKey(req, userId, action);
  const current = rateLimitStore.get(key);
  if (!current || now - current.windowStartedAt >= rateLimitWindowMs) {
    rateLimitStore.set(key, { windowStartedAt: now, count: 1 });
    return;
  }
  if (current.count >= maxRequests) {
    throw new TRPCError({ code: "TOO_MANY_REQUESTS", message: "Limite temporário de solicitações excedido. Tente novamente mais tarde." });
  }
  current.count += 1;
}

function acquireInferenceSlot(): () => void {
  if (activeInferences >= maxConcurrentInference) {
    throw new TRPCError({ code: "TOO_MANY_REQUESTS", message: "O servidor está processando outras análises. Tente novamente em instantes." });
  }
  activeInferences += 1;
  let released = false;
  return () => {
    if (!released) {
      released = true;
      activeInferences = Math.max(0, activeInferences - 1);
    }
  };
}

function hasExpectedImageSignature(buffer: Buffer, mimeType: (typeof imageMimeTypes)[number]): boolean {
  if (mimeType === "image/jpeg") return buffer.length >= 3 && buffer[0] === 0xff && buffer[1] === 0xd8 && buffer[2] === 0xff;
  return buffer.length >= 8 && Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]).equals(buffer.subarray(0, 8));
}

const checkpointHashCache = new Map<string, string>();

async function getCheckpointHashes(): Promise<Record<string, string>> {
  const root = path.resolve(process.env.ML_PROJECT_ROOT || process.cwd());
  const paths: Record<string, string> = {
    cnn: process.env.ML_CNN_CHECKPOINT || path.join(root, "ml_artifacts", "ham10000", "cnn", "best.pt"),
    vit: process.env.ML_VIT_CHECKPOINT || path.join(root, "ml_artifacts", "ham10000", "vit", "best.pt"),
    hybrid: process.env.ML_HYBRID_CHECKPOINT || path.join(root, "ml_artifacts", "ham10000", "hybrid", "best.pt"),
  };
  const result: Record<string, string> = {};
  for (const [model, checkpointPath] of Object.entries(paths)) {
    const resolved = path.resolve(checkpointPath);
    const cached = checkpointHashCache.get(resolved);
    if (cached) {
      result[model] = cached;
      continue;
    }
    try {
      const content = await fs.readFile(resolved);
      const hash = createHash("sha256").update(content).digest("hex");
      checkpointHashCache.set(resolved, hash);
      result[model] = hash;
    } catch {
      result[model] = "unavailable";
    }
  }
  return result;
}

function safeStem(fileName: string): string {
  const stem = path.basename(fileName, path.extname(fileName));
  return stem.replace(/[^a-zA-Z0-9._-]/g, "_").slice(0, 80) || "image";
}

function publicArtifactUrl(filePath: string): string {
  const relative = path.relative(uploadRoot, filePath);
  if (!relative || relative.startsWith("..") || path.isAbsolute(relative)) {
    throw new Error("Artefato fora do diretório público permitido.");
  }
  const encoded = relative.split(path.sep).map(segment => encodeURIComponent(segment)).join("/");
  return `/api/ml-artifacts/${encoded}`;
}

function decodeImageDataUrl(dataUrl: string, mimeType: (typeof imageMimeTypes)[number]): Buffer {
  const prefix = `data:${mimeType};base64,`;
  if (!dataUrl.startsWith(prefix)) {
    throw new TRPCError({ code: "BAD_REQUEST", message: "O conteúdo da imagem não corresponde ao tipo MIME informado." });
  }
  const base64 = dataUrl.slice(prefix.length);
  if (!base64 || !/^[A-Za-z0-9+/]+={0,2}$/.test(base64)) {
    throw new TRPCError({ code: "BAD_REQUEST", message: "Dados base64 inválidos para a imagem." });
  }
  const buffer = Buffer.from(base64, "base64");
  if (!buffer.length || buffer.length > 10 * 1024 * 1024) {
    throw new TRPCError({ code: "BAD_REQUEST", message: "A imagem deve possuir entre 1 byte e 10 MB." });
  }
  if (!hasExpectedImageSignature(buffer, mimeType)) {
    throw new TRPCError({ code: "BAD_REQUEST", message: "O conteúdo não corresponde a um JPEG ou PNG válido." });
  }
  return buffer;
}

async function persistImage(buffer: Buffer, fileName: string, mimeType: (typeof imageMimeTypes)[number], userId: number) {
  const extension = mimeType === "image/png" ? ".png" : ".jpg";
  const uniqueName = `${randomUUID()}-${safeStem(fileName)}${extension}`;
  if (persistentStorageConfigured) {
    const stored = await storagePut(`diagnosis-images/${userId}/${new Date().toISOString().slice(0, 10)}/${uniqueName}`, buffer, mimeType);
    return { imagePath: stored.key, imageUrl: stored.url };
  }
  if (ENV.isProduction) {
    throw new TRPCError({ code: "PRECONDITION_FAILED", message: "Armazenamento persistente não configurado para produção." });
  }
  const directory = path.join(uploadRoot, String(userId), new Date().toISOString().slice(0, 10));
  await fs.mkdir(directory, { recursive: true });
  const storedPath = path.join(directory, uniqueName);
  await fs.writeFile(storedPath, buffer, { flag: "wx" });
  return { imagePath: storedPath, imageUrl: publicArtifactUrl(storedPath) };
}

async function materializeImage(imagePath: string, mimeType: string): Promise<MaterializedImage> {
  if (path.isAbsolute(imagePath)) {
    try {
      await fs.access(imagePath);
      return { localPath: imagePath, cleanup: false };
    } catch {
      // Path may be a stale local reference; attempt persistent storage below.
    }
  }
  if (!persistentStorageConfigured) {
    throw new Error("Imagem persistida não está acessível no filesystem local nem no armazenamento persistente.");
  }
  const stored = await storageGet(imagePath);
  const response = await fetch(stored.url);
  if (!response.ok) throw new Error(`Falha ao baixar imagem persistida (${response.status}).`);
  const bytes = Buffer.from(await response.arrayBuffer());
  if (!bytes.length || bytes.length > 10 * 1024 * 1024) throw new Error("Imagem persistida excede o limite de 10 MB.");
  const extension = mimeType === "image/png" ? ".png" : ".jpg";
  const temporaryPath = path.join(os.tmpdir(), `dermoscopy-${randomUUID()}${extension}`);
  await fs.writeFile(temporaryPath, bytes, { flag: "wx" });
  return { localPath: temporaryPath, cleanup: true };
}

async function persistHeatmaps(paths: HeatmapPaths, userId: number, imageId: number): Promise<HeatmapPaths> {
  if (!persistentStorageConfigured) {
    if (ENV.isProduction) throw new Error("Armazenamento persistente não configurado para heatmaps.");
    return {
      cnnHeatmapPath: publicArtifactUrl(paths.cnnHeatmapPath),
      vitHeatmapPath: publicArtifactUrl(paths.vitHeatmapPath),
      hybridHeatmapPath: publicArtifactUrl(paths.hybridHeatmapPath),
      ensembleHeatmapPath: publicArtifactUrl(paths.ensembleHeatmapPath),
    };
  }
  const upload = async (filePath: string, model: string) => {
    const content = await fs.readFile(filePath);
    const stored = await storagePut(`diagnosis-heatmaps/${userId}/${imageId}/${randomUUID()}-${model}.png`, content, "image/png");
    return stored.url;
  };
  const [cnnHeatmapPath, vitHeatmapPath, hybridHeatmapPath, ensembleHeatmapPath] = await Promise.all([
    upload(paths.cnnHeatmapPath, "cnn-gradcam"),
    upload(paths.vitHeatmapPath, "vit-token-gradient"),
    upload(paths.hybridHeatmapPath, "hybrid-combined"),
    upload(paths.ensembleHeatmapPath, "ensemble-learning"),
  ]);
  return { cnnHeatmapPath, vitHeatmapPath, hybridHeatmapPath, ensembleHeatmapPath };
}

export const appRouter = router({
  system: systemRouter,

  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),

  diagnosis: router({
    uploadImage: protectedProcedure
      .input(z.object({
        fileName: z.string().min(1).max(255),
        mimeType: z.enum(imageMimeTypes),
        dataUrl: z.string().max(15_000_000),
      }))
      .mutation(async ({ ctx, input }) => {
        enforceRateLimit(ctx.req, ctx.user.id, "upload", Math.max(Number.parseInt(process.env.ML_UPLOAD_RATE_LIMIT || "", 10) || 30, 1));
        const buffer = decodeImageDataUrl(input.dataUrl, input.mimeType);
        const stored = await persistImage(buffer, input.fileName, input.mimeType, ctx.user.id);
        let image: DermatologicalImage | null = null;
        try {
          image = await insertDermatologicalImage({
            userId: ctx.user.id,
            fileName: input.fileName,
            imagePath: stored.imagePath,
            fileSize: buffer.length,
            mimeType: input.mimeType,
          });
        } catch (error) {
          if (!isLocalInferenceMode()) throw error;
          console.warn("[Local inference] Banco indisponível; upload mantido temporariamente.");
        }
        if (!image && isLocalInferenceMode()) {
          const localImage: DermatologicalImage = {
            id: nextLocalImageId++,
            userId: ctx.user.id,
            fileName: input.fileName,
            imagePath: stored.imagePath,
            thumbnailPath: null,
            fileSize: buffer.length,
            mimeType: input.mimeType,
            description: null,
            uploadedAt: new Date(),
            updatedAt: new Date(),
          };
          localImages.set(localImage.id, localImage);
          image = localImage;
        }
        if (!image) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Não foi possível registrar a imagem." });
        return { imageId: image.id, fileName: image.fileName, imageUrl: stored.imageUrl };
      }),

    classifyStoredImage: protectedProcedure
      .input(z.object({ imageId: z.number().int().positive() }))
      .mutation(async ({ ctx, input }) => {
        enforceRateLimit(ctx.req, ctx.user.id, "classification", Math.max(Number.parseInt(process.env.ML_CLASSIFICATION_RATE_LIMIT || "", 10) || 20, 1));
        const analysisRunId = randomUUID();
        const analysisStartedAt = new Date();
        const releaseInferenceSlot = acquireInferenceSlot();
        const image = localImages.get(input.imageId) ?? await getImageById(input.imageId);
        if (!image || image.userId !== ctx.user.id) {
          releaseInferenceSlot();
          throw new TRPCError({ code: "NOT_FOUND", message: "Imagem não encontrada ou acesso negado." });
        }
        let materialized: MaterializedImage | null = null;
        try {
          materialized = await materializeImage(image.imagePath, image.mimeType);
          let result;
          try {
            result = await classificationService.classifyImage(materialized.localPath);
          } catch (error) {
            const candidate = error as Error & { code?: string; eligibility?: { accepted: boolean; status: "accepted" | "rejected"; reasons: string[]; warnings: string[]; width?: number; height?: number; quality_score?: number; ood_score?: number | null; ood_threshold?: number | null; features?: Record<string, number> } };
            if (candidate.code === "IMAGE_NOT_ELIGIBLE" && candidate.eligibility) {
              try {
                await insertAnalysisRun({
                  imageId: image.id,
                  userId: ctx.user.id,
                  runId: analysisRunId,
                  status: "rejected",
                  rejectionReasons: JSON.stringify(candidate.eligibility.reasons),
                  oodScore: candidate.eligibility.ood_score ?? null,
                  oodThreshold: candidate.eligibility.ood_threshold ?? null,
                  qualityScore: candidate.eligibility.quality_score ?? null,
                  eligibilityFeatures: candidate.eligibility.features ? JSON.stringify(candidate.eligibility.features) : null,
                  thresholds: JSON.stringify({
                    ood: candidate.eligibility.ood_threshold ?? null,
                    quality: candidate.eligibility.quality_score ?? null,
                  }),
                  startedAt: analysisStartedAt,
                  completedAt: new Date(),
                });
              } catch (runError) {
                console.warn("Execução científica recusada não persistida:", runError);
              }
              return { status: "rejected" as const, imageId: image.id, eligibility: candidate.eligibility };
            }
            try {
              await insertAnalysisRun({
                imageId: image.id,
                userId: ctx.user.id,
                runId: analysisRunId,
                status: "failed",
                rejectionReasons: JSON.stringify([candidate.message || "Falha na triagem ou classificação da imagem."]),
                startedAt: analysisStartedAt,
                completedAt: new Date(),
              });
            } catch (runError) {
              console.warn("Execução científica com falha não persistida:", runError);
            }
            throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Falha na triagem ou classificação da imagem." });
          }

          let heatmaps: HeatmapPaths | undefined;
          try {
            const outputDirectory = path.join(uploadRoot, "heatmaps", String(ctx.user.id), String(image.id), randomUUID());
            const generated = await classificationService.generateAllHeatmaps(materialized.localPath, outputDirectory);
            heatmaps = await persistHeatmaps(generated, ctx.user.id, image.id);
          } catch (error) {
            console.warn("Heatmaps não persistidos para o diagnóstico:", error);
          }

          const resultWithHeatmaps = { ...result, heatmaps };
          const diagnosis = await insertDiagnosis({
            imageId: image.id,
            userId: ctx.user.id,
            classification: result.finalClassification,
            confidence: Math.round(result.finalConfidence),
            cnnResult: result.cnnResult.classification,
            cnnConfidence: Math.round(result.cnnResult.confidence),
            vitResult: result.vitResult.classification,
            vitConfidence: Math.round(result.vitResult.confidence),
            hybridResult: result.hybridResult.classification,
            hybridConfidence: Math.round(result.hybridResult.confidence),
            heatmapPath: heatmaps ? JSON.stringify(heatmaps) : null,
            modelVersion: result.ensembleResult.modelVersion || process.env.ML_MODEL_VERSION || "untrained",
          });
          try {
            await insertAnalysisRun({
              imageId: image.id,
              userId: ctx.user.id,
              runId: analysisRunId,
              status: result.ensembleResult.uncertainty?.abstain ? "abstained" : "classified",
              qualityScore: result.eligibility.quality_score ?? null,
              eligibilityFeatures: result.eligibility.features ? JSON.stringify(result.eligibility.features) : null,
              oodScore: result.eligibility.ood_score ?? null,
              oodThreshold: result.eligibility.ood_threshold ?? null,
              finalClassification: result.finalClassification,
              finalConfidence: result.finalConfidence,
              abstained: result.ensembleResult.uncertainty?.abstain ? 1 : 0,
              predictiveEntropy: result.ensembleResult.uncertainty?.predictiveEntropy ?? null,
              ttaVariance: result.ensembleResult.uncertainty?.ttaVariance ?? null,
              modelVersion: result.ensembleResult.modelVersion || process.env.ML_MODEL_VERSION || "untrained",
              modelHashes: JSON.stringify(await getCheckpointHashes()),
              thresholds: JSON.stringify({
                entropy: process.env.ML_ENTROPY_THRESHOLD || "0.65",
                ttaVariance: process.env.ML_TTA_VARIANCE_THRESHOLD || "0.02",
                ensembleVotes: process.env.ML_ENSEMBLE_ABSTAIN_VOTES || "2",
                ensembleEntropy: process.env.ML_ENSEMBLE_ENTROPY_THRESHOLD || "0.65",
                ensembleTtaVariance: process.env.ML_ENSEMBLE_TTA_VARIANCE_THRESHOLD || "0.02",
              }),
              modelResults: JSON.stringify({
                cnn: result.cnnResult,
                vit: result.vitResult,
                hybrid: result.hybridResult,
                ensemble: result.ensembleResult,
              }),
              heatmapPaths: heatmaps ? JSON.stringify(heatmaps) : null,
              startedAt: analysisStartedAt,
              completedAt: new Date(),
            });
          } catch (runError) {
            console.warn("Execução científica classificada não persistida:", runError);
          }
          return { status: "classified" as const, diagnosis, result: resultWithHeatmaps };
        } finally {
          if (materialized?.cleanup) await fs.rm(materialized.localPath, { force: true });
          releaseInferenceSlot();
        }
      }),

    getHistory: protectedProcedure.query(async ({ ctx }) => {
      try {
        return await getUserDiagnosisHistory(ctx.user.id);
      } catch (error) {
        console.error("Erro ao obter histórico de diagnósticos:", error);
        throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Falha ao obter histórico de diagnósticos." });
      }
    }),

    getById: protectedProcedure
      .input(z.object({ id: z.number().int().positive() }))
      .query(async ({ ctx, input }) => {
        const diagnosis = await getDiagnosisById(input.id);
        if (!diagnosis || diagnosis.userId !== ctx.user.id) {
          throw new TRPCError({ code: "NOT_FOUND", message: "Diagnóstico não encontrado ou acesso negado." });
        }
        return diagnosis;
      }),

    getAnalysisRuns: protectedProcedure
      .input(z.object({ imageId: z.number().int().positive() }))
      .query(async ({ ctx, input }) => {
        const image = await getImageById(input.imageId);
        if (!image || image.userId !== ctx.user.id) {
          throw new TRPCError({ code: "NOT_FOUND", message: "Imagem não encontrada ou acesso negado." });
        }
        return getAnalysisRunsByImage(input.imageId);
      }),
  }),

  metrics: router({
    getAllMetrics: publicProcedure.query(async () => getAllModelMetrics()),
    getMetricsByModel: publicProcedure
      .input(z.object({ modelName: z.string().min(1).max(100) }))
      .query(async ({ input }) => {
        const metric = await getModelMetrics(input.modelName);
        if (!metric) throw new TRPCError({ code: "NOT_FOUND", message: "Métricas não encontradas." });
        return metric;
      }),
  }),
});

export type AppRouter = typeof appRouter;
