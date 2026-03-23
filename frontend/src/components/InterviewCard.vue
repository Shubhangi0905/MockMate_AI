<script setup>
import { computed, reactive, ref, watch } from "vue";

const props = defineProps({
  sessionId: { type: String, default: "" },
  analysisReady: { type: Boolean, default: false },
  question: { type: String, default: "" },
  interview: { type: Object, required: true },
  busy: { type: Object, required: true }
});

const emit = defineEmits(["start", "submit"]);

const answer = ref("");
const status = ref("");

const canStart = computed(
  () => !!props.sessionId && props.analysisReady && !props.busy.start && !locked.value
);
const canSubmit = computed(
  () => !!props.sessionId && !!props.question && !!answer.value.trim() && !props.busy.submit
);
const locked = computed(() => Number(props.interview.questionIndex || 0) > 0 || props.busy.submit || props.busy.start);

watch(
  () => props.question,
  () => {
    answer.value = "";
    status.value = "";
  }
);

function start() {
  status.value = "";
  emit("start", {
    session_id: props.sessionId,
    mode: props.interview.mode,
    difficulty: props.interview.difficulty,
    max_questions: Number(props.interview.maxQuestions)
  });
}

function submit() {
  status.value = "Answer submitted.";
  emit("submit", { session_id: props.sessionId, answer: answer.value });
}
</script>

<template>
  <section class="card">
    <div class="card-head">
      <div>
        <div class="card-title">Mock Interview</div>
        <div class="muted">Answer one question at a time; report is generated at the end.</div>
      </div>
      <div class="pill mono">Q {{ interview.questionIndex || 0 }} / {{ interview.maxQuestions || 0 }}</div>
    </div>

    <div class="grid3">
      <div>
        <label>Mode</label>
        <select v-model="interview.mode" :disabled="locked">
          <option value="quick">quick</option>
          <option value="full">full</option>
          <option value="weak">weak</option>
        </select>
      </div>
      <div>
        <label>Difficulty</label>
        <select v-model="interview.difficulty" :disabled="locked">
          <option value="easy">easy</option>
          <option value="medium">medium</option>
          <option value="hard">hard</option>
        </select>
        <div class="muted">Difficulty updates automatically during interview.</div>
      </div>
      <div>
        <label>Max questions</label>
        <input v-model="interview.maxQuestions" :disabled="locked" type="number" min="1" max="50" />
      </div>
    </div>

    <div class="row" style="margin-top: 12px">
      <button class="btn-primary" :disabled="!canStart" @click="start">
        {{ busy.start ? "Starting..." : "Start Interview" }}
      </button>
      <div class="muted" v-if="!sessionId">Create a session first.</div>
      <div class="muted" v-else-if="!analysisReady">Run Analyze first.</div>
      <div class="muted" v-else-if="status">{{ status }}</div>
    </div>

    <div class="divider" style="margin-top: 14px" />

    <div>
      <div class="muted">Current question</div>
      <div class="pre">{{ question || "—" }}</div>
    </div>

    <div style="margin-top: 12px">
      <label>Your answer</label>
      <textarea v-model="answer" :disabled="!question" placeholder="Type your answer..." />
      <div class="row" style="margin-top: 10px">
        <button :disabled="!canSubmit" @click="submit">
          {{ busy.submit ? "Submitting..." : "Submit Answer" }}
        </button>
      </div>
    </div>
  </section>
</template>
