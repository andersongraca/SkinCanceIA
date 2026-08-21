export interface ImageEligibility {
  accepted: boolean;
  status: 'accepted' | 'rejected';
  reasons: string[];
  warnings: string[];
  width?: number;
  height?: number;
  quality_score?: number;
  ood_score?: number | null;
  ood_threshold?: number | null;
}

export interface ModelPrediction {
  classification: 'benign' | 'malignant';
  confidence: number;
  inferenceTime: number;
  fineGrainedClass?: string;
  uncertainty?: {
    predictiveEntropy: number;
    ttaVariance: number;
    abstain: boolean;
  };
}

export interface ClassificationResponse {
  status: 'classified' | 'rejected';
  imageId: number;
  eligibility?: ImageEligibility;
  result?: {
    eligibility: ImageEligibility;
    finalClassification: 'benign' | 'malignant';
    finalConfidence: number;
    cnnResult: ModelPrediction;
    vitResult: ModelPrediction;
    hybridResult: ModelPrediction;
    ensembleResult: ModelPrediction;
    heatmaps?: {
      cnnHeatmapPath: string;
      vitHeatmapPath: string;
      hybridHeatmapPath: string;
      ensembleHeatmapPath?: string;
    };
  };
  diagnosis?: { id: number } | null;
}
