import fs from "node:fs/promises";
import path from "node:path";
import { classificationService } from "../server/services/ClassificationService";

const imagePath = path.resolve(process.argv[2] || "");
const outputDirectory = path.resolve(process.argv[3] || "runtime/presentation-audit");
if (!imagePath) throw new Error("Informe a imagem de auditoria.");

await fs.rm(outputDirectory, { recursive: true, force: true });
await fs.mkdir(outputDirectory, { recursive: true });

const startedAt = Date.now();
const result = await classificationService.classifyImage(imagePath);
const classifiedAt = Date.now();
const heatmaps = await classificationService.generateAllHeatmaps(imagePath, outputDirectory);
const completedAt = Date.now();

const required = Object.entries(heatmaps);
const files = await Promise.all(required.map(async ([name, filePath]) => {
  const stat = await fs.stat(filePath);
  return { name, filePath, bytes: stat.size };
}));

const payload = {
  imagePath,
  eligibility: result.eligibility,
  finalClassification: result.finalClassification,
  finalConfidence: result.finalConfidence,
  uncertainty: result.ensembleResult.uncertainty,
  componentModels: {
    cnn: result.cnnResult,
    vit: result.vitResult,
    hybrid: result.hybridResult,
    ensemble: result.ensembleResult,
  },
  heatmaps,
  files,
  timingMs: {
    classification: classifiedAt - startedAt,
    heatmaps: completedAt - classifiedAt,
    total: completedAt - startedAt,
  },
};

await fs.writeFile(path.join(outputDirectory, "audit-result.json"), JSON.stringify(payload, null, 2));
console.log(JSON.stringify(payload, null, 2));
