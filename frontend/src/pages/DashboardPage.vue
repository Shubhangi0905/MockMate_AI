<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";

import StatCard from "../components/StatCard.vue";
import { clearSession, sessionStore } from "../store/sessionStore";

const router = useRouter();

const matchScore = computed(() => {
  const v = sessionStore.analysis?.match_score;
  return v === null || v === undefined ? "—" : `${v}/100`;
});

const skillCount = computed(() => (sessionStore.analysis?.skills || []).length);

const interviewScore = computed(() => {
  if (sessionStore.report?.overall_score !== null && sessionStore.report?.overall_score !== undefined) {
    return `${sessionStore.report.overall_score}/100`;
  }
  const evals = sessionStore.transcript?.evaluations || [];
  if (!evals.length) return "—";
  const avg10 =
    evals.reduce((sum, e) => sum + Number(e?.score ?? 0), 0) / Math.max(1, evals.length);
  const score100 = Math.round(avg10 * 10);
  return `${score100}/100`;
});

function go(path) {
  router.push(path);
}
</script>

<template>
  <div class="page-head">
    <div>
      <div class="page-title">Dashboard</div>
      <div class="muted">Complete a full mock interview flow in a few steps.</div>
    </div>
    <div class="row" style="justify-content: flex-end; flex: 0 0 auto">
      <button class="btn-danger" :disabled="!sessionStore.sessionId" @click="clearSession">Start Over</button>
    </div>
  </div>

  <div class="grid-cards" style="margin-bottom: 14px">
    <StatCard
      label="Session"
      :value="sessionStore.sessionId ? 'Active' : 'None'"
      :hint="sessionStore.sessionId ? 'In progress' : 'Start from Resume & JD'"
    />
    <StatCard label="Match Score" :value="matchScore" hint="Available when JD is provided" />
    <StatCard label="Interview Score" :value="interviewScore" hint="Updates during interview" />
    <StatCard label="Skills Extracted" :value="skillCount" hint="From analysis" />
  </div>

  <div class="grid2">
    <div class="card">
      <div class="card-head">
        <div>
          <div class="card-title">1) Resume & JD</div>
          <div class="muted">Upload/paste and run analysis.</div>
        </div>
        <button class="btn-primary" @click="go('/resume')">Open</button>
      </div>
      <div class="muted">Creates a session and extracts skills + gaps.</div>
    </div>

    <div class="card">
      <div class="card-head">
        <div>
          <div class="card-title">2) Interview</div>
          <div class="muted">Adaptive questions based on your profile.</div>
        </div>
        <button class="btn-primary" :disabled="!sessionStore.analysis" @click="go('/interview')">Open</button>
      </div>
      <div class="muted">Requires analysis to be completed first.</div>
    </div>

    <div class="card">
      <div class="card-head">
        <div>
          <div class="card-title">3) Report</div>
          <div class="muted">Final report with PDF download.</div>
        </div>
        <button class="btn-primary" :disabled="!sessionStore.sessionId" @click="go('/report')">Open</button>
      </div>
      <div class="muted">Report appears after the interview finishes.</div>
    </div>
  </div>
</template>
