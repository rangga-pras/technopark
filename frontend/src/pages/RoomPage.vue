<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import RequestState from "../components/RequestState.vue";
import AppIcon from "../components/AppIcon.vue";
import { displayDate, slotLabel, todayWib } from "../utils";
const auth = useAuthStore(),
  route = useRoute(),
  router = useRouter();
const room = ref(null),
  booking = ref(null),
  loading = ref(true),
  error = ref(""),
  date = ref(route.query.date || todayWib());
const selected = ref(Number(route.query.slot) || null),
  schedule = ref(null),
  checking = ref(false),
  scheduleError = ref("");
let requestId = 0;
const editing = computed(() => Boolean(route.query.edit));
const chosen = computed(() =>
  schedule.value?.slots.find((s) => s.id === selected.value),
);
const ownSlot = (s) =>
  booking.value &&
  booking.value.usage_date === date.value &&
  booking.value.time_slot_id === s.id;
async function check() {
  const id = ++requestId;
  checking.value = true;
  scheduleError.value = "";
  schedule.value = null;
  try {
    const data = await auth.api(
      `/rooms/${route.params.id}/availability?date=${encodeURIComponent(date.value)}`,
    );
    if (id === requestId) {
      schedule.value = data;
      if (
        !data.slots.some(
          (s) => s.id === selected.value && (s.available || ownSlot(s)),
        )
      )
        selected.value = null;
    }
  } catch (e) {
    if (id === requestId) scheduleError.value = e.message;
  } finally {
    if (id === requestId) checking.value = false;
  }
}
async function load() {
  loading.value = true;
  error.value = "";
  try {
    room.value = await auth.api(`/rooms/${route.params.id}`);
    if (editing.value) {
      booking.value = await auth.api(`/bookings/${route.query.edit}`);
      if (booking.value.room_id !== room.value.id)
        throw new Error("Ruangan booking tidak sesuai.");
    }
    await check();
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
function proceed() {
  if (!chosen.value || checking.value) return;
  router.push({
    path: `/booking/${room.value.id}`,
    query: {
      date: date.value,
      slot: selected.value,
      ...(editing.value ? { edit: route.query.edit } : {}),
    },
  });
}
watch(date, () => {
  selected.value = null;
  check();
});
onMounted(load);
</script>
<template>
  <div class="shell page">
    <RouterLink class="back-link" to="/rooms">← Semua ruangan</RouterLink
    ><RequestState :loading="loading" :error="error" @retry="load" />
    <div v-if="!loading && !error && room" class="detail-layout">
      <div class="room-detail">
        <img
          class="detail-photo"
          :src="room.thumbnail"
          :alt="`Ilustrasi suasana ${room.name}`"
          width="960"
          height="640"
          @error="$event.target.src = '/images/room-fallback.svg'"
        />
        <p class="photo-caption">Fotografi ilustratif suasana workspace.</p>
        <div class="row-between">
          <h1>{{ room.name }}</h1>
          <span class="free">Gratis</span>
        </div>
        <p class="meta">
          <AppIcon name="people" /> Hingga {{ room.capacity }} orang
          <span>·</span><AppIcon name="clock" /> 2 jam per booking
        </p>
        <p class="description">{{ room.description }}</p>
        <h2>Fasilitas ruangan</h2>
        <ul class="facility-list">
          <li v-for="facility in room.facilities" :key="facility.id">
            <AppIcon name="check" />{{ facility.name }}
          </li>
        </ul>
        <h2>Ruang untuk semua</h2>
        <p>
          Satu akun dapat memiliki satu booking yang belum dibatalkan pada
          setiap tanggal pemakaian. Anda tetap boleh memesan tanggal lain.
        </p>
      </div>
      <aside class="booking-panel">
        <h2>{{ editing ? "Ubah jadwal" : "Pilih jadwal" }}</h2>
        <p class="muted">Senin–Sabtu · Waktu Indonesia Barat</p>
        <label
          >Tanggal pemakaian<input
            v-model="date"
            type="date"
            :min="todayWib()"
            required /></label
        ><RequestState
          :loading="checking"
          :error="scheduleError"
          @retry="check"
        /><template v-if="schedule && !checking"
          ><p v-if="!schedule.calendar_verified" class="notice warning">
            Kalender libur {{ date.slice(0, 4) }} belum diverifikasi pengelola.
            Booking belum dapat dilakukan.
          </p>
          <fieldset class="slot-fieldset">
            <legend>Pilih slot dua jam</legend>
            <div class="slot-grid">
              <button
                v-for="slot in schedule.slots"
                :key="slot.id"
                class="slot"
                :class="{ active: selected === slot.id }"
                :disabled="!slot.available && !ownSlot(slot)"
                :aria-pressed="selected === slot.id"
                @click="selected = slot.id"
              >
                <strong>{{ slotLabel(slot) }}</strong
                ><small>{{
                  ownSlot(slot)
                    ? "Jadwal Anda saat ini"
                    : slot.available
                      ? "Tersedia"
                      : slot.reason
                }}</small>
              </button>
            </div>
          </fieldset>
          <div v-if="chosen" class="booking-mini-summary">
            <strong>{{ displayDate(date) }}</strong
            ><span>{{ slotLabel(chosen) }} WIB · 2 jam</span>
          </div></template
        ><button
          class="button full"
          :disabled="
            !chosen ||
            checking ||
            !!scheduleError ||
            (!chosen.available && !ownSlot(chosen))
          "
          @click="proceed"
        >
          {{ editing ? "Tinjau perubahan" : "Lanjutkan booking" }}
          <AppIcon name="arrow" />
        </button>
        <p class="small muted">
          {{
            auth.loggedIn
              ? "Periksa ringkasan sebelum mengonfirmasi."
              : "Masuk atau daftar pada langkah konfirmasi."
          }}
        </p>
      </aside>
    </div>
  </div>
</template>
