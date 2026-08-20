import fs from "node:fs";
import path from "node:path";
import { upsertModelMetric } from "../server/db";

const root = path.join(process.env.ML_PROJECT_ROOT || process.cwd(), "ml_artifacts", "ham10000");
const version = "ham10000-160px-cpu-epoch2";

interface MetricSource {
  name: string;
  dir: string;
}

const sources: MetricSource[] = [
  { name: "CNN (ResNet-50)", dir: "cnn" },
  { name: "Vision Transformer", dir: "vit" },
  { name: "Hibrido CNN-ViT", dir: "hybrid" },
  { name: "Ensemble Learning", dir: "ensemble" },
];

async function main() {
  console.log(`Persistindo métricas reais para versão: ${version}`);
  
  for (const source of sources) {
    const metricsPath = path.join(root, source.dir, "test_metrics.json");
    if (!fs.existsSync(metricsPath)) {
      console.warn(`Aviso: Métricas não encontradas para ${source.name} em ${metricsPath}`);
      continue;
    }

    const text = fs.readFileSync(metricsPath, "utf8").trim();
    const raw = source.dir === "ensemble"
      ? JSON.parse(text)
      : JSON.parse(text.split(/\r?\n/, 1)[0]);
    // O ensemble tem uma estrutura levemente diferente no JSON gerado pelo script ensemble.py
    const data = source.dir === "ensemble" ? raw.ensemble_test_metrics : raw.metrics;
    
    if (!data || !data.binary || !data.multiclass) {
      console.warn(`Aviso: Formato de métricas inválido para ${source.name}`);
      continue;
    }

    const payload = {
      modelName: source.name,
      modelVersion: version,
      accuracy: Math.round(data.binary.accuracy * 100),
      sensitivity: Math.round(data.binary.sensitivity * 100),
      specificity: Math.round(data.binary.specificity * 100),
      f1Score: Math.round(data.binary.f1 * 100),
      auc: Math.round(data.binary.auroc * 100),
      precision: Math.round(data.binary.precision * 100),
      sampleCount: 1527,
    };

    const saved = await upsertModelMetric(payload);
    if (saved) {
      console.log(`[OK] ${source.name}: ${payload.auc}% AUROC, ${payload.f1Score}% F1 (binário)`);
    } else {
      console.warn(`[SKIP] ${source.name}: Banco de dados não disponível.`);
    }
  }
}

main().catch(console.error);
