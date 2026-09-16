import "dotenv/config";
import mysql from "mysql2/promise";

async function main() {
  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    console.log(JSON.stringify({ databaseConfigured: false }));
    return;
  }
  const connection = await mysql.createConnection(databaseUrl);
  try {
    const [counts] = await connection.query<mysql.RowDataPacket[]>(
      "SELECT TABLE_NAME AS tableName, TABLE_ROWS AS approximateRows FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN ('analysis_runs','dermatological_images','diagnoses') ORDER BY TABLE_NAME",
    );
    const [runs] = await connection.query<mysql.RowDataPacket[]>(
      "SELECT run_id AS runId, image_id AS imageId, status, abstained, ood_score AS oodScore, quality_score AS qualityScore, predictive_entropy AS predictiveEntropy, tta_variance AS ttaVariance, model_hashes IS NOT NULL AS hasModelHashes, eligibility_features IS NOT NULL AS hasEligibilityFeatures, thresholds IS NOT NULL AS hasThresholds, model_results IS NOT NULL AS hasModelResults, heatmap_paths IS NOT NULL AS hasHeatmapPaths FROM analysis_runs ORDER BY started_at DESC LIMIT 10",
    );
    console.log(JSON.stringify({ databaseConfigured: true, counts, latestRuns: runs }, null, 2));
  } finally {
    await connection.end();
  }
}

main().catch((error) => {
  console.error("database-inspection-failed", error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
