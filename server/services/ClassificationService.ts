import { ImageEligibilityResult, pythonInferenceService } from "./PythonInferenceService";
import {
  BaseClassificationModel,
  ClassificationResult,
  CNNModel,
  ViTModel,
  HybridModel,
  EnsembleModel,
  ModelMetrics,
} from "./ClassificationModels";

export interface ComprehensiveClassificationResult {
  eligibility: ImageEligibilityResult;
  cnnResult: ClassificationResult;
  vitResult: ClassificationResult;
  hybridResult: ClassificationResult;
  ensembleResult: ClassificationResult;
  finalClassification: "benign" | "malignant";
  finalConfidence: number;
}

function emptyMetrics(modelName: string, modelVersion: string): ModelMetrics {
  return {
    modelName,
    modelVersion,
    accuracy: 0,
    sensitivity: 0,
    specificity: 0,
    f1Score: 0,
    auc: 0,
    precision: 0,
    sampleCount: 0,
  };
}

export class ClassificationService {
  private cnnModel: CNNModel;
  private vitModel: ViTModel;
  private hybridModel: HybridModel;
  private ensembleModel: EnsembleModel;

  constructor() {
    const version = process.env.ML_MODEL_VERSION || "untrained";
    this.cnnModel = new CNNModel("CNN (ResNet-50)", version, emptyMetrics("CNN (ResNet-50)", version));
    this.vitModel = new ViTModel("Vision Transformer (ViT)", version, emptyMetrics("Vision Transformer (ViT)", version));
    this.hybridModel = new HybridModel(version, emptyMetrics("Hybrid CNN-ViT", version), this.cnnModel, this.vitModel);
    this.ensembleModel = new EnsembleModel(version, emptyMetrics("Ensemble Learning", version), [this.cnnModel, this.vitModel, this.hybridModel]);
  }

  async classifyImage(imagePath: string): Promise<ComprehensiveClassificationResult> {
    try {
      const eligibility = await pythonInferenceService.validateImage(imagePath);
      if (!eligibility.accepted) {
        const error = new Error(`Imagem não elegível: ${eligibility.reasons.join(", ")}`) as Error & { code: string; eligibility: ImageEligibilityResult };
        error.code = "IMAGE_NOT_ELIGIBLE";
        error.eligibility = eligibility;
        throw error;
      }
      const [cnnResult, vitResult, hybridResult] = await Promise.all([
        this.cnnModel.classify(imagePath),
        this.vitModel.classify(imagePath),
        this.hybridModel.classify(imagePath),
      ]);
      const ensembleResult = this.ensembleModel.combineResults([cnnResult, vitResult, hybridResult]);
      return {
        eligibility,
        cnnResult,
        vitResult,
        hybridResult,
        ensembleResult,
        finalClassification: ensembleResult.classification,
        finalConfidence: ensembleResult.confidence,
      };
    } catch (error) {
      console.error("Erro ao classificar imagem:", error);
      const candidate = error as Error & { code?: string; eligibility?: ImageEligibilityResult };
      if (candidate.code === "IMAGE_NOT_ELIGIBLE") throw error;
      throw new Error(`Falha na classificação: ${error instanceof Error ? error.message : "Erro desconhecido"}`);
    }
  }

  async generateAllHeatmaps(imagePath: string, outputDir: string): Promise<{
    cnnHeatmapPath: string;
    vitHeatmapPath: string;
    hybridHeatmapPath: string;
    ensembleHeatmapPath: string;
  }> {
    try {
      const [cnn, vit, hybrid] = await Promise.all([
        pythonInferenceService.explain(this.cnnModel.getCheckpointPath(), "cnn", imagePath, `${outputDir}/cnn.png`),
        pythonInferenceService.explain(this.vitModel.getCheckpointPath(), "vit", imagePath, `${outputDir}/vit.png`),
        pythonInferenceService.explain(this.hybridModel.getCheckpointPath(), "hybrid", imagePath, `${outputDir}/hybrid.png`),
      ]);
      const componentPaths = {
        cnnHeatmapPath: cnn.paths.gradcam,
        vitHeatmapPath: vit.paths.token_gradient,
        hybridHeatmapPath: hybrid.paths.hybrid,
      };
      if (!componentPaths.cnnHeatmapPath || !componentPaths.vitHeatmapPath || !componentPaths.hybridHeatmapPath) {
        throw new Error("Um ou mais heatmaps componentes não foram gerados.");
      }
      const ensemble = await pythonInferenceService.generateEnsembleHeatmap(
        imagePath,
        componentPaths.cnnHeatmapPath,
        componentPaths.vitHeatmapPath,
        componentPaths.hybridHeatmapPath,
        `${outputDir}/ensemble.png`,
      );
      const paths = {
        ...componentPaths,
        ensembleHeatmapPath: ensemble.paths.ensemble,
      };
      if (!paths.ensembleHeatmapPath) {
        throw new Error("O heatmap do Ensemble Learning não foi gerado.");
      }
      return paths;
    } catch (error) {
      console.error("Erro ao gerar heatmaps:", error);
      throw new Error(`Falha ao gerar heatmaps: ${error instanceof Error ? error.message : "Erro desconhecido"}`);
    }
  }

  public getAllModelMetrics(): ModelMetrics[] {
    return [this.cnnModel.getMetrics(), this.vitModel.getMetrics(), this.hybridModel.getMetrics(), this.ensembleModel.getMetrics()];
  }

  public getModelMetrics(modelName: string): ModelMetrics | null {
    const model = this.getModelByName(modelName);
    return model?.getMetrics() || null;
  }

  public updateModelMetrics(modelName: string, metrics: ModelMetrics): boolean {
    const model = this.getModelByName(modelName);
    if (!model) return false;
    model.setMetrics(metrics);
    return true;
  }

  private getModelByName(modelName: string): BaseClassificationModel | null {
    switch (modelName.toLowerCase()) {
      case "cnn": return this.cnnModel;
      case "vit": return this.vitModel;
      case "hybrid": return this.hybridModel;
      case "ensemble": return this.ensembleModel;
      default: return null;
    }
  }

  public getCNNModel(): CNNModel { return this.cnnModel; }
  public getViTModel(): ViTModel { return this.vitModel; }
  public getHybridModel(): HybridModel { return this.hybridModel; }
  public getEnsembleModel(): EnsembleModel { return this.ensembleModel; }
}

export const classificationService = new ClassificationService();
