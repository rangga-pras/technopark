<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "../stores/auth";
import RequestState from "../components/RequestState.vue";
import AppIcon from "../components/AppIcon.vue";
import { displayDate, slotLabel } from "../utils";
const auth = useAuthStore(),
  route = useRoute(),
  booking = ref(null),
  loading = ref(true),
  error = ref("");
async function load() {
  loading.value = true;
  error.value = "";
  try {
    if (!route.query.id)
      throw new Error("Pilih booking dari riwayat untuk melihat detail.");
    booking.value = await auth.api(`/bookings/${route.query.id}`);
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
onMounted(load);
</script>
<template>
  <div class="shell page narrow">
    <RequestState :loading="loading" :error="error" @retry="load" />
    <section v-if="booking" class="success-panel">
      <span class="success-mark"><AppIcon name="check" /></span>
      <h1>Booking tersimpan</h1>
      <p>Jadwal Anda sudah tercatat di TechnoPark.</p>
      <div class="confirmation-ticket">
        <span class="muted">Booking #{{ booking.id }}</span>
        <h2>{{ booking.room.name }}</h2>
        <p>
          {{ displayDate(booking.usage_date) }}<br />{{
            slotLabel(booking.time_slot)
          }}
          WIB · 2 jam
        </p>
        <strong>Gratis</strong>
      </div>
      <RouterLink class="button" to="/my-bookings"
        >Lihat booking saya</RouterLink
      ><RouterLink class="back-link" to="/rooms"
        >Cari ruangan untuk hari lain</RouterLink
      >
    </section>
  </div>
</template>
