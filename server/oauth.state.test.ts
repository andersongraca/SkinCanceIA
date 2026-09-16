import { describe, expect, it } from "vitest";
import { decodeOAuthState, encodeOAuthState } from "@shared/const";

describe("OAuth state", () => {
  it("round-trips redirect URI and nonce", () => {
    const state = encodeOAuthState({
      redirectUri: "http://localhost:3000/api/oauth/callback",
      nonce: "nonce-with-at-least-16-chars",
    });

    expect(decodeOAuthState(state)).toEqual({
      redirectUri: "http://localhost:3000/api/oauth/callback",
      nonce: "nonce-with-at-least-16-chars",
    });
  });

  it("rejects missing, malformed and weak states", () => {
    expect(decodeOAuthState(undefined)).toBeNull();
    expect(decodeOAuthState("not-base64-json")).toBeNull();
    const weak = encodeOAuthState({
      redirectUri: "https://example.com/callback",
      nonce: "short",
    });
    expect(decodeOAuthState(weak)).toBeNull();
  });
});
