import { int, index, mysqlEnum, mysqlTable, text, timestamp, uniqueIndex, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  id: int("id").autoincrement().primaryKey(),
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

export const dermatologicalImages = mysqlTable("dermatological_images", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("user_id").notNull().references(() => users.id, { onDelete: "cascade" }),
  fileName: varchar("file_name", { length: 255 }).notNull(),
  imagePath: text("image_path").notNull(),
  thumbnailPath: text("thumbnail_path"),
  fileSize: int("file_size").notNull(),
  mimeType: varchar("mime_type", { length: 50 }).notNull(),
  description: text("description"),
  uploadedAt: timestamp("uploaded_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
}, (table) => ({
  userIdx: index("dermatological_images_user_idx").on(table.userId),
}));

export type DermatologicalImage = typeof dermatologicalImages.$inferSelect;
export type InsertDermatologicalImage = typeof dermatologicalImages.$inferInsert;

export const diagnoses = mysqlTable("diagnoses", {
  id: int("id").autoincrement().primaryKey(),
  imageId: int("image_id").notNull().references(() => dermatologicalImages.id, { onDelete: "cascade" }),
  userId: int("user_id").notNull().references(() => users.id, { onDelete: "cascade" }),
  classification: varchar("classification", { length: 50 }).notNull(),
  confidence: int("confidence").notNull(),
  cnnResult: varchar("cnn_result", { length: 50 }),
  cnnConfidence: int("cnn_confidence"),
  vitResult: varchar("vit_result", { length: 50 }),
  vitConfidence: int("vit_confidence"),
  hybridResult: varchar("hybrid_result", { length: 50 }),
  hybridConfidence: int("hybrid_confidence"),
  heatmapPath: text("heatmap_path"),
  modelVersion: varchar("model_version", { length: 50 }),
  diagnosedAt: timestamp("diagnosed_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
}, (table) => ({
  userIdx: index("diagnoses_user_idx").on(table.userId),
  imageIdx: index("diagnoses_image_idx").on(table.imageId),
  diagnosedAtIdx: index("diagnoses_diagnosed_at_idx").on(table.diagnosedAt),
}));

export type Diagnosis = typeof diagnoses.$inferSelect;
export type InsertDiagnosis = typeof diagnoses.$inferInsert;

export const modelMetrics = mysqlTable("model_metrics", {
  id: int("id").autoincrement().primaryKey(),
  modelName: varchar("model_name", { length: 100 }).notNull(),
  modelVersion: varchar("model_version", { length: 50 }).notNull(),
  accuracy: int("accuracy").notNull(),
  sensitivity: int("sensitivity").notNull(),
  specificity: int("specificity").notNull(),
  f1Score: int("f1_score").notNull(),
  auc: int("auc").notNull(),
  precision: int("precision").notNull(),
  sampleCount: int("sample_count").notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
}, (table) => ({
  modelVersionUnique: uniqueIndex("model_metrics_model_version_unique").on(table.modelName, table.modelVersion),
}));

export type ModelMetric = typeof modelMetrics.$inferSelect;
export type InsertModelMetric = typeof modelMetrics.$inferInsert;
