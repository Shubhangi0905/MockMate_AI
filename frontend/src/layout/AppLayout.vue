<script setup>
import { computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import ThemeToggle from "../components/ThemeToggle.vue";
import ToastBar from "../components/ToastBar.vue";
import { persistPrefs, sessionStore } from "../store/sessionStore";

const route = useRoute();
const router = useRouter();

const nav = [
  { path: "/", label: "Dashboard" },
  { path: "/resume", label: "Resume & JD" },
  { path: "/interview", label: "Interview" },
  { path: "/report", label: "Report" }
];

const activePath = computed(() => route.path);

function go(path) {
  router.push(path);
}

function applyTheme(next) {
  const t = next === "light" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", t);
}

watch(
  () => sessionStore.theme,
  (t) => {
    applyTheme(t);
    persistPrefs();
  },
  { immediate: true }
);
</script>

<template>
  <div class="shell">
    <aside class="side">
      <div class="side-brand">
        <div class="brand-title">MockMate AI</div>
        <div class="brand-sub">Mock Interview Dashboard</div>
      </div>

      <nav class="side-nav">
        <button
          v-for="it in nav"
          :key="it.path"
          class="side-link"
          :class="{ active: it.path === activePath }"
          @click="go(it.path)"
        >
          <span class="nav-dot" />
          <span>{{ it.label }}</span>
        </button>
      </nav>

      <div class="side-footer">
        <ThemeToggle v-model="sessionStore.theme" />
        <div class="muted" style="margin-top: 10px">Session</div>
        <div class="pill" style="display: inline-flex; margin-top: 6px">
          {{ sessionStore.sessionId ? "Active" : "None" }}
        </div>
      </div>
    </aside>

    <main class="content">
      <div class="content-inner">
        <router-view />
      </div>
    </main>

    <ToastBar :message="sessionStore.errorMsg" @close="sessionStore.errorMsg = ''" />
  </div>
</template>
