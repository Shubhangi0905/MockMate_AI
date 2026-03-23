import { reactive } from "vue";
import { api } from "../api";

function safeJsonParse(raw, fallback) {
  try {
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

const persisted = safeJsonParse(localStorage.getItem("mockmate_prefs"), {});

// Clean up legacy key from earlier iterations that stored server-only session ids.
// Keeping it would cause "Unknown session_id" after a browser refresh.
try {
  if (localStorage.getItem("mockmate_snapshot")) localStorage.removeItem("mockmate_snapshot");
} catch {
  // ignore
}

export const sessionStore = reactive({
  theme: persisted.theme || "dark",

  sessionId: "",
  analysis: null,
  currentQuestion: "",
  report: null,

  transcript: { questions: [], answers: [], evaluations: [] },

  interview: {
    mode: "quick",
    difficulty: "easy",
    maxQuestions: 5,
    questionIndex: 0,
    done: false
  },

  busy: {
    upload: false,
    analyze: false,
    start: false,
    submit: false,
    report: false
  },

  errorMsg: ""
});

export function persistPrefs() {
  localStorage.setItem("mockmate_prefs", JSON.stringify({ theme: sessionStore.theme }));
}

export function clearSession() {
  sessionStore.sessionId = "";
  sessionStore.analysis = null;
  sessionStore.currentQuestion = "";
  sessionStore.report = null;
  sessionStore.transcript = { questions: [], answers: [], evaluations: [] };
  sessionStore.interview.questionIndex = 0;
  sessionStore.interview.done = false;
}

function setError(e) {
  sessionStore.errorMsg = e?.message || String(e);
}

function handleUnknownSession(err) {
  const msg = err?.message || "";
  if (msg.toLowerCase().includes("unknown session_id") || err?.status === 404) {
    clearSession();
    sessionStore.errorMsg = "Session is invalid/expired. Please create a new session by uploading resume again.";
    return true;
  }
  return false;
}

export async function createSession({ resume_text, jd_text }) {
  sessionStore.errorMsg = "";
  sessionStore.busy.upload = true;
  try {
    clearSession();
    const res = await api.upload({ resume_text, jd_text });
    sessionStore.sessionId = res.session_id;
  } catch (e) {
    setError(e);
  } finally {
    sessionStore.busy.upload = false;
  }
}

export async function runAnalyze() {
  sessionStore.errorMsg = "";
  sessionStore.busy.analyze = true;
  try {
    const res = await api.analyze({ session_id: sessionStore.sessionId });
    sessionStore.analysis = res.analysis;
  } catch (e) {
    if (!handleUnknownSession(e)) setError(e);
  } finally {
    sessionStore.busy.analyze = false;
  }
}

export async function startInterview(payload) {
  sessionStore.errorMsg = "";
  sessionStore.busy.start = true;
  try {
    sessionStore.currentQuestion = "";
    sessionStore.report = null;
    sessionStore.transcript = { questions: [], answers: [], evaluations: [] };
    sessionStore.interview.questionIndex = 0;
    sessionStore.interview.done = false;

    const res = await api.startInterview(payload);
    sessionStore.currentQuestion = res.question;
    sessionStore.interview.questionIndex = res.question_index;
    sessionStore.interview.maxQuestions = res.max_questions;
    sessionStore.transcript.questions = res.question ? [res.question] : [];
  } catch (e) {
    if (!handleUnknownSession(e)) setError(e);
  } finally {
    sessionStore.busy.start = false;
  }
}

export async function submitAnswer(payload) {
  sessionStore.errorMsg = "";
  sessionStore.busy.submit = true;
  try {
    const res = await api.submitAnswer(payload);
    sessionStore.interview.questionIndex = res.question_index;
    sessionStore.interview.maxQuestions = res.max_questions;
    sessionStore.interview.done = !!res.done;
    sessionStore.interview.difficulty = res.difficulty;

    sessionStore.transcript.answers.push(payload.answer);
    if (res.evaluation) sessionStore.transcript.evaluations.push(res.evaluation);

    sessionStore.currentQuestion = res.next_question || "";
    if (res.next_question) sessionStore.transcript.questions.push(res.next_question);

    if (res.report_ready) {
      await refreshReport();
    }
    return res;
  } catch (e) {
    if (!handleUnknownSession(e)) setError(e);
    return null;
  } finally {
    sessionStore.busy.submit = false;
  }
}

export async function refreshReport() {
  sessionStore.errorMsg = "";
  sessionStore.busy.report = true;
  try {
    sessionStore.report = (await api.report(sessionStore.sessionId)).report;
  } catch (e) {
    if (!handleUnknownSession(e)) setError(e);
  } finally {
    sessionStore.busy.report = false;
  }
}
