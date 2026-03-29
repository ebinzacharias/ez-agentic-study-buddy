/**
 * Shared API helpers for the EZ Study Lab frontend.
 */

/** Format an API error response into a user-friendly string. */
export function fmtError(data) {
  const code = data?.error_code;
  const msg = data?.error || "Unknown error";
  if (code === "session_expired") return `🔄 ${msg}`;
  if (code === "invalid_quiz_format") return `🧩 ${msg}`;
  if (code === "rate_limit") return `⏳ Rate limited — ${msg}`;
  if (code === "timeout") return `⌛ Timeout — ${msg}`;
  if (code === "auth_error") return `🔑 Auth error — ${msg}`;
  if (code === "llm_error") return `🤖 LLM error — ${msg}`;
  return msg;
}

/** Returns true if the error payload indicates an expired session. */
export function isSessionExpired(data) {
  return data?.error_code === "session_expired";
}
