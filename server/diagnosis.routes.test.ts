import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

function createContext(user: TrpcContext["user"] = null): TrpcContext {
  return {
    user,
    req: { protocol: "http", headers: {} } as TrpcContext["req"],
    res: {} as TrpcContext["res"],
  };
}

describe("diagnosis procedures", () => {
  it("rejects image upload without an authenticated user", async () => {
    const caller = appRouter.createCaller(createContext());
    await expect(caller.diagnosis.uploadImage({
      fileName: "lesion.jpg",
      mimeType: "image/jpeg",
      dataUrl: "data:image/jpeg;base64,AA==",
    })).rejects.toMatchObject({ code: "UNAUTHORIZED" });
  });

  it("rejects stored-image classification without an authenticated user", async () => {
    const caller = appRouter.createCaller(createContext());
    await expect(caller.diagnosis.classifyStoredImage({ imageId: 1 })).rejects.toMatchObject({ code: "UNAUTHORIZED" });
  });

  it("returns an empty metrics list when no database is configured", async () => {
    const caller = appRouter.createCaller(createContext());
    await expect(caller.metrics.getAllMetrics()).resolves.toEqual([]);
  });
});
