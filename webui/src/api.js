/**
 * Shared API helpers for the EZ Study Lab frontend.
 */

/** @typedef {{ title: string, detail?: string }} ErrorDisplay */

const API_KEY_DISPLAY = {
  title: "Can't verify your API key",
  detail:
    "Add GROQ_API_KEY to the API server's .env file, save it, then restart the API process.",
};

const GENERIC_ASSISTANT_DISPLAY = {
  title: "The assistant hit a snag",
  detail: "Try again in a moment. If it keeps happening, check your API key and connection.",
};

function looksLikeApiKeyIssue(text) {
  const low = text.toLowerCase();
  return (
    low.includes("401") ||
    low.includes("403") ||
    low.includes("invalid_api_key") ||
    low.includes("api key error") ||
    low.includes("invalid api key") ||
    low.includes("incorrect api key") ||
    (low.includes("authentication") && low.includes("invalid"))
  );
}

function stripToolPrefixes(msg) {
  return msg
    .replace(/^Could not generate explanation:\s*/i, "")
    .replace(/^Could not generate plan:\s*/i, "")
    .replace(/^\[error:llm_error\]\s*/i, "")
    .trim();
}

function looksLikeRawPayloadDump(text) {
  return (
    text.includes("{'error'") ||
    text.includes('{"error"') ||
    text.includes("'invalid_request_error'") ||
    text.includes('"invalid_request_error"') ||
    text.includes("Error code:")
  );
}

/**
 * Normalize LLM/auth-style backend text into short UI copy.
 * @param {string} message
 * @returns {ErrorDisplay}
 */
export function humanizeBackendMessage(message) {
  const raw = stripToolPrefixes(String(message || "").trim());
  if (!raw) return { ...GENERIC_ASSISTANT_DISPLAY };

  if (looksLikeApiKeyIssue(raw)) return { ...API_KEY_DISPLAY };

  if (looksLikeRawPayloadDump(raw) || raw.length > 220) {
    if (looksLikeApiKeyIssue(raw)) return { ...API_KEY_DISPLAY };
    return { ...GENERIC_ASSISTANT_DISPLAY };
  }

  if (raw.length <= 120 && !raw.includes("{")) {
    return { title: raw };
  }

  return {
    title: "Something went wrong",
    detail: "Please try again shortly.",
  };
}

/**
 * Map an API JSON error body to user-facing title + optional detail.
 * @param {Record<string, unknown> | null | undefined} data
 * @returns {ErrorDisplay}
 */
export function errorDisplayFromApi(data) {
  const code = data?.error_code;
  const msg = String(data?.error ?? "Unknown error");

  if (code === "session_expired") {
    return {
      title: "Session expired",
      detail: msg || "Upload your material again to start a new session.",
    };
  }

  if (code === "invalid_quiz_format") {
    return {
      title: "Quiz couldn't be built",
      detail:
        "We couldn't create valid multiple-choice questions this time. Try generating the quiz again.",
    };
  }

  if (code === "rate_limit") {
    return {
      title: "Too many requests",
      detail: "The AI service is rate-limited. Wait a short time, then try again.",
    };
  }

  if (code === "timeout") {
    return {
      title: "Request timed out",
      detail: "Check your network or proxy, then try again.",
    };
  }

  if (code === "auth_error" || code === "llm_error") {
    return humanizeBackendMessage(msg);
  }

  return humanizeBackendMessage(msg);
}

/**
 * Strip legacy emoji-prefixed fmtError strings and re-humanize.
 * @param {string} message
 * @returns {ErrorDisplay}
 */
export function errorDisplayFromCaughtMessage(message) {
  let m = String(message || "").trim();
  m = m.replace(/^🤖\s*LLM error\s*[—:-]\s*/i, "");
  m = m.replace(/^🔑\s*Auth error\s*[—:-]\s*/i, "");
  m = m.replace(/^🔄\s*/i, "");
  m = m.replace(/^🧩\s*/i, "");
  m = m.replace(/^⏳\s*Rate limited\s*[—:-]\s*/i, "");
  m = m.replace(/^⌛\s*Timeout\s*[—:-]\s*/i, "");

  const low = m.toLowerCase();
  if (low.includes("rate limit") || low.includes("429")) {
    return {
      title: "Too many requests",
      detail: "The AI service is rate-limited. Wait a short time, then try again.",
    };
  }
  if (low.includes("timeout") || low.includes("timed out")) {
    return {
      title: "Request timed out",
      detail: "Check your network or proxy, then try again.",
    };
  }

  return humanizeBackendMessage(m);
}

/** @param {Record<string, unknown> | null | undefined} data */
export function createUserFacingApiError(data) {
  const display = errorDisplayFromApi(data);
  const err = new Error(display.title);
  err.userFacing = display;
  return err;
}

/** Format an API error response into a single-line string (legacy / logging). */
export function fmtError(data) {
  const { title, detail } = errorDisplayFromApi(data);
  return detail ? `${title} — ${detail}` : title;
}

/** Returns true if the error payload indicates an expired session. */
export function isSessionExpired(data) {
  return data?.error_code === "session_expired";
}
