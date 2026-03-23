<script setup>
import { computed, ref } from "vue";
import { buildReportPdf } from "../lib/reportPdf";

const props = defineProps({
  sessionId: { type: String, default: "" },
  report: { type: Object, default: null },
  analysis: { type: Object, default: null },
  transcript: { type: Object, default: null },
  busy: { type: Object, required: true }
});

const emit = defineEmits(["refresh"]);

const canRefresh = computed(() => !!props.sessionId && !props.busy.report);
const canDownload = computed(() => !!props.report && !!props.sessionId);

const showTranscript = ref(false);

function downloadPdf() {
  const questions = props.transcript?.questions || [];
  const answers = props.transcript?.answers || [];
  const evaluations = props.transcript?.evaluations || [];
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
  <section class="card">
    <div class="card-head">
      <div>
        <div class="card-title">Final Report</div>
        <div class="muted">Generated after the interview completes.</div>
      </div>
      <div class="row report-actions" style="justify-content: flex-end; flex: 0 0 auto">
        <button :disabled="!canRefresh" @click="$emit('refresh')">
          {{ busy.report ? "Refreshing..." : "Refresh" }}
        </button>
        <button class="btn-primary" :disabled="!canDownload" @click="downloadPdf">Download PDF</button>
      </div>
    </div>

    <div v-if="!sessionId" class="empty">
      <div class="muted">No session yet.</div>
      <div class="muted">Create a session from Resume & JD first.</div>
    </div>

    <div v-else-if="report" class="stack">
      <div class="kpi-grid">
        <div class="kpi">
          <div class="kpi-label">Overall score</div>
          <div class="kpi-value">{{ report.overall_score }}/100</div>
          <div class="kpi-sub muted">{{ report.verdict }}</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Questions answered</div>
          <div class="kpi-value">{{ (transcript?.answers || []).length }}</div>
          <div class="kpi-sub muted">Out of {{ (transcript?.questions || []).length || "—" }}</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Focus areas</div>
          <div class="kpi-chips">
            <span v-for="s in (analysis?.missing_skills || []).slice(0, 4)" :key="s" class="chip chip-warn">{{ s }}</span>
            <span v-for="s in (analysis?.weak_skills || []).slice(0, 4)" :key="s" class="chip chip-warn">{{ s }}</span>
            <span v-if="!(analysis?.missing_skills || []).length && !(analysis?.weak_skills || []).length" class="muted">—</span>
          </div>
        </div>
      </div>

      <div class="section-grid">
        <div class="section">
          <div class="section-title">Strengths</div>
          <ul class="list-clean">
            <li v-for="s in report.strengths || []" :key="s">{{ s }}</li>
          </ul>
        </div>
        <div class="section">
          <div class="section-title">Weaknesses</div>
          <ul class="list-clean">
            <li v-for="s in report.weaknesses || []" :key="s">{{ s }}</li>
          </ul>
        </div>
        <div class="section">
          <div class="section-title">Suggestions</div>
          <ul class="list-clean">
            <li v-for="s in report.suggestions || []" :key="s">{{ s }}</li>
          </ul>
        </div>
      </div>

      <div class="divider" />

      <div class="row" style="justify-content: space-between">
        <div>
          <div class="section-title">Transcript</div>
          <div class="muted">Optional: review Q/A with scores.</div>
        </div>
        <button @click="showTranscript = !showTranscript">
          {{ showTranscript ? "Hide Transcript" : "View Transcript" }}
        </button>
      </div>

      <div v-if="showTranscript" class="stack">
        <div
          v-for="(q, idx) in transcript?.questions || []"
          :key="idx"
          class="transcript-item"
        >
          <div class="row" style="justify-content: space-between; align-items: baseline">
            <div class="mono muted">Q{{ idx + 1 }}</div>
            <div v-if="(transcript?.evaluations || [])[idx]" class="pill">
              Score: {{ (transcript?.evaluations || [])[idx].score }}/10
            </div>
          </div>
          <div class="pre" style="margin-top: 8px">{{ q }}</div>
          <div class="muted" style="margin-top: 10px">Answer</div>
          <div class="pre">{{ (transcript?.answers || [])[idx] || "—" }}</div>
          <div v-if="(transcript?.evaluations || [])[idx]" class="callout" style="margin-top: 10px">
            <div class="callout-title">Feedback</div>
            <div class="muted">{{ (transcript?.evaluations || [])[idx].feedback }}</div>
            <div class="muted" style="margin-top: 8px">
              Tip: {{ (transcript?.evaluations || [])[idx].improvement_tip }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty">
      <div class="muted">No final report yet.</div>
      <div class="muted">Complete the interview, then click Refresh.</div>
    </div>
  </section>
</template>
