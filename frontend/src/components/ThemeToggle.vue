<script setup>
defineProps({
  modelValue: { type: String, required: true }
});
defineEmits(["update:modelValue"]);
</script>

<template>
  <button
    class="toggle"
    role="switch"
    :aria-checked="modelValue === 'dark'"
    @click="$emit('update:modelValue', modelValue === 'dark' ? 'light' : 'dark')"
  >
    <span class="toggle-track">
      <span class="toggle-thumb" :class="{ on: modelValue === 'dark' }" />
    </span>
    <span class="toggle-label">{{ modelValue === "dark" ? "Dark" : "Light" }}</span>
  </button>
</template>

