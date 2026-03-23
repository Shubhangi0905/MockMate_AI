<script setup>
import { computed } from "vue";
import { buildReportPdf } from "../lib/reportPdf";

const props = defineProps({
  sessionId: { type: String, default: "" },
  busy: { type: Object, required: true },
  analysis: { type: Object, default: null },
  state: { type: Object, default: null },
  report: { type: Object, default: null }
});

const emit = defineEmits(["fetchReport"]);

const canFetch = computed(() => !!props.sessionId && !props.busy.report);
const canDownload = computed(() => !!props.report && !!props.sessionId);

function downloadPdf() {
  const questions = props.state?.questions || [];
  const answers = props.state?.answers || [];
  const evaluations = props.state?.evaluations || [];

  const doc = buildReportPdf({
    sessionId: props.sessionId,
    analysis: props.analysis,
    questions,
    answers,
    evaluations,
    report: props.report
  });
  doc.save(`mockmate_report_${props.sessionId}.pdf`);
}
</script>

<template>
  <div class="card">
    <div class="card-head">
      <div>
        <div class="card-title">Report</div>
        <div class="muted">View a structured report and download as PDF.</div>
      </div>
      <div class="row" style="justify-content: flex-end; flex: 0 0 auto">
        <button :disabled="!canFetch" @click="$emit('fetchReport')">
          {{ busy.report ? "Fetching..." : "Refresh" }}
        </button>
        <button class="btn-primary" :disabled="!canDownload" @click="downloadPdf">Download PDF</button>
      </div>
    </div>

    <div v-if="report" class="stack">
      <div class="report-grid">
        <div class="report-metric">
          <div class="muted">Overall score</div>
          <div class="score">{{ report.overall_score }}/100</div>
          <div class="muted">{{ report.verdict }}</div>
        </div>
        <div class="report-box">
          <div class="box-title">Strengths</div>
          <ul>
            <li v-for="s in report.strengths || []" :key="s">{{ s }}</li>
          </ul>
        </div>
        <div class="report-box">
          <div class="box-title">Weaknesses</div>
          <ul>
            <li v-for="s in report.weaknesses || []" :key="s">{{ s }}</li>
          </ul>
        </div>
        <div class="report-box">
          <div class="box-title">Suggestions</div>
          <ul>
            <li v-for="s in report.suggestions || []" :key="s">{{ s }}</li>
          </ul>
        </div>
      </div>

      <div class="divider" />

      <div>
        <div class="muted">Transcript</div>
        <div v-if="state && (state.questions || []).length" class="stack">
          <div v-for="(q, idx) in state.questions" :key="idx" class="transcript">
            <div class="mono muted">Q{{ idx + 1 }}</div>
            <div class="pre">{{ q }}</div>
            <div class="mono muted" style="margin-top: 8px">Answer</div>
            <div class="pre">{{ (state.answers || [])[idx] || "—" }}</div>
            <div v-if="(state.evaluations || [])[idx]" class="eval-mini">
              <div class="mono">Score: {{ (state.evaluations || [])[idx].score }}/10</div>
              <div class="muted">{{ (state.evaluations || [])[idx].feedback }}</div>
              <div class="muted">Tip: {{ (state.evaluations || [])[idx].improvement_tip }}</div>
            </div>
          </div>
        </div>
        <div v-else class="muted">No transcript yet. Finish at least one question.</div>
      </div>
    </div>

    <div v-else class="empty">
      <div class="muted">No report yet.</div>
      <div class="muted">Finish the interview, then click Refresh.</div>
    </div>
  </div>
</template>

