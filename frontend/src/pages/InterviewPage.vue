<script setup>
import { useRouter } from "vue-router";
import InterviewCard from "../components/InterviewCard.vue";
import { sessionStore, startInterview, submitAnswer } from "../store/sessionStore";

const router = useRouter();

async function onSubmit(payload) {
  const res = await submitAnswer(payload);
  if (res && (res.report_ready || res.done)) {
    router.push("/report");
  }
}
</script>

<template>
  <div class="page-head">
    <div>
      <div class="page-title">Interview</div>
      <div class="muted">Start and answer questions; the report is generated at the end.</div>
    </div>
  </div>

  <InterviewCard
    :session-id="sessionStore.sessionId"
    :analysis-ready="!!sessionStore.analysis"
    :question="sessionStore.currentQuestion"
    :interview="sessionStore.interview"
    :busy="sessionStore.busy"
    @start="startInterview"
    @submit="onSubmit"
  />
</template>
