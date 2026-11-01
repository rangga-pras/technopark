<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import RequestState from "../components/RequestState.vue";
const auth = useAuthStore(),
  router = useRouter(),
  error = ref(""),
  loading = ref(false);
async function refresh() {
  loading.value = true;
  error.value = "";
  try {
    auth.user = await auth.api("/auth/me");
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
function logout() {
  auth.logout();
  router.replace("/");
}
onMounted(refresh);
</script>
<template>
  <div class="shell page narrow">
    <h1>Profil Anda</h1>
    <p>Akun untuk setiap rencana produktif Anda.</p>
    <RequestState :loading="loading" :error="error" @retry="refresh" />
    <section v-if="auth.user" class="panel profile-panel">
      <span class="avatar large">{{ auth.user.name[0].toUpperCase() }}</span>
      <h2>{{ auth.user.name }}</h2>
      <dl class="summary-list">
        <div>
          <dt>Email</dt>
          <dd>{{ auth.user.email }}</dd>
        </div>
        <div>
          <dt>Peran</dt>
          <dd>{{ auth.user.role === "admin" ? "Admin" : "Pengguna" }}</dd>
        </div>
        <div>
          <dt>Status akun</dt>
          <dd>{{ auth.user.is_active ? "Aktif" : "Nonaktif" }}</dd>
        </div>
      </dl>
      <p class="notice">
        Sesi Anda hanya tersimpan di memori. Refresh halaman atau keluar akan
        mengakhiri sesi pada perangkat ini.
      </p>
      <RouterLink
        v-if="auth.user.role === 'admin'"
        class="button secondary"
        to="/admin"
        >Buka pengelolaan</RouterLink
      ><button class="button danger" @click="logout">Keluar dari akun</button>
    </section>
  </div>
</template>
