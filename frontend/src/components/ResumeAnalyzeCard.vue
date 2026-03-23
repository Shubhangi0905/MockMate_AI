<script setup>
import { computed, reactive, ref } from "vue";
import IconPlus from "./IconPlus.vue";
import { extractTextFromFile } from "../lib/fileText";

const props = defineProps({
  sessionId: { type: String, default: "" },
  analysis: { type: Object, default: null },
  busy: { type: Object, required: true }
});
const emit = defineEmits(["upload", "analyze"]);

const text = reactive({ resume: "", jd: "" });
const fileError = ref("");

const canCreate = computed(() => text.resume.trim().length >= 20 && !props.busy.upload);
const canAnalyze = computed(() => !!props.sessionId && !props.busy.analyze);

async function pickResume(e) {
  fileError.value = "";
  const file = e?.target?.files?.[0] || null;
  if (!file) return;
  try {
    text.resume = await extractTextFromFile(file);
  } catch (err) {
    fileError.value = err.message || String(err);
    text.resume = "";
  }
}

async function pickJd(e) {
  fileError.value = "";
  const file = e?.target?.files?.[0] || null;
  if (!file) {
    text.jd = "";
    return;
  }
  try {
    text.jd = await extractTextFromFile(file);
  } catch (err) {
    fileError.value = err.message || String(err);
    text.jd = "";
  }
}

function createSession() {
  emit("upload", { resume_text: text.resume, jd_text: text.jd?.trim() ? text.jd : null });
}
</script>

<template>
  <section class="card">
    <div class="card-head">
      <div>
        <div class="card-title">Resume & JD</div>
        <div class="muted">Upload (PDF/TXT) or paste text, then analyze.</div>
      </div>
      <div class="pill">Session: {{ sessionId ? "Active" : "None" }}</div>
    </div>

    <div v-if="fileError" class="callout callout-danger">
      <div class="callout-title">File error</div>
      <div class="mono pre">{{ fileError }}</div>
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
        <textarea v-model="text.resume" placeholder="Paste resume text..." />
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
        <textarea v-model="text.jd" placeholder="Paste JD text (optional)..." />
      </div>
    </div>

    <div class="row" style="margin-top: 12px">
      <button class="btn-primary" :disabled="!canCreate" @click="createSession">
        {{ busy.upload ? "Starting..." : "Start" }}
      </button>
      <button :disabled="!canAnalyze" @click="$emit('analyze')">
        {{ busy.analyze ? "Analyzing..." : "Analyze" }}
      </button>
      <div class="muted">Minimum resume length: ~20 characters.</div>
    </div>

    <div class="divider" style="margin-top: 14px" />

    <div v-if="analysis" class="analysis">
      <div class="analysis-grid">
        <div class="analysis-box">
          <div class="box-title">Role</div>
          <div class="mono">{{ analysis.inferred_role || "—" }}</div>
        </div>
        <div class="analysis-box">
          <div class="box-title">Match score</div>
          <div class="score-sm">
            {{ analysis.match_score === null || analysis.match_score === undefined ? "—" : analysis.match_score + "/100" }}
          </div>
          <div class="muted">Shown when JD is provided.</div>
        </div>
      </div>

      <div class="analysis-section">
        <div class="box-title">Skills</div>
        <div>
          <span v-for="s in analysis.skills || []" :key="s" class="tag">{{ s }}</span>
        </div>
      </div>

      <div v-if="analysis.missing_skills && analysis.missing_skills.length" class="analysis-section">
        <div class="box-title">Missing skills</div>
        <div>
          <span v-for="s in analysis.missing_skills" :key="s" class="tag tag-warn">{{ s }}</span>
        </div>
      </div>

      <div class="analysis-grid" v-if="(analysis.strong_skills && analysis.strong_skills.length) || (analysis.weak_skills && analysis.weak_skills.length)">
        <div v-if="analysis.strong_skills && analysis.strong_skills.length" class="analysis-section">
          <div class="box-title">Strong skills</div>
          <div>
            <span v-for="s in analysis.strong_skills" :key="s" class="tag tag-ok">{{ s }}</span>
          </div>
        </div>
        <div v-if="analysis.weak_skills && analysis.weak_skills.length" class="analysis-section">
          <div class="box-title">Weak skills</div>
          <div>
            <span v-for="s in analysis.weak_skills" :key="s" class="tag tag-warn">{{ s }}</span>
          </div>
        </div>
      </div>

      <div v-if="analysis.experience_summary && analysis.experience_summary.length" class="analysis-section">
        <div class="box-title">Experience summary</div>
        <ul class="list">
          <li v-for="(x, i) in analysis.experience_summary" :key="i">{{ x }}</li>
        </ul>
      </div>
    </div>
    <div v-else class="empty">
      <div class="muted">No analysis yet.</div>
      <div class="muted">Create a session, then click Analyze.</div>
    </div>
  </section>
</template>
