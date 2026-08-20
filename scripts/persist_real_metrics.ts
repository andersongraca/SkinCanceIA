import fs from "node:fs/promises";
import path from "node:path";
import { upsertModelMetric } from "../server/db";

type BinaryMetrics = {
  accuracy: number;
  sensitivity: number;
  specificity: number;
  precision: number;
  f1: number;
  auroc: number;
};

type MetricsPayload = {
  test_sample_count: number;
  component_test_metrics: Record<string, { binary?: BinaryMetrics }>;
  ensemble_test_metrics?: { binary?: BinaryMetrics };
};

const projectRoot = process.env.ML_PROJECT_ROOT || process.cwd();
const metricsPath = path.join(
  projectRoot,
  "ml_artifacts",
  "ham10000",
  "ensemble",
  "test_metrics.json",
);
const modelVersion = process.env.ML_MODEL_VERSION || "ham10000-160px-epoch2";

function percent(value: number | undefined): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error("Métrica ausente ou inválida no test_metrics.json");
  }
  return Math.round(value * 100);
}

function toDatabaseMetric(modelName: string, binary: BinaryMetrics, sampleCount: number) {
  return {
    modelName,
    modelVersion,
    accuracy: percent(binary.accuracy),
    sensitivity: percent(binary.sensitivity),
    specificity: percent(binary.specificity),
    f1Score: percent(binary.f1),
    auc: percent(binary.auroc),
    precision: percent(binary.precision),
    sampleCount,
  };
}

async function main() {
  const payload = JSON.parse(await fs.readFile(metricsPath, "utf8")) as MetricsPayload;
  const sampleCount = payload.test_sample_count;
  if (!Number.isInteger(sampleCount) || sampleCount <= 0) {
    throw new Error("test_sample_count inválido no test_metrics.json");
  }

  const modelSpecs = [
    ["CNN (ResNet-50)", "cnn"],
    ["Vision Transformer", "vit"],
    ["Hibrido CNN-ViT", "hybrid"],
  ] as const;

  const metrics = modelSpecs.map(([modelName, key]) => {
    const binary = payload.component_test_metrics[key]?.binary;
    if (!binary) throw new Error(`Métricas binárias ausentes para ${key}`);
    return toDatabaseMetric(modelName, binary, sampleCount);
  });

  const ensembleBinary = payload.ensemble_test_metrics?.binary;
  if (!ensembleBinary) throw new Error("Métricas binárias ausentes para ensemble");
  metrics.push(toDatabaseMetric("Ensemble Learning", ensembleBinary, sampleCount));

  for (const metric of metrics) {
    const saved = await upsertModelMetric(metric);
    if (!saved) throw new Error("Banco de dados indisponível para persistir as métricas.");
    console.log(
      `${metric.modelName}: AUROC=${metric.auc}% | sensibilidade=${metric.sensitivity}% | especificidade=${metric.specificity}% | F1=${metric.f1Score}% | n=${metric.sampleCount}`,
    );
  }
}

main()
  .then(() => process.exit(0))
  .catch(error => {
    console.error("Falha ao persistir métricas reais:", error);
    process.exit(1);
  });
