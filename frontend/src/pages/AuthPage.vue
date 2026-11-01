<script setup>
import { computed, nextTick, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import FormErrors from "../components/FormErrors.vue";
import { safeRedirect } from "../utils";
const route = useRoute(),
  router = useRouter(),
  auth = useAuthStore();
const register = computed(() => route.path === "/register"),
  busy = ref(false),
  error = ref(""),
  fields = ref([]),
  visible = ref(false),
  recovery = ref(Boolean(route.query.recovery));
const form = reactive({
  name: "",
  email: "",
  password: "",
  confirm_password: "",
});
const fieldError = (key) => fields.value.find((f) => f.field === key)?.message;
async function submit() {
  busy.value = true;
  error.value = "";
  fields.value = [];
  try {
    if (register.value)
      await auth.api("/auth/register", { method: "POST", body: form });
    await auth.login(form.email, form.password);
    form.password = "";
    form.confirm_password = "";
    router.replace(safeRedirect(route.query.redirect));
  } catch (e) {
    error.value = e.message;
    fields.value = e.fields || [];
    await nextTick();
    document.querySelector("#form-errors")?.focus();
  } finally {
    busy.value = false;
  }
}
</script>
<template>
  <div class="shell page auth-layout">
    <div class="auth-story">
      <img
        src="/images/room-fallback.svg"
        width="960"
        height="640"
        alt="Ilustrasi meja kerja dengan monitor, jendela, dan kursi"
      />
      <h2>Ide bagus dimulai<br />dari ruang yang pas.</h2>
      <p>Temukan tempat untuk belajar, bertemu, dan bertumbuh bersama.</p>
      <div class="auth-hours">
        <strong>Jam operasional</strong>
        <p>
          Senin–Sabtu, 09.00–19.00 WIB.<br />Minggu dan libur nasional tutup.
        </p>
      </div>
    </div>
    <div class="auth-form">
      <RouterLink class="back-link" to="/rooms"
        >← Kembali ke ruangan</RouterLink
      >
      <h1>{{ register ? "Buat akun Anda" : "Masuk ke TechnoPark" }}</h1>
      <p>
        {{
          register
            ? "Satu akun, banyak kesempatan bertemu."
            : "Lanjutkan rencana baik Anda hari ini."
        }}
      </p>
      <FormErrors :error="error" :fields="fields" />
      <form @submit.prevent="submit">
        <label v-if="register" for="field-name"
          >Nama lengkap<input
            id="field-name"
            v-model.trim="form.name"
            autocomplete="name"
            minlength="2"
            maxlength="100"
            required
            :aria-invalid="!!fieldError('name')"
            aria-describedby="error-name"
          /><small
            v-if="fieldError('name')"
            id="error-name"
            class="field-error"
            >{{ fieldError("name") }}</small
          ></label
        ><label for="field-email"
          >Email<input
            id="field-email"
            v-model.trim="form.email"
            type="email"
            autocomplete="username"
            maxlength="254"
            required
            :aria-invalid="!!fieldError('email')"
            aria-describedby="error-email"
          /><small
            v-if="fieldError('email')"
            id="error-email"
            class="field-error"
            >{{ fieldError("email") }}</small
          ></label
        ><label for="field-password"
          ><span id="password-label">Kata sandi</span>
          <div class="password-field">
            <input
              aria-labelledby="password-label"
              id="field-password"
              v-model="form.password"
              :type="visible ? 'text' : 'password'"
              :autocomplete="register ? 'new-password' : 'current-password'"
              :minlength="register ? 8 : 1"
              maxlength="72"
              required
              :aria-invalid="!!fieldError('password')"
              aria-describedby="password-help error-password"
            /><button
              type="button"
              :aria-pressed="visible"
              @click="visible = !visible"
            >
              {{ visible ? "Sembunyikan" : "Lihat" }}
            </button>
          </div>
          <small id="password-help">{{
            register
              ? "Minimal 8 karakter, maksimal 72 byte UTF-8."
              : "Gunakan kata sandi akun Anda."
          }}</small
          ><small
            v-if="fieldError('password')"
            id="error-password"
            class="field-error"
            >{{ fieldError("password") }}</small
          ></label
        ><label v-if="register" for="field-confirm_password"
          >Ulangi kata sandi<input
            id="field-confirm_password"
            v-model="form.confirm_password"
            :type="visible ? 'text' : 'password'"
            autocomplete="new-password"
            required /></label
        ><button
          v-if="!register"
          type="button"
          class="text-button forgot"
          @click="recovery = !recovery"
        >
          Lupa kata sandi?
        </button>
        <div v-if="recovery && !register" class="notice">
          Hubungi pengelola TechnoPark untuk penggantian kata sandi. Pemulihan
          melalui email belum tersedia.
        </div>
        <button class="button full" :disabled="busy">
          {{ busy ? "Memproses…" : register ? "Daftar & masuk" : "Masuk" }}
        </button>
      </form>
      <p class="auth-switch">
        {{ register ? "Sudah punya akun?" : "Belum punya akun?" }}
        <RouterLink
          :to="{ path: register ? '/login' : '/register', query: route.query }"
          >{{ register ? "Masuk" : "Daftar gratis" }}</RouterLink
        >
      </p>
      <p class="small muted">
        Sesi disimpan selama halaman terbuka. Setelah refresh, silakan masuk
        kembali.
      </p>
    </div>
  </div>
</template>
