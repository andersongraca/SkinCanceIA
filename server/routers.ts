import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { TRPCError } from "@trpc/server";
import { z } from "zod";
import { COOKIE_NAME } from "@shared/const";
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
  getImageById,
  insertDiagnosis,
  insertDermatologicalImage,
} from "./db";
import { classificationService } from "./services/ClassificationService";

const imageMimeTypes = ["image/jpeg", "image/png"] as const;
const uploadRoot = path.resolve(
  process.env.ML_UPLOAD_ROOT || path.join(process.env.ML_PROJECT_ROOT || process.cwd(), "runtime", "uploads"),
);
const persistentStorageConfigured = Boolean(ENV.forgeApiUrl && ENV.forgeApiKey);

type HeatmapPaths = { cnnHeatmapPath: string; vitHeatmapPath: string; hybridHeatmapPath: string };

type MaterializedImage = { localPath: string; cleanup: boolean };

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
    };
  }
  const upload = async (filePath: string, model: string) => {
    const content = await fs.readFile(filePath);
    const stored = await storagePut(`diagnosis-heatmaps/${userId}/${imageId}/${randomUUID()}-${model}.png`, content, "image/png");
    return stored.url;
  };
  const [cnnHeatmapPath, vitHeatmapPath, hybridHeatmapPath] = await Promise.all([
    upload(paths.cnnHeatmapPath, "cnn-gradcam"),
    upload(paths.vitHeatmapPath, "vit-token-gradient"),
    upload(paths.hybridHeatmapPath, "hybrid-combined"),
  ]);
  return { cnnHeatmapPath, vitHeatmapPath, hybridHeatmapPath };
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
        const buffer = decodeImageDataUrl(input.dataUrl, input.mimeType);
        const stored = await persistImage(buffer, input.fileName, input.mimeType, ctx.user.id);
        const image = await insertDermatologicalImage({
          userId: ctx.user.id,
          fileName: input.fileName,
          imagePath: stored.imagePath,
          fileSize: buffer.length,
          mimeType: input.mimeType,
        });
        if (!image) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "Não foi possível registrar a imagem." });
        return { imageId: image.id, fileName: image.fileName, imageUrl: stored.imageUrl };
      }),

    classifyStoredImage: protectedProcedure
      .input(z.object({ imageId: z.number().int().positive() }))
      .mutation(async ({ ctx, input }) => {
        const image = await getImageById(input.imageId);
        if (!image || image.userId !== ctx.user.id) {
          throw new TRPCError({ code: "NOT_FOUND", message: "Imagem não encontrada ou acesso negado." });
        }
        const materialized = await materializeImage(image.imagePath, image.mimeType);
        try {
          let result;
          try {
            result = await classificationService.classifyImage(materialized.localPath);
          } catch (error) {
            const candidate = error as Error & { code?: string; eligibility?: { accepted: boolean; status: "accepted" | "rejected"; reasons: string[]; warnings: string[]; width?: number; height?: number; quality_score?: number; ood_score?: number | null; ood_threshold?: number | null } };
            if (candidate.code === "IMAGE_NOT_ELIGIBLE" && candidate.eligibility) {
              return { status: "rejected" as const, imageId: image.id, eligibility: candidate.eligibility };
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
          return { status: "classified" as const, diagnosis, result: resultWithHeatmaps };
        } finally {
          if (materialized.cleanup) await fs.rm(materialized.localPath, { force: true });
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
