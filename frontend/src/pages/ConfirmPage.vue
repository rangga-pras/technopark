<script setup>
import { onMounted, ref, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import RequestState from "../components/RequestState.vue";
import FormErrors from "../components/FormErrors.vue";
import { displayDate, slotLabel } from "../utils";
const auth = useAuthStore(),
  route = useRoute(),
  router = useRouter();
const room = ref(null),
  slot = ref(null),
  loading = ref(true),
  error = ref(""),
  fields = ref([]),
  agreed = ref(false),
  busy = ref(false);
async function load() {
  loading.value = true;
  error.value = "";
  try {
    room.value = await auth.api(`/rooms/${route.params.roomId}`);
    slot.value = (await auth.api("/time-slots")).find(
      (s) => s.id === Number(route.query.slot),
    );
    if (!slot.value || !/^\d{4}-\d{2}-\d{2}$/.test(route.query.date || ""))
      throw new Error(
        "Jadwal belum lengkap. Kembali ke detail ruangan untuk memilih tanggal dan slot.",
      );
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
async function confirm() {
  if (!agreed.value) return;
  busy.value = true;
  error.value = "";
  fields.value = [];
  try {
    const result = await auth.api(
      route.query.edit ? `/bookings/${route.query.edit}` : "/bookings",
      {
        method: route.query.edit ? "PATCH" : "POST",
        body: {
          room_id: room.value.id,
          usage_date: route.query.date,
          time_slot_id: slot.value.id,
        },
      },
    );
    router.replace({ path: "/booking/success", query: { id: result.id } });
  } catch (e) {
    error.value = e.message;
    fields.value = e.fields || [];
    await nextTick();
    document.querySelector("#form-errors")?.focus();
  } finally {
    busy.value = false;
  }
}
onMounted(load);
</script>
<template>
  <div class="shell page narrow">
    <h1>{{ route.query.edit ? "Tinjau perubahan" : "Konfirmasi booking" }}</h1>
    <p>Pastikan ruangan dan jadwal sudah sesuai rencana.</p>
    <RequestState
      :loading="loading"
      :error="!room || !slot ? error : ''"
      @retry="load"
    />
    <section v-if="room && slot" class="confirm-card">
      <img
        :src="room.thumbnail"
        :alt="`Ilustrasi ${room.name}`"
        width="960"
        height="640"
        @error="$event.target.src = '/images/room-fallback.svg'"
      />
      <div class="panel">
        <h2>{{ room.name }}</h2>
        <dl class="summary-list">
          <div>
            <dt>Tanggal pemakaian</dt>
            <dd>{{ displayDate(route.query.date) }}</dd>
          </div>
          <div>
            <dt>Waktu</dt>
            <dd>{{ slotLabel(slot) }} WIB</dd>
          </div>
          <div>
            <dt>Durasi</dt>
            <dd>2 jam</dd>
          </div>
          <div>
            <dt>Pemesan</dt>
            <dd>{{ auth.user.name }}</dd>
          </div>
          <div>
            <dt>Biaya</dt>
            <dd class="free">Gratis</dd>
          </div>
        </dl>
        <FormErrors :error="error" :fields="fields" />
        <form @submit.prevent="confirm">
          <label class="checkbox-label"
            ><input v-model="agreed" type="checkbox" required />Saya memahami
            batas satu booking per tanggal pemakaian dan akan menggunakan
            ruangan sesuai jadwal.</label
          ><button class="button full" :disabled="busy || !agreed">
            {{
              busy
                ? "Menyimpan booking…"
                : route.query.edit
                  ? "Simpan perubahan"
                  : "Konfirmasi booking"
            }}
          </button>
        </form>
        <RouterLink
          class="back-link"
          :to="{ path: `/rooms/${room.id}`, query: route.query }"
          >Kembali ke jadwal</RouterLink
        >
      </div>
    </section>
  </div>
</template>
