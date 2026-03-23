<script setup>
defineProps({
  items: { type: Array, required: true },
  active: { type: String, required: true }
});
defineEmits(["select"]);
</script>

<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-title">MockMate AI</div>
      <div class="brand-sub">Mock Interview Agent</div>
    </div>

    <nav class="nav">
      <button
        v-for="it in items"
        :key="it.key"
        class="nav-item"
        :class="{ active: it.key === active }"
        @click="$emit('select', it.key)"
      >
        <span class="nav-dot" />
        <span class="nav-label">{{ it.label }}</span>
      </button>
    </nav>

    <div class="sidebar-footer">
      <div class="muted">Tip: run backend at</div>
      <div class="mono">http://127.0.0.1:8000</div>
    </div>
  </aside>
</template>

