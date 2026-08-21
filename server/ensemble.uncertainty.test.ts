import { afterEach, describe, expect, it } from "vitest";
import { EnsembleModel, type ClassificationResult, type ModelMetrics } from "./services/ClassificationModels";

const metrics: ModelMetrics = {
  modelName: "test",
  modelVersion: "test",
  accuracy: 0,
  sensitivity: 0,
  specificity: 0,
  f1Score: 0,
  auc: 0,
  precision: 0,
  sampleCount: 0,
};

function prediction(
  predictiveEntropy: number,
  ttaVariance: number,
  abstain: boolean,
): ClassificationResult {
  return {
    classification: "benign",
    confidence: 90,
    probabilities: { benign: 0.9, malignant: 0.1 },
    inferenceTime: 1,
    uncertainty: { predictiveEntropy, ttaVariance, abstain },
  };
}

describe("EnsembleModel uncertainty policy", () => {
  const original = {
    votes: process.env.ML_ENSEMBLE_ABSTAIN_VOTES,
    entropy: process.env.ML_ENSEMBLE_ENTROPY_THRESHOLD,
    variance: process.env.ML_ENSEMBLE_TTA_VARIANCE_THRESHOLD,
  };

  afterEach(() => {
    if (original.votes === undefined) delete process.env.ML_ENSEMBLE_ABSTAIN_VOTES;
    else process.env.ML_ENSEMBLE_ABSTAIN_VOTES = original.votes;
    if (original.entropy === undefined) delete process.env.ML_ENSEMBLE_ENTROPY_THRESHOLD;
    else process.env.ML_ENSEMBLE_ENTROPY_THRESHOLD = original.entropy;
    if (original.variance === undefined) delete process.env.ML_ENSEMBLE_TTA_VARIANCE_THRESHOLD;
    else process.env.ML_ENSEMBLE_TTA_VARIANCE_THRESHOLD = original.variance;
  });

  it("does not abstain because of one model vote when quorum is two", () => {
    process.env.ML_ENSEMBLE_ABSTAIN_VOTES = "2";
    process.env.ML_ENSEMBLE_ENTROPY_THRESHOLD = "0.75";
    process.env.ML_ENSEMBLE_TTA_VARIANCE_THRESHOLD = "0.03";
    const ensemble = new EnsembleModel("test", metrics, []);

    const result = ensemble.combineResults([
      prediction(0.70, 0.003, true),
      prediction(0.46, 0.001, false),
      prediction(0.49, 0.000, false),
    ]);

    expect(result.uncertainty?.abstain).toBe(false);
  });

  it("still abstains when two models vote for abstention", () => {
    process.env.ML_ENSEMBLE_ABSTAIN_VOTES = "2";
    process.env.ML_ENSEMBLE_ENTROPY_THRESHOLD = "0.75";
    process.env.ML_ENSEMBLE_TTA_VARIANCE_THRESHOLD = "0.03";
    const ensemble = new EnsembleModel("test", metrics, []);

    const result = ensemble.combineResults([
      prediction(0.70, 0.003, true),
      prediction(0.71, 0.004, true),
      prediction(0.49, 0.000, false),
    ]);

    expect(result.uncertainty?.abstain).toBe(true);
  });

  it("still abstains when ensemble average entropy exceeds its threshold", () => {
    process.env.ML_ENSEMBLE_ABSTAIN_VOTES = "3";
    process.env.ML_ENSEMBLE_ENTROPY_THRESHOLD = "0.60";
    process.env.ML_ENSEMBLE_TTA_VARIANCE_THRESHOLD = "0.03";
    const ensemble = new EnsembleModel("test", metrics, []);

    const result = ensemble.combineResults([
      prediction(0.70, 0.003, false),
      prediction(0.68, 0.004, false),
      prediction(0.66, 0.005, false),
    ]);

    expect(result.uncertainty?.abstain).toBe(true);
  });
});
