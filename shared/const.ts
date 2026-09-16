export const COOKIE_NAME = "app_session_id";
export const OAUTH_STATE_COOKIE = "__Host-oauth_state";
export const ONE_YEAR_MS = 1000 * 60 * 60 * 24 * 365;
export const AXIOS_TIMEOUT_MS = 30_000;
export const UNAUTHED_ERR_MSG = "Please login (10001)";
export const NOT_ADMIN_ERR_MSG = "You do not have required permission (10002)";

export type OAuthState = {
  redirectUri: string;
  nonce: string;
};

function encodeBase64Url(value: string): string {
  const bytes = new TextEncoder().encode(value);
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function decodeBase64Url(value: string): string {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized + "=".repeat((4 - (normalized.length % 4)) % 4);
  const binary = atob(padded);
  const bytes = Uint8Array.from(binary, character => character.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

export function encodeOAuthState(state: OAuthState): string {
  return encodeBase64Url(JSON.stringify(state));
}

export function decodeOAuthState(value: string | undefined | null): OAuthState | null {
  if (!value) return null;
  try {
    const parsed = JSON.parse(decodeBase64Url(value)) as Partial<OAuthState>;
    if (
      typeof parsed.redirectUri !== "string" ||
      !/^https?:\/\//.test(parsed.redirectUri) ||
      typeof parsed.nonce !== "string" ||
      parsed.nonce.length < 16
    ) {
      return null;
    }
    return { redirectUri: parsed.redirectUri, nonce: parsed.nonce };
  } catch {
    return null;
  }
}
