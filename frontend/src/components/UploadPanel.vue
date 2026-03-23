<script setup>
import { computed, reactive, ref } from "vue";
import IconPlus from "./IconPlus.vue";
import { extractTextFromFile } from "../lib/fileText";

const props = defineProps({
  sessionId: { type: String, default: "" },
  busy: { type: Object, required: true }
});

const emit = defineEmits(["upload"]);

const files = reactive({
  resume: null,
  jd: null
});

const text = reactive({
  resume: "",
  jd: ""
});

const error = ref("");

const canUpload = computed(() => text.resume.trim().length >= 20 && !props.busy.upload);

async function pickResume(e) {
  error.value = "";
  const file = e?.target?.files?.[0] || null;
  files.resume = file;
  if (!file) return;
  try {
    text.resume = await extractTextFromFile(file);
  } catch (err) {
    error.value = err.message || String(err);
    text.resume = "";
  }
}

async function pickJd(e) {
  error.value = "";
  const file = e?.target?.files?.[0] || null;
  files.jd = file;
  if (!file) {
    text.jd = "";
    return;
  }
  try {
    text.jd = await extractTextFromFile(file);
  } catch (err) {
    error.value = err.message || String(err);
    text.jd = "";
  }
}

function emitUpload() {
  error.value = "";
  emit("upload", { resume_text: text.resume, jd_text: text.jd?.trim() ? text.jd : null });
}
</script>

<template>
  <div class="card">
    <div class="card-head">
      <div>
        <div class="card-title">Upload</div>
        <div class="muted">Upload PDF/TXT or paste text for Resume and JD.</div>
      </div>
      <div class="pill">Session: {{ sessionId ? "Active" : "None" }}</div>
    </div>

    <div v-if="error" class="callout callout-danger">
      <div class="callout-title">Upload error</div>
      <div class="mono pre">{{ error }}</div>
    </div>

    <div class="grid2">
      <div class="panel">
        <div class="panel-head">
          <div class="panel-title">Resume</div>
          <label class="icon-btn" title="Upload resume">
            <IconPlus />
            <input
              type="file"
              accept=".pdf,.txt,.md,text/plain,application/pdf"
              @change="pickResume"
              style="display: none"
            />
          </label>
        </div>
        <textarea v-model="text.resume" placeholder="Paste resume text here..." />
        <div class="muted">Tip: PDF is supported. Large PDFs may take a few seconds to extract.</div>
      </div>

      <div class="panel">
        <div class="panel-head">
          <div class="panel-title">Job Description (optional)</div>
          <label class="icon-btn" title="Upload job description">
            <IconPlus />
            <input
              type="file"
              accept=".pdf,.txt,.md,text/plain,application/pdf"
              @change="pickJd"
              style="display: none"
            />
          </label>
        </div>
        <textarea v-model="text.jd" placeholder="Paste JD text here (optional)..." />
        <div class="muted">If JD is provided, you’ll get a match score and missing skills.</div>
      </div>
    </div>

    <div class="row" style="margin-top: 12px">
      <button class="btn-primary" :disabled="!canUpload" @click="emitUpload">
        {{ busy.upload ? "Starting..." : "Start" }}
      </button>
      <div class="muted">Minimum resume length: ~20 characters.</div>
    </div>
  </div>
</template>
