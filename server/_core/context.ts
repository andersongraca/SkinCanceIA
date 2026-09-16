import type { CreateExpressContextOptions } from "@trpc/server/adapters/express";
import type { User } from "../../drizzle/schema";
import * as db from "../db";
import { ENV } from "./env";
import { sdk } from "./sdk";

export type TrpcContext = {
  req: CreateExpressContextOptions["req"];
  res: CreateExpressContextOptions["res"];
  user: User | null;
};

export async function createContext(
  opts: CreateExpressContextOptions
): Promise<TrpcContext> {
  let user: User | null = null;

  const localInferenceMode = !ENV.isProduction && (ENV.isLocalDemoMode || !process.env.DATABASE_URL);

  if (localInferenceMode) {
    const demoUser: User = {
      id: 1,
      openId: "local-demo",
      name: "Usuário de demonstração",
      email: null,
      loginMethod: "local-demo",
      role: "user",
      createdAt: new Date(0),
      updatedAt: new Date(0),
      lastSignedIn: new Date(0),
    };
    try {
      const database = await db.getDb();
      if (!database) {
        user = demoUser;
      } else {
        await db.upsertUser({
          openId: "local-demo",
          name: "Usuário de demonstração",
          email: null,
          loginMethod: "local-demo",
          role: "user",
          lastSignedIn: new Date(),
        });
        user = (await db.getUserByOpenId("local-demo")) ?? demoUser;
      }
    } catch (error) {
      console.error("[Auth] Falha ao preparar usuário local demo:", error);
      user = demoUser;
    }
  } else {
    try {
      user = await sdk.authenticateRequest(opts.req);
    } catch (error) {
      // Authentication is optional for public procedures.
      user = null;
    }
  }

  return {
    req: opts.req,
    res: opts.res,
    user,
  };
}
