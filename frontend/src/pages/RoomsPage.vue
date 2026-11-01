<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import RoomCard from "../components/RoomCard.vue";
import RequestState from "../components/RequestState.vue";
import AppIcon from "../components/AppIcon.vue";
import { todayWib } from "../utils";
const auth = useAuthStore(),
  route = useRoute(),
  router = useRouter();
const rooms = ref([]),
  q = ref(route.query.q || ""),
  capacity = ref(route.query.capacity || ""),
  date = ref(route.query.date || todayWib());
const loading = ref(true),
  error = ref(""),
  availability = ref({}),
  checking = ref(false);
let loadId = 0;
const filtered = computed(() =>
  rooms.value.filter(
    (r) =>
      (!capacity.value || r.capacity === Number(capacity.value)) &&
      `${r.name} ${r.capacity}`
        .toLowerCase()
        .includes(q.value.toLowerCase().trim()),
  ),
);
function syncUrl() {
  router.replace({
    query: {
      ...(q.value ? { q: q.value } : {}),
      ...(capacity.value ? { capacity: capacity.value } : {}),
      date: date.value,
    },
  });
}
async function check() {
  const current = ++loadId;
  availability.value = {};
  checking.value = true;
  await Promise.all(
    rooms.value.map(async (r) => {
      try {
        const data = await auth.api(
          `/rooms/${r.id}/availability?date=${encodeURIComponent(date.value)}`,
        );
        if (current === loadId) availability.value[r.id] = data;
      } catch (e) {
        if (current === loadId) availability.value[r.id] = { error: e.message };
      }
    }),
  );
  if (current === loadId) checking.value = false;
}
async function load() {
  loading.value = true;
  error.value = "";
  try {
    rooms.value = await auth.api("/rooms");
    await check();
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
function availabilityText(id) {
  const a = availability.value[id];
  if (!a) return "Memeriksa jadwal…";
  if (a.error) return a.error;
  if (!a.calendar_verified) return "Kalender tahun ini belum siap";
  const count = a.slots.filter((s) => s.available).length;
  return count
    ? `${count} slot tersedia`
    : a.slots[0]?.reason || "Tidak ada slot tersedia";
}
watch([q, capacity], syncUrl);
watch(date, () => {
  syncUrl();
  check();
});
onMounted(load);
</script>
<template>
  <div class="shell page">
    <div class="page-heading">
      <h1>Cari ruangan</h1>
      <p>Ruang yang pas untuk orang-orang dan ide-ide Anda.</p>
    </div>
    <form class="catalog-filters" @submit.prevent="syncUrl">
      <label class="search-field"
        ><span>Cari nama atau kapasitas</span>
        <div class="input-icon">
          <AppIcon name="search" /><input
            v-model="q"
            type="search"
            maxlength="100"
            placeholder="Misalnya: Balapan atau 6"
          /></div></label
      ><label
        >Tanggal pemakaian<input
          v-model="date"
          type="date"
          :min="todayWib()"
          required
      /></label>
    </form>
    <div class="row-between filter-row">
      <div class="chips" aria-label="Kapasitas ruang">
        <button
          v-for="item in ['', 4, 6, 8]"
          :key="item"
          :class="{ active: String(capacity) === String(item) }"
          :aria-pressed="String(capacity) === String(item)"
          @click="capacity = item"
        >
          {{ item ? `${item} orang` : "Semua" }}
        </button>
      </div>
      <span class="muted" role="status">{{ filtered.length }} ruangan</span>
    </div>
    <RequestState
      :loading="loading"
      :error="error"
      :empty="!filtered.length"
      empty-text="Coba kata kunci atau kapasitas lain."
      @retry="load"
      ><button
        class="button secondary"
        @click="
          q = '';
          capacity = '';
        "
      >
        Hapus filter
      </button></RequestState
    >
    <div v-if="!loading && !error && filtered.length" class="room-grid">
      <div v-for="room in filtered" :key="room.id">
        <RoomCard :room="room" />
        <div class="availability-note">
          <span>{{ availabilityText(room.id) }}</span
          ><RouterLink :to="{ path: `/rooms/${room.id}`, query: { date } }"
            >Pilih slot</RouterLink
          ><button
            v-if="availability[room.id]?.error"
            class="text-button"
            @click="check"
            :disabled="checking"
          >
            Coba lagi
          </button>
        </div>
      </div>
    </div>
    <p class="photo-caption">
      Foto merupakan ilustrasi suasana; fasilitas dan kapasitas tercantum sesuai
      data ruangan.
    </p>
  </div>
</template>
