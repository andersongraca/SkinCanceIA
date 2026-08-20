import fs from "node:fs";
import path from "node:path";
import { pythonInferenceService } from "./PythonInferenceService";

export interface ClassificationResult {
  classification: "benign" | "malignant";
  confidence: number;
  probabilities: { benign: number; malignant: number };
  inferenceTime: number;
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

export interface ModelMetrics {
  modelName: string;
  modelVersion: string;
  accuracy: number;
  sensitivity: number;
  specificity: number;
  f1Score: number;
  auc: number;
  precision: number;
  sampleCount: number;
}

export abstract class BaseClassificationModel {
  protected modelName: string;
  protected modelVersion: string;
  protected metrics: ModelMetrics;

  constructor(modelName: string, modelVersion: string, metrics: ModelMetrics) {
    this.modelName = modelName;
    this.modelVersion = modelVersion;
    this.metrics = metrics;
  }

  abstract classify(imagePath: string): Promise<ClassificationResult>;
  abstract generateHeatmap(imagePath: string, outputPath: string): Promise<boolean>;

  public getModelName(): string {
    return this.modelName;
  }

  public getModelVersion(): string {
    return this.modelVersion;
  }

  public getMetrics(): ModelMetrics {
    return this.metrics;
  }

  public setMetrics(metrics: ModelMetrics): void {
    this.metrics = metrics;
  }
}

function mapPythonResult(result: Awaited<ReturnType<typeof pythonInferenceService.classify>>, inferenceTime: number): ClassificationResult {
  return {
    classification: result.classification,
    confidence: result.confidence,
    probabilities: result.probabilities,
    inferenceTime,
    fineGrainedClass: result.fineGrainedClass,
    fineGrainedProbabilities: result.fineGrainedProbabilities,
    uncertainty: result.uncertainty,
    ttaSamples: result.ttaSamples,
    modelVersion: result.modelVersion,
  };
}

abstract class PythonBackedModel extends BaseClassificationModel {
  protected readonly checkpointPath: string | undefined;
  protected readonly modelKey: "cnn" | "vit" | "hybrid";

  constructor(
    modelName: string,
    modelVersion: string,
    metrics: ModelMetrics,
    modelKey: "cnn" | "vit" | "hybrid",
    checkpointPath?: string,
  ) {
    super(modelName, modelVersion, metrics);
    this.modelKey = modelKey;
    this.checkpointPath = checkpointPath
      || process.env[`ML_${modelKey.toUpperCase()}_CHECKPOINT`]
      || path.join(process.env.ML_PROJECT_ROOT || process.cwd(), "ml_artifacts", "ham10000", modelKey, "best.pt");
  }

  public getCheckpointPath(): string | undefined {
    return this.checkpointPath;
  }

  async classify(imagePath: string): Promise<ClassificationResult> {
    const startTime = Date.now();
    const result = await pythonInferenceService.classify(this.checkpointPath, this.modelKey, imagePath);
    return mapPythonResult(result, Date.now() - startTime);
  }

  async generateHeatmap(imagePath: string, outputPath: string): Promise<boolean> {
    const result = await pythonInferenceService.explain(this.checkpointPath, this.modelKey, imagePath, outputPath);
    return Object.values(result.paths).some(path => fs.existsSync(path));
  }
}

export class CNNModel extends PythonBackedModel {
  constructor(modelName: string, modelVersion: string, metrics: ModelMetrics, checkpointPath?: string) {
    super(modelName, modelVersion, metrics, "cnn", checkpointPath);
  }
}

export class ViTModel extends PythonBackedModel {
  constructor(modelName: string, modelVersion: string, metrics: ModelMetrics, checkpointPath?: string) {
    super(modelName, modelVersion, metrics, "vit", checkpointPath);
  }
}

export class HybridModel extends PythonBackedModel {
  constructor(
    modelVersion: string,
    metrics: ModelMetrics,
    _cnnModel?: CNNModel,
    _vitModel?: ViTModel,
    checkpointPath?: string,
  ) {
    super("Hybrid CNN-ViT", modelVersion, metrics, "hybrid", checkpointPath);
  }

  public getCNNModel(): CNNModel | undefined {
    return undefined;
  }

  public getViTModel(): ViTModel | undefined {
    return undefined;
  }
}

export class EnsembleModel extends BaseClassificationModel {
  private models: BaseClassificationModel[];
  private weights: number[];

  constructor(modelVersion: string, metrics: ModelMetrics, models: BaseClassificationModel[]) {
    super("Ensemble Learning", modelVersion, metrics);
    this.models = models;
    this.weights = this.loadWeights(models.length);
  }

  private loadWeights(count: number): number[] {
    const fallback = Array.from({ length: count }, () => 1 / Math.max(count, 1));
    const configuredPath = process.env.ML_ENSEMBLE_WEIGHTS_PATH || path.join(process.env.ML_PROJECT_ROOT || process.cwd(), "ml_artifacts", "ham10000", "ensemble", "weights.json");
    try {
      const raw = process.env.ML_ENSEMBLE_WEIGHTS || (fs.existsSync(configuredPath) ? fs.readFileSync(configuredPath, "utf8") : "");
      if (!raw) return fallback;
      const parsed = JSON.parse(raw) as Record<string, number>;
      const keys = ["cnn", "vit", "hybrid"];
      const values = keys.slice(0, count).map(key => Number(parsed[key]));
      if (values.some(value => !Number.isFinite(value) || value < 0)) return fallback;
      const total = values.reduce((sum, value) => sum + value, 0);
      return total > 0 ? values.map(value => value / total) : fallback;
    } catch {
      return fallback;
    }
  }

  public combineResults(results: ClassificationResult[]): ClassificationResult {
    if (!results.length) throw new Error("Não é possível combinar zero resultados.");
    const weights = this.weights.length === results.length ? this.weights : Array.from({ length: results.length }, () => 1 / results.length);
    const malignantProbability = results.reduce((sum, result, index) => sum + weights[index] * result.probabilities.malignant, 0);
    const classification = malignantProbability >= 0.5 ? "malignant" : "benign";
    const confidence = (classification === "malignant" ? malignantProbability : 1 - malignantProbability) * 100;
    const fineGrainedProbabilities: Record<string, number> = {};
    for (const [index, result] of results.entries()) {
      for (const [label, probability] of Object.entries(result.fineGrainedProbabilities || {})) {
        fineGrainedProbabilities[label] = (fineGrainedProbabilities[label] || 0) + weights[index] * probability;
      }
    }
    return {
      classification,
      confidence,
      probabilities: { benign: 1 - malignantProbability, malignant: malignantProbability },
      inferenceTime: results.reduce((max, result) => Math.max(max, result.inferenceTime), 0),
      fineGrainedClass: Object.entries(fineGrainedProbabilities).sort((a, b) => b[1] - a[1])[0]?.[0],
      fineGrainedProbabilities: Object.keys(fineGrainedProbabilities).length ? fineGrainedProbabilities : undefined,
      uncertainty: {
        predictiveEntropy: results.reduce((sum, result) => sum + (result.uncertainty?.predictiveEntropy || 0), 0) / results.length,
        ttaVariance: results.reduce((sum, result) => sum + (result.uncertainty?.ttaVariance || 0), 0) / results.length,
        abstain: results.some(result => result.uncertainty?.abstain),
      },
      modelVersion: this.modelVersion,
    };
  }

  async classify(imagePath: string): Promise<ClassificationResult> {
    const startTime = Date.now();
    const results = await Promise.all(this.models.map(model => model.classify(imagePath)));
    return { ...this.combineResults(results), inferenceTime: Date.now() - startTime };
  }

  async generateHeatmap(imagePath: string, outputPath: string): Promise<boolean> {
    const results = await Promise.all(this.models.map(model => model.generateHeatmap(imagePath, outputPath)));
    return results.every(Boolean);
  }

  public getModels(): BaseClassificationModel[] {
    return this.models;
  }
}
