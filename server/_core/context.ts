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

  if (ENV.isLocalDemoMode && !ENV.isProduction) {
    try {
      await db.upsertUser({
        openId: "local-demo",
        name: "Usuário de demonstração",
        email: null,
        loginMethod: "local-demo",
        role: "user",
        lastSignedIn: new Date(),
      });
      user = (await db.getUserByOpenId("local-demo")) ?? null;
    } catch (error) {
      console.error("[Auth] Falha ao preparar usuário local demo:", error);
      user = null;
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
