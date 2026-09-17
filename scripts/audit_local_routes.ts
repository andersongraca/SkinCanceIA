import fs from "node:fs/promises";
import path from "node:path";
import { appRouter } from "../server/routers";

const imagePath = path.resolve(process.argv[2] || "");
if (!imagePath) throw new Error("Informe a imagem de auditoria.");
const bytes = await fs.readFile(imagePath);
const caller = appRouter.createCaller({ req: {} as any, res: {} as any, user: null });

const uploaded = await caller.diagnosis.uploadImage({
  fileName: path.basename(imagePath),
  mimeType: "image/jpeg",
  dataUrl: `data:image/jpeg;base64,${bytes.toString("base64")}`,
});
const classified = await caller.diagnosis.classifyStoredImage({ imageId: uploaded.imageId });
if (classified.status !== "classified" || !classified.result.heatmaps) {
  throw new Error("A rota local não retornou classificação com heatmaps.");
}
const heatmapUrls = Object.values(classified.result.heatmaps);
if (heatmapUrls.length !== 4 || heatmapUrls.some(url => !url.startsWith("/api/ml-artifacts/"))) {
  throw new Error(`URLs de heatmap inválidas: ${JSON.stringify(heatmapUrls)}`);
}
const history = await caller.diagnosis.getHistory();
if (history.length !== 1) throw new Error(`Histórico local esperado=1 recebido=${history.length}`);
const details = await caller.diagnosis.getById({ id: history[0].id });
const metrics = await caller.metrics.getAllMetrics();
if (metrics.length !== 4 || metrics.some(metric => metric.sampleCount !== 1527)) {
  throw new Error("Métricas locais reais não foram carregadas corretamente.");
}
console.log(JSON.stringify({
  upload: uploaded,
  classificationStatus: classified.status,
  finalClassification: classified.result.finalClassification,
  finalConfidence: classified.result.finalConfidence,
  heatmapUrls,
  historyCount: history.length,
  detailId: details.id,
  metricModels: metrics.map(metric => metric.modelName),
  metricSamples: metrics.map(metric => metric.sampleCount),
}, null, 2));
