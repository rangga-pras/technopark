<script setup>
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "./stores/auth";
import BrandLogo from "./components/BrandLogo.vue";
import AppIcon from "./components/AppIcon.vue";
const auth = useAuthStore(),
  route = useRoute(),
  router = useRouter(),
  menu = ref(false);
watch(
  () => route.fullPath,
  () => {
    menu.value = false;
  },
);
watch(
  () => auth.loggedIn,
  (value) => {
    if (!value && route.meta.auth)
      router.push({ path: "/login", query: { redirect: route.fullPath } });
  },
);
</script>
<template>
  <a class="skip-link" href="#main-content">Langsung ke konten</a>
  <header class="site-header">
    <div class="shell header-inner">
      <BrandLogo /><button
        class="menu-toggle"
        :aria-expanded="menu"
        aria-controls="main-nav"
        aria-label="Buka navigasi"
        @click="menu = !menu"
      >
        <AppIcon :name="menu ? 'close' : 'menu'" />
      </button>
      <nav id="main-nav" aria-label="Navigasi utama" :class="{ open: menu }">
        <RouterLink to="/" exact-active-class="selected">Beranda</RouterLink
        ><RouterLink to="/rooms" active-class="selected">Ruangan</RouterLink
        ><RouterLink to="/my-bookings" active-class="selected"
          >Booking saya</RouterLink
        ><RouterLink
          v-if="auth.user?.role === 'admin'"
          to="/admin"
          active-class="selected"
          >Admin</RouterLink
        ><RouterLink v-if="auth.loggedIn" class="account-link" to="/profile"
          >{{ auth.user.name.split(" ")[0] }}
          <span class="avatar">{{
            auth.user.name[0].toUpperCase()
          }}</span></RouterLink
        ><RouterLink v-else class="button compact" to="/login"
          >Masuk</RouterLink
        >
      </nav>
    </div>
  </header>
  <main id="main-content" tabindex="-1"><RouterView :key="route.path" /></main>
  <footer class="site-footer">
    <div class="shell footer-grid">
      <div>
        <BrandLogo />
        <p>Tempat bertemu. Ruang bertumbuh.</p>
      </div>
      <div>
        <strong>Jam operasional</strong>
        <p>
          Senin–Sabtu, 09.00–19.00 WIB<br />Minggu dan libur nasional tutup.
        </p>
      </div>
      <div>
        <RouterLink to="/rooms">Cari ruangan</RouterLink
        ><RouterLink to="/my-bookings">Booking saya</RouterLink
        ><a href="/credits.html">Kredit fotografi</a>
      </div>
    </div>
    <div class="shell footer-end">
      <span>TechnoPark</span><span>Ruang bersama, akses untuk semua.</span>
    </div>
  </footer>
</template>
