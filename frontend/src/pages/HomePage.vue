<script setup>
import { onMounted, ref } from "vue";
import { useAuthStore } from "../stores/auth";
import RoomCard from "../components/RoomCard.vue";
import RequestState from "../components/RequestState.vue";
import AppIcon from "../components/AppIcon.vue";
import { slotLabel } from "../utils";
const auth = useAuthStore(),
  rooms = ref([]),
  slots = ref([]),
  capacity = ref(""),
  loading = ref(true),
  error = ref("");
const slotsError = ref(""),
  slotsLoading = ref(true);
let generation = 0;
async function load() {
  const current = ++generation;
  loading.value = true;
  error.value = "";
  try {
    const data = await auth.api(
      `/rooms${capacity.value ? `?capacity=${capacity.value}` : ""}`,
    );
    if (current === generation) rooms.value = data.slice(0, 4);
  } catch (e) {
    if (current === generation) error.value = e.message;
  } finally {
    if (current === generation) loading.value = false;
  }
}
async function loadSlots() {
  slotsLoading.value = true;
  slotsError.value = "";
  try {
    slots.value = await auth.api("/time-slots");
  } catch (e) {
    slotsError.value = e.message;
  } finally {
    slotsLoading.value = false;
  }
}
onMounted(() => {
  load();
  loadSlots();
});
</script>
<template>
  <div class="home-intro">
    <div class="shell">
      <section class="hero-ticket" aria-labelledby="hero-title">
        <div class="hero-copy">
          <h1 id="hero-title">Ruang untuk<br />ide besarmu</h1>
          <p>
            Belajar, berdiskusi, atau kerja kelompok. Temukan workspace yang pas
            dan booking dua jam, gratis.
          </p>
          <RouterLink class="button" to="/rooms"
            >Cari ruangan <AppIcon name="arrow"
          /></RouterLink>
          <div class="hero-facts">
            <span><strong>4–8</strong> orang per ruang</span
            ><span><strong>2 jam</strong> setiap booking</span>
          </div>
        </div>
        <div class="hero-media">
          <img
            src="/images/rooms/adi-soemarmo.webp"
            alt="Ilustrasi workspace dengan meja bersama dan cahaya alami"
            width="960"
            height="640"
            fetchpriority="high"
            @error="$event.target.src = '/images/room-fallback.svg'"
          />
          <div class="hero-photo-note">Ruang untuk berpikir bersama.</div>
        </div>
        <div class="ticket-stub">
          <span><AppIcon name="clock" /> Senin–Sabtu · 09.00–19.00 WIB</span
          ><span>Tanpa biaya. Satu booking per tanggal pemakaian.</span>
        </div>
      </section>
    </div>
  </div>
  <section class="shell home-section" aria-labelledby="rooms-title">
    <div class="section-heading">
      <div>
        <h2 id="rooms-title">Temukan ruangmu</h2>
        <p>Dari diskusi kecil sampai kolaborasi satu tim.</p>
      </div>
      <RouterLink class="text-link" to="/rooms"
        >Lihat semua ruangan <AppIcon name="arrow"
      /></RouterLink>
    </div>
    <div class="chips" aria-label="Filter kapasitas">
      <button
        v-for="item in ['', 4, 6, 8]"
        :key="item"
        :aria-pressed="String(capacity) === String(item)"
        :class="{ active: String(capacity) === String(item) }"
        @click="
          capacity = item;
          load();
        "
      >
        {{ item ? `${item} orang` : "Semua" }}
      </button>
    </div>
    <RequestState
      :loading="loading"
      :error="error"
      :empty="!rooms.length"
      empty-text="Ruangan untuk kapasitas ini belum tersedia."
      @retry="load"
    />
    <div v-if="!loading && !error && rooms.length" class="room-grid home-rooms">
      <RoomCard v-for="room in rooms" :key="room.id" :room="room" />
    </div>
    <p class="photo-caption">
      Fotografi ilustratif. Kapasitas dan fasilitas mengikuti data masing-masing
      ruangan.
    </p>
  </section>
  <section class="schedule-section" aria-labelledby="schedule-title">
    <div class="shell schedule-layout">
      <div>
        <h2 id="schedule-title">
          Dua jam.<br />
          Banyak kemungkinan.
        </h2>
        <p>
          Pilih tanggal pemakaian, cari slot kosong, lalu konfirmasi. Satu akun
          mendapat satu booking per tanggal agar setiap orang punya kesempatan.
        </p>
        <RouterLink class="text-link" to="/rooms"
          >Periksa jadwal ruangan <AppIcon name="arrow"
        /></RouterLink>
      </div>
      <div class="schedule-slip">
        <h3>Jadwal harian</h3>
        <p>Senin–Sabtu, dalam WIB</p>
        <div v-for="slot in slots" :key="slot.id" class="schedule-row">
          <span>{{ slotLabel(slot) }}</span
          ><span>2 jam</span>
        </div>
        <RequestState
          :loading="slotsLoading"
          :error="slotsError"
          @retry="loadSlots"
        />
        <div class="slip-foot">Minggu & libur nasional tutup</div>
      </div>
    </div>
  </section>
  <section class="shell home-section faq-layout" aria-labelledby="faq-title">
    <h2 id="faq-title">Sebelum booking</h2>
    <div class="faq-copy">
      <p>
        <strong>Benar-benar gratis?</strong> Ya. Tidak ada pembayaran atau biaya
        keanggotaan untuk memesan ruangan TechnoPark.
      </p>
      <p>
        <strong>Harus punya akun?</strong> Anda bebas melihat ruang dan jadwal.
        Masuk atau daftar ketika akan mengonfirmasi booking.
      </p>
      <p>
        <strong>Bisa booking beberapa hari?</strong> Bisa. Anda boleh membuat
        booking untuk tanggal pemakaian berbeda pada hari yang sama.
      </p>
      <p>
        <strong>Rencana berubah?</strong> Ubah jadwal atau batalkan melalui
        Booking saya sebelum slot dimulai. Riwayat tetap tersimpan.
      </p>
    </div>
  </section>
</template>
