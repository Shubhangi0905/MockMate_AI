import { createRouter, createWebHistory } from "vue-router";

import DashboardPage from "../pages/DashboardPage.vue";
import ResumePage from "../pages/ResumePage.vue";
import InterviewPage from "../pages/InterviewPage.vue";
import ReportPage from "../pages/ReportPage.vue";

export const routes = [
  { path: "/", name: "dashboard", component: DashboardPage },
  { path: "/resume", name: "resume", component: ResumePage },
  { path: "/interview", name: "interview", component: InterviewPage },
  { path: "/report", name: "report", component: ReportPage }
];

export const router = createRouter({
  history: createWebHistory(),
  routes
});

