import { createRouter, createWebHistory } from "vue-router";
import { nextTick } from "vue";
import { useAuthStore } from "../stores/auth";
import HomePage from "../pages/HomePage.vue";
const router = createRouter({
  history: createWebHistory(),
  scrollBehavior(to, from, saved) {
    return saved || { top: 0 };
  },
  routes: [
    {
      path: "/",
      component: HomePage,
      meta: { title: "Workspace gratis" },
    },
    {
      path: "/rooms",
      component: () => import("../pages/RoomsPage.vue"),
      meta: { title: "Cari ruangan" },
    },
    {
      path: "/rooms/:id",
      component: () => import("../pages/RoomPage.vue"),
      meta: { title: "Detail ruangan" },
    },
    {
      path: "/login",
      component: () => import("../pages/AuthPage.vue"),
      meta: { title: "Masuk" },
    },
    {
      path: "/register",
      component: () => import("../pages/AuthPage.vue"),
      meta: { title: "Daftar" },
    },
    {
      path: "/booking/success",
      component: () => import("../pages/SuccessPage.vue"),
      meta: { auth: true, title: "Booking berhasil" },
    },
    {
      path: "/booking/:roomId",
      component: () => import("../pages/ConfirmPage.vue"),
      meta: { auth: true, title: "Konfirmasi booking" },
    },
    {
      path: "/my-bookings",
      component: () => import("../pages/BookingsPage.vue"),
      meta: { auth: true, title: "Booking saya" },
    },
    {
      path: "/profile",
      component: () => import("../pages/ProfilePage.vue"),
      meta: { auth: true, title: "Profil" },
    },
    {
      path: "/admin/:resource?",
      component: () => import("../pages/AdminPage.vue"),
      meta: { auth: true, admin: true, title: "Pengelolaan" },
    },
    {
      path: "/:pathMatch(.*)*",
      component: () => import("../pages/NotFoundPage.vue"),
      meta: { title: "Halaman tidak ditemukan" },
    },
  ],
});
router.beforeEach((to) => {
  const auth = useAuthStore();
  if (to.meta.auth && !auth.loggedIn)
    return { path: "/login", query: { redirect: to.fullPath } };
  if (to.meta.admin && auth.user?.role !== "admin") return "/";
});
router.afterEach(async (to) => {
  document.title = `${to.meta.title} — TechnoPark`;
  await nextTick();
  document.querySelector("#main-content")?.focus({ preventScroll: true });
});
export default router;
