import { desc, eq } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { InsertUser, users, dermatologicalImages, diagnoses, modelMetrics, DermatologicalImage, Diagnosis, ModelMetric, InsertDermatologicalImage, InsertDiagnosis, InsertModelMetric } from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

/**
 * Obtém a instância do banco de dados Drizzle.
 * Cria a conexão de forma preguiçosa para permitir que ferramentas locais
 * funcionem sem um banco de dados disponível.
 */
export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Falha ao conectar:", error);
      _db = null;
    }
  }
  return _db;
}

/**
 * Insere ou atualiza um usuário no banco de dados.
 * Utiliza a estratégia onDuplicateKeyUpdate para evitar conflitos de chave única.
 */
export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId é obrigatório para upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Não é possível fazer upsert do usuário: banco de dados não disponível");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = 'admin';
      updateSet.role = 'admin';
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Falha ao fazer upsert do usuário:", error);
    throw error;
  }
}

/**
 * Obtém um usuário pelo seu openId.
 */
export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Não é possível obter usuário: banco de dados não disponível");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);

  return result.length > 0 ? result[0] : undefined;
}

/**
 * Insere uma nova imagem dermatoscópica no banco de dados.
 */
export async function insertDermatologicalImage(image: InsertDermatologicalImage): Promise<DermatologicalImage | null> {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Não é possível inserir imagem: banco de dados não disponível");
    return null;
  }

  try {
    const result = await db.insert(dermatologicalImages).values(image);
    const insertedImage = await db.select().from(dermatologicalImages).where(eq(dermatologicalImages.id, Number(result[0].insertId))).limit(1);
    return insertedImage.length > 0 ? insertedImage[0] : null;
  } catch (error) {
    console.error("[Database] Falha ao inserir imagem:", error);
    throw error;
  }
}

/**
 * Obtém todas as imagens de um usuário específico.
 */
export async function getUserImages(userId: number): Promise<DermatologicalImage[]> {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Não é possível obter imagens: banco de dados não disponível");
    return [];
  }

  try {
    return await db.select().from(dermatologicalImages).where(eq(dermatologicalImages.userId, userId));
  } catch (error) {
    console.error("[Database] Falha ao obter imagens do usuário:", error);
    throw error;
  }
}

/**
 * Obtém uma imagem específica pelo seu ID.
 */
export async function getImageById(imageId: number): Promise<DermatologicalImage | null> {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Não é possível obter imagem: banco de dados não disponível");
    return null;
  }

  try {
    const result = await db.select().from(dermatologicalImages).where(eq(dermatologicalImages.id, imageId)).limit(1);
    return result.length > 0 ? result[0] : null;
  } catch (error) {
    console.error("[Database] Falha ao obter imagem:", error);
    throw error;
  }
}

/**
 * Insere um novo diagnóstico no banco de dados.
 */
export async function insertDiagnosis(diagnosis: InsertDiagnosis): Promise<Diagnosis | null> {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Não é possível inserir diagnóstico: banco de dados não disponível");
    return null;
  }

  try {
    const result = await db.insert(diagnoses).values(diagnosis);
    const insertedDiagnosis = await db.select().from(diagnoses).where(eq(diagnoses.id, Number(result[0].insertId))).limit(1);
    return insertedDiagnosis.length > 0 ? insertedDiagnosis[0] : null;
  } catch (error) {
    console.error("[Database] Falha ao inserir diagnóstico:", error);
    throw error;
  }
}

/**
 * Obtém todos os diagnósticos de um usuário específico.
 */
export async function getUserDiagnoses(userId: number): Promise<Diagnosis[]> {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Não é possível obter diagnósticos: banco de dados não disponível");
    return [];
  }

  try {
    return await db.select().from(diagnoses).where(eq(diagnoses.userId, userId));
  } catch (error) {
    console.error("[Database] Falha ao obter diagnósticos do usuário:", error);
    throw error;
  }
}

/**
 * Obtém um diagnóstico específico pelo seu ID.
 */
export async function getUserDiagnosisHistory(userId: number) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Não é possível obter histórico: banco de dados não disponível");
    return [];
  }

  const rows = await db
    .select()
    .from(diagnoses)
    .innerJoin(dermatologicalImages, eq(diagnoses.imageId, dermatologicalImages.id))
    .where(eq(diagnoses.userId, userId))
    .orderBy(desc(diagnoses.diagnosedAt));

  return rows.map(row => ({
    ...row.diagnoses,
    imageFileName: row.dermatological_images.fileName,
    imagePath: row.dermatological_images.imagePath,
  }));
}

export async function getDiagnosisById(diagnosisId: number): Promise<Diagnosis | null> {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Não é possível obter diagnóstico: banco de dados não disponível");
    return null;
  }

  try {
    const result = await db.select().from(diagnoses).where(eq(diagnoses.id, diagnosisId)).limit(1);
    return result.length > 0 ? result[0] : null;
  } catch (error) {
    console.error("[Database] Falha ao obter diagnóstico:", error);
    throw error;
  }
}

/**
 * Obtém todos os diagnósticos associados a uma imagem específica.
 */
export async function getImageDiagnoses(imageId: number): Promise<Diagnosis[]> {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Não é possível obter diagnósticos: banco de dados não disponível");
    return [];
  }

  try {
    return await db.select().from(diagnoses).where(eq(diagnoses.imageId, imageId));
  } catch (error) {
    console.error("[Database] Falha ao obter diagnósticos da imagem:", error);
    throw error;
  }
}

/**
 * Insere ou atualiza as métricas de desempenho de um modelo.
 */
export async function upsertModelMetric(metric: InsertModelMetric): Promise<ModelMetric | null> {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Não é possível inserir métrica: banco de dados não disponível");
    return null;
  }

  try {
    const result = await db.insert(modelMetrics).values(metric).onDuplicateKeyUpdate({
      set: {
        accuracy: metric.accuracy,
        sensitivity: metric.sensitivity,
        specificity: metric.specificity,
        f1Score: metric.f1Score,
        auc: metric.auc,
        precision: metric.precision,
        sampleCount: metric.sampleCount,
        updatedAt: new Date(),
      },
    });

    const insertedMetric = await db.select().from(modelMetrics).where(eq(modelMetrics.id, Number(result[0].insertId))).limit(1);
    return insertedMetric.length > 0 ? insertedMetric[0] : null;
  } catch (error) {
    console.error("[Database] Falha ao inserir métrica:", error);
    throw error;
  }
}

/**
 * Obtém as métricas de um modelo específico.
 */
export async function getModelMetrics(modelName: string): Promise<ModelMetric | null> {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Não é possível obter métricas: banco de dados não disponível");
    return null;
  }

  try {
    const result = await db.select().from(modelMetrics).where(eq(modelMetrics.modelName, modelName)).limit(1);
    return result.length > 0 ? result[0] : null;
  } catch (error) {
    console.error("[Database] Falha ao obter métricas:", error);
    throw error;
  }
}

/**
 * Obtém todas as métricas de todos os modelos.
 */
export async function getAllModelMetrics(): Promise<ModelMetric[]> {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Não é possível obter métricas: banco de dados não disponível");
    return [];
  }

  try {
    return await db.select().from(modelMetrics);
  } catch (error) {
    console.error("[Database] Falha ao obter todas as métricas:", error);
    throw error;
  }
}
