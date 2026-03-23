const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

function errorMessageFromData(data, status) {
  const detail = data?.detail;
  if (typeof detail === "string") return detail;
  if (detail && typeof detail === "object") {
    const msg = detail.message || detail.error || null;
    if (msg) {
      if (typeof detail.retry_after_seconds === "number") {
        return `${msg} Retry after ~${detail.retry_after_seconds}s.`;
      }
      return msg;
    }
    return JSON.stringify(detail);
  }
  if (typeof data?.message === "string") return data.message;
  return `HTTP ${status}`;
}

async function request(path, { method = "GET", body } = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined
  });

  let data = null;
  const text = await res.text();
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { raw: text };
  }

  if (!res.ok) {
    const message = errorMessageFromData(data, res.status);
    const err = new Error(message);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

export const api = {
  health: () => request("/health"),
  upload: (payload) => request("/upload", { method: "POST", body: payload }),
  analyze: (payload) => request("/analyze", { method: "POST", body: payload }),
  startInterview: (payload) => request("/start-interview", { method: "POST", body: payload }),
  nextQuestion: (payload) => request("/next-question", { method: "POST", body: payload }),
  submitAnswer: (payload) => request("/submit-answer", { method: "POST", body: payload }),
  report: (sessionId) => request(`/report?session_id=${encodeURIComponent(sessionId)}`)
};
