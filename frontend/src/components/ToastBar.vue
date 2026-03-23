<script setup>
defineProps({
  message: { type: String, default: "" }
});
defineEmits(["close"]);
</script>

<template>
  <div v-if="message" class="toast">
    <div class="toast-title">Error</div>
    <div class="toast-body">{{ message }}</div>
    <button class="toast-close" @click="$emit('close')">Close</button>
  </div>
</template>

