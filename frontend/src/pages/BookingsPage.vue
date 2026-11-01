<script setup>
import { computed, onMounted, ref } from "vue";
import { useAuthStore } from "../stores/auth";
import RequestState from "../components/RequestState.vue";
import { canEdit, displayDate, slotLabel, statusLabel } from "../utils";
const auth = useAuthStore(),
  bookings = ref([]),
  tab = ref("upcoming"),
  loading = ref(true),
  error = ref(""),
  actionError = ref(""),
  cancelling = ref(null),
  busy = ref(false);
const filtered = computed(() =>
  bookings.value.filter((b) => b.status === tab.value),
);
async function load() {
  loading.value = true;
  error.value = "";
  try {
    bookings.value = await auth.api("/bookings/me");
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
async function cancel() {
  busy.value = true;
  actionError.value = "";
  try {
    await auth.api(`/bookings/${cancelling.value.id}`, { method: "DELETE" });
    cancelling.value = null;
    await load();
  } catch (e) {
    actionError.value = e.message;
  } finally {
    busy.value = false;
  }
}
onMounted(load);
</script>
<template>
  <div class="shell page">
    <div class="section-heading">
      <div>
        <h1>Booking saya</h1>
        <p>Rencana pertemuan dan riwayat ruang Anda.</p>
      </div>
      <RouterLink class="button" to="/rooms">Cari ruangan</RouterLink>
    </div>
    <div class="tabs" aria-label="Status booking">
      <button
        v-for="status in ['upcoming', 'completed', 'cancelled']"
        :key="status"
        :class="{ active: tab === status }"
        :aria-pressed="tab === status"
        @click="tab = status"
      >
        {{ statusLabel(status) }}
        <span>{{ bookings.filter((b) => b.status === status).length }}</span>
      </button>
    </div>
    <RequestState
      :loading="loading"
      :error="error"
      :empty="!filtered.length"
      :empty-text="`Belum ada booking ${statusLabel(tab).toLowerCase()}.`"
      @retry="load"
      ><RouterLink to="/rooms" class="text-link"
        >Jelajahi ruangan</RouterLink
      ></RequestState
    >
    <p v-if="actionError" role="alert" class="notice error">
      {{ actionError }}
    </p>
    <div
      v-if="cancelling"
      class="cancel-confirm"
      role="region"
      aria-label="Konfirmasi pembatalan"
    >
      <h2>Batalkan {{ cancelling.room.name }}?</h2>
      <p>
        {{ displayDate(cancelling.usage_date) }},
        {{ slotLabel(cancelling.time_slot) }} WIB. Slot akan tersedia kembali
        untuk pengguna lain.
      </p>
      <div class="actions">
        <button class="button danger" :disabled="busy" @click="cancel">
          {{ busy ? "Membatalkan…" : "Ya, batalkan" }}</button
        ><button
          class="button secondary"
          :disabled="busy"
          @click="cancelling = null"
        >
          Tetap gunakan
        </button>
      </div>
    </div>
    <div v-if="!loading && !error" class="booking-list">
      <article v-for="b in filtered" :key="b.id" class="booking-card">
        <img
          :src="b.room.thumbnail"
          :alt="`Ilustrasi ${b.room.name}`"
          width="240"
          height="160"
          @error="$event.target.src = '/images/room-fallback.svg'"
        />
        <div class="booking-card-main">
          <span class="status-pill" :class="b.status">{{
            statusLabel(b.status)
          }}</span>
          <h2>{{ b.room.name }}</h2>
          <p>
            {{ displayDate(b.usage_date) }}<br />{{
              slotLabel(b.time_slot)
            }}
            WIB · 2 jam · Gratis
          </p>
          <p
            v-for="conflict in b.operational_conflicts"
            :key="conflict"
            class="notice warning"
          >
            {{ conflict }}
          </p>
          <small class="muted">Booking #{{ b.id }}</small>
        </div>
        <div v-if="canEdit(b)" class="booking-actions">
          <RouterLink
            class="button secondary"
            :to="{
              path: `/rooms/${b.room_id}`,
              query: { edit: b.id, date: b.usage_date, slot: b.time_slot_id },
            }"
            >Ubah jadwal</RouterLink
          ><button
            class="text-button danger-text"
            @click="
              cancelling = b;
              actionError = '';
            "
          >
            Batalkan booking
          </button>
        </div>
      </article>
    </div>
  </div>
</template>
