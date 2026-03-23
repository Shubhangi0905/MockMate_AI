<script setup>
import FinalReportCard from "../components/FinalReportCard.vue";
import { useRouter } from "vue-router";
import { refreshReport, sessionStore } from "../store/sessionStore";

const router = useRouter();
</script>

<template>
  <div class="page-head">
    <div>
      <div class="page-title">Report</div>
      <div class="muted">View the final report and download it as PDF.</div>
    </div>
    <div class="row" style="justify-content: flex-end; flex: 0 0 auto">
      <button v-if="!sessionStore.sessionId" class="btn-primary" @click="router.push('/resume')">Go to Resume</button>
      <button v-else-if="!sessionStore.report" class="btn-primary" @click="router.push('/interview')">Go to Interview</button>
    </div>
  </div>

  <FinalReportCard
    :session-id="sessionStore.sessionId"
    :report="sessionStore.report"
    :analysis="sessionStore.analysis"
    :transcript="sessionStore.transcript"
    :busy="sessionStore.busy"
    @refresh="refreshReport"
  />
</template>
