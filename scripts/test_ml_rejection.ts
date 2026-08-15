import path from "node:path";
import { classificationService } from "../server/services/ClassificationService";

const imagePath = process.argv[2];
if (!imagePath) throw new Error("Informe o caminho da imagem de teste.");

try {
  await classificationService.classifyImage(path.resolve(imagePath));
  console.error(JSON.stringify({ acceptedUnexpectedly: true, image: path.resolve(imagePath) }));
  process.exitCode = 1;
} catch (error) {
  const candidate = error as Error & { code?: string; eligibility?: unknown };
  if (candidate.code !== "IMAGE_NOT_ELIGIBLE") {
    throw error;
  }
  console.log(JSON.stringify({
    acceptedUnexpectedly: false,
    image: path.resolve(imagePath),
    code: candidate.code,
    eligibility: candidate.eligibility,
  }, null, 2));
}
