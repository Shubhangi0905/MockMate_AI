<script setup>
import ResumeAnalyzeCard from "../components/ResumeAnalyzeCard.vue";
import { createSession, runAnalyze, sessionStore } from "../store/sessionStore";
</script>

<template>
  <div class="page-head">
    <div>
      <div class="page-title">Resume & JD</div>
      <div class="muted">Upload Resume and optional JD, then analyze.</div>
    </div>
  </div>

  <ResumeAnalyzeCard
    :session-id="sessionStore.sessionId"
    :analysis="sessionStore.analysis"
    :busy="sessionStore.busy"
    @upload="createSession"
    @analyze="runAnalyze"
  />
</template>

