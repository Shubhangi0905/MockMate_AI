<script setup>
import { computed, reactive, ref, watch } from "vue";

const props = defineProps({
  sessionId: { type: String, default: "" },
  question: { type: String, default: "" },
  busy: { type: Object, required: true },
  interview: { type: Object, required: true },
  lastEvaluation: { type: Object, default: null }
});

const emit = defineEmits(["start", "submit"]);

const answer = ref("");
const canStart = computed(() => !!props.sessionId && !props.busy.start);
const canSubmit = computed(
  () => !!props.sessionId && !!props.question && !!answer.value.trim() && !props.busy.submit
);

watch(
  () => props.question,
  () => {
    answer.value = "";
  }
);

function start() {
  emit("start", {
    session_id: props.sessionId,
    mode: props.interview.mode,
    difficulty: props.interview.difficulty,
    max_questions: Number(props.interview.maxQuestions)
  });
}

function submit() {
  emit("submit", { session_id: props.sessionId, answer: answer.value });
}
</script>

<template>
  <div class="card">
    <div class="card-head">
      <div>
        <div class="card-title">Interview</div>
        <div class="muted">Adaptive Q→A→Eval loop with difficulty adjustment.</div>
      </div>
      <div class="pill mono">Q {{ interview.questionIndex || 0 }} / {{ interview.maxQuestions || 0 }}</div>
    </div>

    <div class="grid3">
      <div>
        <label>Mode</label>
        <select v-model="interview.mode">
          <option value="quick">quick</option>
          <option value="full">full</option>
          <option value="weak">weak</option>
        </select>
      </div>
      <div>
        <label>Difficulty</label>
        <select v-model="interview.difficulty">
          <option value="easy">easy</option>
          <option value="medium">medium</option>
          <option value="hard">hard</option>
        </select>
      </div>
      <div>
        <label>Max questions</label>
        <input v-model="interview.maxQuestions" type="number" min="1" max="50" />
      </div>
    </div>

    <div class="row" style="margin-top: 10px">
      <button class="btn-primary" :disabled="!canStart" @click="start">
        {{ busy.start ? "Starting..." : "Start Interview" }}
      </button>
      <div class="pill mono">Difficulty: {{ interview.difficulty }}</div>
    </div>

    <div style="margin-top: 12px">
      <div class="muted">Current question</div>
      <div class="pre">{{ question || "—" }}</div>
    </div>

    <div style="margin-top: 10px">
      <label>Your answer</label>
      <textarea v-model="answer" :disabled="!question" placeholder="Type your answer..." />
      <div class="row" style="margin-top: 10px">
        <button :disabled="!canSubmit" @click="submit">
          {{ busy.submit ? "Submitting..." : "Submit Answer" }}
        </button>
      </div>
    </div>

    <div v-if="lastEvaluation" style="margin-top: 12px">
      <div class="muted">Last evaluation</div>
      <div class="eval">
        <div class="eval-score mono">Score: {{ lastEvaluation.score }}/10</div>
        <div class="eval-text">{{ lastEvaluation.feedback }}</div>
        <div class="eval-tip">
          <span class="muted">Tip:</span> {{ lastEvaluation.improvement_tip }}
        </div>
      </div>
    </div>
  </div>
</template>

