<script setup>
import { computed } from "vue";

const props = defineProps({
  sessionId: { type: String, default: "" },
  analysis: { type: Object, default: null },
  busy: { type: Object, required: true }
});
const emit = defineEmits(["analyze"]);

const canAnalyze = computed(() => !!props.sessionId && !props.busy.analyze);
</script>

<template>
  <div class="card">
    <div class="card-head">
      <div>
        <div class="card-title">Analyze</div>
        <div class="muted">Extract skills, experience, and gaps (plus match score if JD exists).</div>
      </div>
      <button :disabled="!canAnalyze" @click="$emit('analyze')">
        {{ busy.analyze ? "Analyzing..." : "Run Analyze" }}
      </button>
    </div>

    <div v-if="analysis" class="stack">
      <div class="kv" v-if="analysis.inferred_role">
        <div class="muted">Inferred role</div>
        <div class="mono">{{ analysis.inferred_role }}</div>
      </div>
      <div class="kv" v-if="analysis.match_score !== null && analysis.match_score !== undefined">
        <div class="muted">Match score</div>
        <div class="mono">{{ analysis.match_score }}</div>
      </div>

      <div class="kv">
        <div class="muted">Skills</div>
        <div>
          <span v-for="s in analysis.skills || []" :key="s" class="tag">{{ s }}</span>
        </div>
      </div>

      <div class="kv" v-if="analysis.missing_skills && analysis.missing_skills.length">
        <div class="muted">Missing skills</div>
        <div>
          <span v-for="s in analysis.missing_skills" :key="s" class="tag">{{ s }}</span>
        </div>
      </div>

      <div class="kv" v-if="analysis.strong_skills && analysis.strong_skills.length">
        <div class="muted">Strong skills</div>
        <div>
          <span v-for="s in analysis.strong_skills" :key="s" class="tag">{{ s }}</span>
        </div>
      </div>

      <div class="kv" v-if="analysis.weak_skills && analysis.weak_skills.length">
        <div class="muted">Weak skills</div>
        <div>
          <span v-for="s in analysis.weak_skills" :key="s" class="tag">{{ s }}</span>
        </div>
      </div>

      <div class="kv" v-if="analysis.experience_summary && analysis.experience_summary.length">
        <div class="muted">Experience</div>
        <div class="pre">{{ (analysis.experience_summary || []).join("\n• ").replace(/^/,'• ') }}</div>
      </div>
    </div>

    <div v-else class="empty">
      <div class="muted">No analysis yet.</div>
      <div class="muted">Create a session, then click Run Analyze.</div>
    </div>
  </div>
</template>

