import "dotenv/config";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import path from "node:path";

const execFileAsync = promisify(execFile);

export interface PythonClassificationResult {
  classification: "benign" | "malignant";
  confidence: number;
  probabilities: { benign: number; malignant: number };
  fineGrainedClass?: string;
  fineGrainedProbabilities?: Record<string, number>;
  uncertainty?: {
    predictiveEntropy: number;
    ttaVariance: number;
    abstain: boolean;
  };
  ttaSamples?: number;
  modelVersion?: string;
}

export interface PythonHeatmapResult {
  targetClass: string;
  method: string[];
  paths: Record<string, string>;
}

export interface ImageEligibilityResult {
  accepted: boolean;
  status: "accepted" | "rejected";
  reasons: string[];
  warnings: string[];
  width?: number;
  height?: number;
  quality_score?: number;
  ood_score?: number | null;
  ood_threshold?: number | null;
  features?: Record<string, number>;
}

function configuredRoot(): string {
  return path.resolve(process.env.ML_PROJECT_ROOT || process.cwd());
}

function configuredPython(): string {
  return process.env.ML_PYTHON_PATH || "python3";
}

function ensureCheckpoint(checkpointPath: string | undefined, modelName: string): string {
  if (!checkpointPath) {
    throw new Error(`Checkpoint do modelo ${modelName} não configurado. Defina a variável ML_${modelName.toUpperCase()}_CHECKPOINT.`);
  }
  return path.resolve(checkpointPath);
}

function parseJsonLine(stdout: string): unknown {
  const lines = stdout.trim().split(/\r?\n/).filter(Boolean);
  const candidate = lines.at(-1);
  if (!candidate) throw new Error("O pipeline Python não retornou uma resposta JSON.");
  try {
    return JSON.parse(candidate);
  } catch {
    throw new Error(`Resposta inválida do pipeline Python: ${candidate.slice(0, 300)}`);
  }
}

export class PythonInferenceService {
  private readonly timeoutMs = Number(process.env.ML_INFERENCE_TIMEOUT_MS || 120_000);

  async validateImage(imagePath: string): Promise<ImageEligibilityResult> {
    const reference = process.env.ML_DOMAIN_REFERENCE || path.join(configuredRoot(), "ml_artifacts", "ham10000", "quality_reference.json");
    const { stdout, stderr } = await execFileAsync(
      configuredPython(),
      ["-m", "ml.skin_cancer_ml.quality", "--image", path.resolve(imagePath), "--reference", path.resolve(reference), "--require-reference"],
      {
        cwd: configuredRoot(),
        env: { ...process.env, PYTHONPATH: configuredRoot() },
        timeout: Math.min(this.timeoutMs, 30_000),
        maxBuffer: 2 * 1024 * 1024,
      },
    );
    if (stderr.trim()) console.warn(`[ML:quality] ${stderr.trim().slice(0, 1000)}`);
    return parseJsonLine(stdout) as ImageEligibilityResult;
  }

  async classify(checkpointPath: string | undefined, modelName: string, imagePath: string): Promise<PythonClassificationResult> {
    const checkpoint = ensureCheckpoint(checkpointPath, modelName);
    const { stdout, stderr } = await execFileAsync(
      configuredPython(),
      ["-m", "ml.skin_cancer_ml.infer", "--checkpoint", checkpoint, "--image", path.resolve(imagePath)],
      {
        cwd: configuredRoot(),
        env: { ...process.env, PYTHONPATH: configuredRoot() },
        timeout: this.timeoutMs,
        maxBuffer: 4 * 1024 * 1024,
      },
    );
    if (stderr.trim()) console.warn(`[ML:${modelName}] ${stderr.trim().slice(0, 1000)}`);
    return parseJsonLine(stdout) as PythonClassificationResult;
  }

  async explain(
    checkpointPath: string | undefined,
    modelName: string,
    imagePath: string,
    outputPath: string,
  ): Promise<PythonHeatmapResult> {
    const checkpoint = ensureCheckpoint(checkpointPath, modelName);
    const { stdout, stderr } = await execFileAsync(
      configuredPython(),
      ["-m", "ml.skin_cancer_ml.explain", "--checkpoint", checkpoint, "--image", path.resolve(imagePath), "--output", path.resolve(outputPath)],
      {
        cwd: configuredRoot(),
        env: { ...process.env, PYTHONPATH: configuredRoot() },
        timeout: this.timeoutMs,
        maxBuffer: 4 * 1024 * 1024,
      },
    );
    if (stderr.trim()) console.warn(`[XAI:${modelName}] ${stderr.trim().slice(0, 1000)}`);
    return parseJsonLine(stdout) as PythonHeatmapResult;
  }

  async generateEnsembleHeatmap(
    imagePath: string,
    cnnHeatmapPath: string,
    vitHeatmapPath: string,
    hybridHeatmapPath: string,
    outputPath: string,
  ): Promise<PythonHeatmapResult> {
    const weightsPath = process.env.ML_ENSEMBLE_WEIGHTS_PATH || path.join(
      configuredRoot(),
      "ml_artifacts",
      "ham10000",
      "ensemble",
      "weights.json",
    );
    const { stdout, stderr } = await execFileAsync(
      configuredPython(),
      [
        "-m",
        "ml.skin_cancer_ml.ensemble_heatmap",
        "--image",
        path.resolve(imagePath),
        "--cnn",
        path.resolve(cnnHeatmapPath),
        "--vit",
        path.resolve(vitHeatmapPath),
        "--hybrid",
        path.resolve(hybridHeatmapPath),
        "--output",
        path.resolve(outputPath),
        "--weights",
        path.resolve(weightsPath),
      ],
      {
        cwd: configuredRoot(),
        env: { ...process.env, PYTHONPATH: configuredRoot() },
        timeout: this.timeoutMs,
        maxBuffer: 4 * 1024 * 1024,
      },
    );
    if (stderr.trim()) console.warn(`[XAI:ensemble] ${stderr.trim().slice(0, 1000)}`);
    const payload = parseJsonLine(stdout) as { targetClass: string; method: string[]; path: string };
    if (!payload.path) throw new Error("O pipeline Python não retornou o heatmap do ensemble.");
    return {
      targetClass: payload.targetClass,
      method: payload.method,
      paths: { ensemble: payload.path },
    };
  }
}

export const pythonInferenceService = new PythonInferenceService();
