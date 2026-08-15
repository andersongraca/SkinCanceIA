import { upsertModelMetric } from "../server/db";

const modelVersion = process.env.ML_MODEL_VERSION || "ham10000-test-2026-08-15";
const sampleCount = 1527;

const metrics = [
  {
    modelName: "CNN (ResNet-50)",
    accuracy: 75,
    sensitivity: 79,
    specificity: 74,
    f1Score: 56,
    auc: 85,
    precision: 43,
  },
  {
    modelName: "Vision Transformer",
    accuracy: 76,
    sensitivity: 77,
    specificity: 76,
    f1Score: 56,
    auc: 85,
    precision: 44,
  },
  {
    modelName: "Hibrido CNN-ViT",
    accuracy: 73,
    sensitivity: 80,
    specificity: 71,
    f1Score: 54,
    auc: 84,
    precision: 40,
  },
  {
    modelName: "Ensemble Learning",
    accuracy: 75,
    sensitivity: 80,
    specificity: 74,
    f1Score: 56,
    auc: 86,
    precision: 43,
  },
] as const;

async function main() {
  for (const metric of metrics) {
    const saved = await upsertModelMetric({
      ...metric,
      modelVersion,
      sampleCount,
    });
    if (!saved) {
      throw new Error("Banco de dados indisponível para atualizar as métricas.");
    }
    console.log(`${metric.modelName}: ${metric.auc}% AUROC, ${metric.f1Score}% F1, n=${sampleCount}`);
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
