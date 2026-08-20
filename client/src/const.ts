export { COOKIE_NAME, ONE_YEAR_MS } from "@shared/const";
import { encodeOAuthState } from "@shared/const";

export const isAuthConfigured = Boolean(
  import.meta.env.VITE_OAUTH_PORTAL_URL?.trim() &&
    import.meta.env.VITE_APP_ID?.trim(),
);

// O modo demo precisa ser opt-in explícito. Sem essa variável, a aplicação usa OAuth real.
export const isDemoMode = import.meta.env.VITE_LOCAL_DEMO_MODE === "true";

export const getLoginUrl = (): string | null => {
  const oauthPortalUrl = import.meta.env.VITE_OAUTH_PORTAL_URL?.trim();
  const appId = import.meta.env.VITE_APP_ID?.trim();
  if (!oauthPortalUrl || !appId) return null;

  const redirectUri = `${window.location.origin}/api/oauth/callback`;
  const nonce = crypto.randomUUID();
  document.cookie = `__Host-oauth_state=${nonce}; Path=/; Max-Age=600; SameSite=None; Secure`;
  const state = encodeOAuthState({ redirectUri, nonce });

  const url = new URL(`${oauthPortalUrl.replace(/\/+$/, "")}/app-auth`);
  url.searchParams.set("appId", appId);
  url.searchParams.set("redirectUri", redirectUri);
  url.searchParams.set("state", state);
  url.searchParams.set("type", "signIn");
  return url.toString();
};
