import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { request } from "../api";
export const useAuthStore = defineStore("auth", () => {
  const token = ref(null);
  const user = ref(null);
  const loggedIn = computed(() => Boolean(token.value && user.value));
  let expiryTimer;
  function logout() {
    token.value = null;
    user.value = null;
    clearTimeout(expiryTimer);
  }
  async function login(email, password) {
    const data = await request("/auth/login", {
      method: "POST",
      body: { email, password },
    });
    token.value = data.access_token;
    user.value = data.user;
    const payload = JSON.parse(
      atob(
        data.access_token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"),
      ),
    );
    expiryTimer = setTimeout(
      logout,
      Math.max(0, payload.exp * 1000 - Date.now()),
    );
  }
  async function api(path, options) {
    try {
      return await request(path, options, token.value);
    } catch (error) {
      if (error.status === 401 && token.value) logout();
      throw error;
    }
  }
  return { token, user, loggedIn, login, logout, api };
});
