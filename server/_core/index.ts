import "dotenv/config";
import express, { type NextFunction, type Request, type Response } from "express";
import path from "node:path";
import fs from "node:fs/promises";
import { createServer } from "http";
import net from "net";
import { sql } from "drizzle-orm";
import { createExpressMiddleware } from "@trpc/server/adapters/express";
import { registerOAuthRoutes } from "./oauth";
import { appRouter } from "../routers";
import { getDb } from "../db";
import { createContext } from "./context";
import { ENV } from "./env";
import { sdk } from "./sdk";
import { serveStatic, setupVite } from "./vite";

const MAX_BODY_LIMIT = process.env.ML_HTTP_BODY_LIMIT || "15mb";
const MAX_FORM_LIMIT = process.env.ML_HTTP_FORM_LIMIT || "1mb";
const startedAt = Date.now();

type ArtifactUser = { id: number; role: string };

function isPortAvailable(port: number): Promise<boolean> {
  return new Promise(resolve => {
    const server = net.createServer();
    server.listen(port, () => {
      server.close(() => resolve(true));
    });
    server.on("error", () => resolve(false));
  });
}

async function findAvailablePort(startPort: number = 3000): Promise<number> {
  for (let port = startPort; port < startPort + 20; port++) {
    if (await isPortAvailable(port)) return port;
  }
  throw new Error(`No available port found starting from ${startPort}`);
}

function artifactOwnerId(requestPath: string): number | null {
  const segments = requestPath.split("/").filter(Boolean);
  const ownerSegment = segments[0] === "heatmaps" ? segments[1] : segments[0];
  const ownerId = Number(ownerSegment);
  return Number.isInteger(ownerId) && ownerId > 0 ? ownerId : null;
}

async function authenticateArtifactRequest(req: Request, res: Response): Promise<ArtifactUser | null> {
  try {
    const user = ENV.isLocalDemoMode && !ENV.isProduction
      ? (await createContext({ req, res } as any)).user
      : await sdk.authenticateRequest(req);
    return user ? { id: user.id, role: user.role } : null;
  } catch {
    return null;
  }
}

function protectArtifactRequest(req: Request, res: Response, next: NextFunction): void {
  if (req.method !== "GET" && req.method !== "HEAD") {
    res.status(405).json({ error: "Method not allowed" });
    return;
  }
  void (async () => {
    const user = await authenticateArtifactRequest(req, res);
    if (!user) {
      res.status(401).json({ error: "Authentication required" });
      return;
    }
    const ownerId = artifactOwnerId(req.path);
    if (!ownerId || (ownerId !== user.id && user.role !== "admin")) {
      res.status(403).json({ error: "Artifact access denied" });
      return;
    }
    next();
  })().catch(() => {
    if (!res.headersSent) res.status(500).json({ error: "Artifact authorization failed" });
  });
}

function checkpointCandidates(): Record<string, string> {
  const root = path.resolve(process.env.ML_PROJECT_ROOT || process.cwd());
  return {
    cnn: process.env.ML_CNN_CHECKPOINT || path.join(root, "ml_artifacts", "ham10000", "cnn", "best.pt"),
    vit: process.env.ML_VIT_CHECKPOINT || path.join(root, "ml_artifacts", "ham10000", "vit", "best.pt"),
    hybrid: process.env.ML_HYBRID_CHECKPOINT || path.join(root, "ml_artifacts", "ham10000", "hybrid", "best.pt"),
  };
}

async function readinessStatus() {
  const checks: Record<string, unknown> = {
    pythonConfigured: Boolean(process.env.ML_PYTHON_PATH),
    domainReferenceConfigured: Boolean(process.env.ML_DOMAIN_REFERENCE),
    persistentStorageConfigured: Boolean(ENV.forgeApiUrl && ENV.forgeApiKey),
    checkpoints: {},
  };
  const checkpointEntries = await Promise.all(Object.entries(checkpointCandidates()).map(async ([name, checkpoint]) => {
    try {
      await fs.access(checkpoint);
      return [name, true] as const;
    } catch {
      return [name, false] as const;
    }
  }));
  checks.checkpoints = Object.fromEntries(checkpointEntries);

  try {
    const database = await getDb();
    if (!database) {
      checks.database = false;
    } else {
      await database.execute(sql`SELECT 1`);
      checks.database = true;
    }
  } catch {
    checks.database = false;
  }

  const checkpointReady = Object.values(checks.checkpoints as Record<string, boolean>).every(Boolean);
  const ready = Boolean(checks.database) && checkpointReady;
  return { ready, checks };
}

async function startServer() {
  const app = express();
  const server = createServer(app);
  app.disable("x-powered-by");
  app.use((_req, res, next) => {
    res.setHeader("X-Content-Type-Options", "nosniff");
    res.setHeader("Referrer-Policy", "same-origin");
    res.setHeader("Permissions-Policy", "camera=(), microphone=(), geolocation=()");
    next();
  });
  app.use(express.json({ limit: MAX_BODY_LIMIT }));
  app.use(express.urlencoded({ limit: MAX_FORM_LIMIT, extended: true }));

  const runtimeRoot = path.resolve(process.env.ML_UPLOAD_ROOT || path.join(process.env.ML_PROJECT_ROOT || process.cwd(), "runtime", "uploads"));
  app.use("/api/ml-artifacts", protectArtifactRequest, express.static(runtimeRoot, { index: false, dotfiles: "deny" }));

  app.get("/api/health", (_req, res) => {
    res.status(200).json({
      service: "SkinCancerCADDermoIA",
      status: "ok",
      uptimeSeconds: Math.floor((Date.now() - startedAt) / 1000),
    });
  });
  app.get("/api/ready", async (_req, res) => {
    const status = await readinessStatus();
    res.status(status.ready ? 200 : 503).json({ service: "SkinCancerCADDermoIA", ...status });
  });

  registerOAuthRoutes(app);
  app.use("/api/trpc", createExpressMiddleware({ router: appRouter, createContext }));

  if (process.env.NODE_ENV === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  const preferredPort = parseInt(process.env.PORT || "3000");
  const port = await findAvailablePort(preferredPort);
  if (port !== preferredPort) console.log(`Port ${preferredPort} is busy, using port ${port}`);
  server.listen(port, () => console.log(`Server running on http://localhost:${port}/`));
}

startServer().catch(console.error);
