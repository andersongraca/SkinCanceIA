import path from "node:path";
import { classificationService } from "../server/services/ClassificationService";

const imagePath = process.argv[2];
if (!imagePath) throw new Error("Informe o caminho da imagem de teste.");

const absoluteImage = path.resolve(imagePath);
const result = await classificationService.classifyImage(absoluteImage);
const outputDirectory = path.join(path.dirname(absoluteImage), "typescript_service_heatmaps");
const heatmaps = await classificationService.generateAllHeatmaps(absoluteImage, outputDirectory);

console.log(JSON.stringify({
  eligibility: result.eligibility,
  finalClassification: result.finalClassification,
  finalConfidence: result.finalConfidence,
  uncertainty: result.ensembleResult.uncertainty,
  componentModels: {
    cnn: result.cnnResult.classification,
    vit: result.vitResult.classification,
    hybrid: result.hybridResult.classification,
  },
  heatmaps,
}, null, 2));
