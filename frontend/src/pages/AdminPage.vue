<script setup>
import { computed, nextTick, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "../stores/auth";
import RequestState from "../components/RequestState.vue";
import FormErrors from "../components/FormErrors.vue";
import {
  displayDate,
  slotLabel,
  statusLabel,
  todayWib,
  canEdit,
} from "../utils";
const route = useRoute(),
  auth = useAuthStore();
const labels = {
  rooms: "Ruangan",
  bookings: "Booking",
  users: "Pengguna",
  facilities: "Fasilitas",
  holidays: "Hari libur",
};
const resource = computed(() => route.params.resource || ""),
  valid = computed(() => !resource.value || resource.value in labels);
const rows = ref([]),
  summary = ref(null),
  calendar = ref(null),
  rooms = ref([]),
  users = ref([]),
  facilities = ref([]),
  slots = ref([]);
const loading = ref(true),
  error = ref(""),
  formError = ref(""),
  fields = ref([]),
  editor = ref(false),
  editing = ref(null),
  busy = ref(false),
  notice = ref(""),
  removeTarget = ref(null),
  query = ref("");
const form = reactive({});
const filtered = computed(() =>
  rows.value.filter((row) =>
    [
      row.name,
      row.email,
      row.room?.name,
      row.user?.name,
      row.usage_date,
      row.holiday_date,
      row.id,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase()
      .includes(query.value.toLowerCase()),
  ),
);
async function load() {
  if (!valid.value) {
    loading.value = false;
    return;
  }
  loading.value = true;
  error.value = "";
  try {
    if (!resource.value) {
      [summary.value, rows.value, calendar.value] = await Promise.all([
        auth.api("/admin/summary"),
        auth.api("/admin/bookings"),
        auth.api("/calendar"),
      ]);
    } else {
      rows.value = await auth.api(`/admin/${resource.value}`);
      if (resource.value === "rooms")
        facilities.value = await auth.api("/admin/facilities");
      if (resource.value === "bookings")
        [rooms.value, users.value, slots.value] = await Promise.all([
          auth.api("/admin/rooms"),
          auth.api("/admin/users"),
          auth.api("/time-slots"),
        ]);
      if (resource.value === "holidays")
        calendar.value = await auth.api("/calendar");
    }
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
async function openForm(item = null) {
  editing.value = item;
  editor.value = true;
  removeTarget.value = null;
  formError.value = "";
  fields.value = [];
  notice.value = "";
  for (const key of Object.keys(form)) delete form[key];
  if (resource.value === "rooms")
    Object.assign(
      form,
      item
        ? {
            name: item.name,
            capacity: item.capacity,
            description: item.description,
            thumbnail: item.thumbnail,
            is_active: item.is_active,
            facility_ids: item.facilities.map((f) => f.id),
          }
        : {
            name: "",
            capacity: 4,
            description: "",
            thumbnail: "/images/rooms/adi-soemarmo.webp",
            is_active: true,
            facility_ids: [],
          },
    );
  if (resource.value === "users")
    Object.assign(form, {
      name: item?.name || "",
      email: item?.email || "",
      role: item?.role || "user",
      is_active: item?.is_active ?? true,
      password: "",
      confirm_password: "",
    });
  if (resource.value === "facilities")
    Object.assign(form, { name: item?.name || "" });
  if (resource.value === "holidays")
    Object.assign(form, {
      holiday_date: item?.holiday_date || "",
      name: item?.name || "",
    });
  if (resource.value === "bookings")
    Object.assign(form, {
      user_id: item?.user_id || "",
      room_id: item?.room_id || "",
      usage_date: item?.usage_date || todayWib(),
      time_slot_id: item?.time_slot_id || "",
    });
  await nextTick();
  document.querySelector("#editor-heading")?.focus();
}
const keyOf = (item) =>
  resource.value === "holidays" ? item.holiday_date : item.id;
const fieldError = (key) => fields.value.find((f) => f.field === key)?.message;
async function save() {
  busy.value = true;
  formError.value = "";
  fields.value = [];
  try {
    const body = { ...form };
    if (resource.value === "users" && editing.value) {
      delete body.confirm_password;
      if (!body.password) delete body.password;
    }
    if (resource.value === "bookings" && editing.value) delete body.user_id;
    await auth.api(
      `/admin/${resource.value}${editing.value ? `/${keyOf(editing.value)}` : ""}`,
      { method: editing.value ? "PATCH" : "POST", body },
    );
    editor.value = false;
    notice.value = "Perubahan berhasil disimpan.";
    await load();
  } catch (e) {
    formError.value = e.message;
    fields.value = e.fields || [];
    await nextTick();
    document.querySelector("#form-errors")?.focus();
  } finally {
    busy.value = false;
  }
}
async function remove() {
  busy.value = true;
  formError.value = "";
  try {
    const result = await auth.api(
      `/admin/${resource.value}/${keyOf(removeTarget.value)}`,
      { method: "DELETE" },
    );
    removeTarget.value = null;
    notice.value = result.message || "Booking berhasil dibatalkan.";
    await load();
  } catch (e) {
    formError.value = e.message;
  } finally {
    busy.value = false;
  }
}
const actionName = computed(
  () =>
    ({
      rooms: "Arsipkan",
      users: "Nonaktifkan",
      bookings: "Batalkan",
      facilities: "Hapus",
      holidays: "Hapus",
    })[resource.value],
);
onMounted(load);
</script>
<template>
  <div class="shell page admin-shell">
    <aside class="admin-nav">
      <strong>Pengelolaan</strong>
      <nav aria-label="Navigasi admin">
        <RouterLink to="/admin" exact-active-class="selected"
          >Ringkasan</RouterLink
        ><RouterLink
          v-for="(label, key) in labels"
          :key="key"
          :to="`/admin/${key}`"
          active-class="selected"
          >{{ label }}</RouterLink
        >
      </nav>
      <p class="small muted">TechnoPark<br />Operasional workspace</p>
    </aside>
    <div class="admin-content">
      <div class="section-heading">
        <div>
          <h1>
            {{
              resource
                ? labels[resource] || "Halaman tidak ditemukan"
                : "Ringkasan operasional"
            }}
          </h1>
          <p>
            {{
              resource
                ? "Kelola data TechnoPark dengan riwayat yang tetap terjaga."
                : `Halo, ${auth.user.name}. Tinjau rencana ruang berikutnya.`
            }}
          </p>
        </div>
        <button v-if="resource && valid" class="button" @click="openForm()">
          Tambah {{ labels[resource].toLowerCase() }}
        </button>
      </div>
      <RequestState :loading="loading" :error="error" @retry="load" />
      <p v-if="notice" class="notice success" role="status">{{ notice }}</p>
      <template v-if="!loading && !error && valid"
        ><template v-if="!resource && summary"
          ><div class="metrics">
            <div
              v-for="(label, key) in {
                active_rooms: 'Ruang aktif',
                active_users: 'Akun aktif',
                upcoming: 'Booking mendatang',
                cancelled: 'Dibatalkan',
              }"
              :key="key"
            >
              <span>{{ label }}</span
              ><strong>{{ summary[key] }}</strong>
            </div>
          </div>
          <p v-if="summary.operational_conflicts" class="notice warning">
            {{ summary.operational_conflicts }} booking perlu ditinjau karena
            perubahan operasional. Booking tetap tersimpan.
          </p>
          <div class="admin-overview-grid">
            <section>
              <div class="row-between">
                <h2>Booking mendatang</h2>
                <RouterLink to="/admin/bookings">Lihat semua</RouterLink>
              </div>
              <article
                v-for="b in rows
                  .filter((b) => b.status === 'upcoming')
                  .slice(0, 5)"
                :key="b.id"
                class="overview-row"
              >
                <strong>{{ b.room.name }}</strong
                ><span
                  >{{ displayDate(b.usage_date) }}<br />{{
                    slotLabel(b.time_slot)
                  }}
                  · {{ b.user.name }}</span
                >
              </article>
              <p
                v-if="!rows.some((b) => b.status === 'upcoming')"
                class="state"
              >
                Belum ada booking mendatang.
              </p>
            </section>
            <section class="calendar-summary">
              <h2>Kalender operasional</h2>
              <p v-if="calendar?.verified_years.length">
                Tahun terverifikasi: {{ calendar.verified_years.join(", ") }}
              </p>
              <p v-else>
                Belum ada tahun kalender terverifikasi. Booking ditutup sampai
                daftar hari libur nasional diaudit.
              </p>
              <RouterLink class="text-link" to="/admin/holidays"
                >Kelola hari libur</RouterLink
              >
            </section>
          </div></template
        ><template v-else-if="resource"
          ><div v-if="resource === 'holidays'" class="notice">
            <strong
              >Cakupan kalender:
              {{
                calendar?.verified_years.length
                  ? calendar.verified_years.join(", ")
                  : "belum ada tahun terverifikasi"
              }}</strong
            >
            <p>
              Masukkan seluruh libur nasional dari sumber pemerintah. Setelah
              diaudit, operator deployment menetapkan tahun dan URL sumber pada
              konfigurasi HOLIDAY_CALENDARS. Perubahan hari libur dapat
              memengaruhi booking yang sudah ada; tinjau konflik di ringkasan.
            </p>
          </div>
          <section v-if="editor" class="editor-panel">
            <div class="row-between">
              <h2 id="editor-heading" tabindex="-1">
                {{ editing ? "Edit" : "Tambah" }}
                {{ labels[resource].toLowerCase() }}
              </h2>
              <button
                class="text-button"
                :disabled="busy"
                @click="editor = false"
              >
                Tutup form
              </button>
            </div>
            <FormErrors :error="formError" :fields="fields" />
            <form class="admin-form" @submit.prevent="save">
              <template
                v-if="
                  ['rooms', 'users', 'facilities', 'holidays'].includes(
                    resource,
                  )
                "
                ><label for="field-name"
                  >{{ resource === "holidays" ? "Nama hari libur" : "Nama"
                  }}<input
                    id="field-name"
                    v-model.trim="form.name"
                    required
                    minlength="2"
                    :maxlength="
                      resource === 'holidays'
                        ? 150
                        : resource === 'facilities'
                          ? 80
                          : 100
                    "
                    :aria-invalid="!!fieldError('name')"
                  /><small v-if="fieldError('name')" class="field-error">{{
                    fieldError("name")
                  }}</small></label
                ></template
              ><template v-if="resource === 'rooms'"
                ><label for="field-capacity"
                  >Kapasitas orang<input
                    id="field-capacity"
                    v-model.number="form.capacity"
                    type="number"
                    min="1"
                    max="100"
                    required
                  /><small
                    >Nama dan kapasitas sembilan ruang bawaan dilindungi.</small
                  ></label
                ><label class="form-wide" for="field-description"
                  >Deskripsi<textarea
                    id="field-description"
                    v-model="form.description"
                    minlength="10"
                    maxlength="3000"
                    rows="3"
                    required
                  /></label
                ><label for="field-thumbnail"
                  >Foto ilustratif<select
                    aria-label="Foto ilustratif"
                    id="field-thumbnail"
                    v-model="form.thumbnail"
                  >
                    <option
                      v-for="slug in [
                        'adi-soemarmo',
                        'balapan',
                        'jebres',
                        'tirtonadi',
                        'purwosari',
                        'solo-kota',
                        'batik-solo-trans',
                        'kerten',
                        'kleco',
                      ]"
                      :key="slug"
                      :value="`/images/rooms/${slug}.webp`"
                    >
                      {{ slug.replaceAll("-", " ") }}
                    </option>
                  </select></label
                >
                <fieldset class="form-wide facility-checks">
                  <legend>Fasilitas</legend>
                  <label
                    v-for="f in facilities"
                    :key="f.id"
                    class="checkbox-label"
                    ><input
                      v-model="form.facility_ids"
                      type="checkbox"
                      :value="f.id"
                    />{{ f.name }}</label
                  >
                </fieldset></template
              ><template v-if="resource === 'users'"
                ><label for="field-email"
                  >Email<input
                    id="field-email"
                    v-model.trim="form.email"
                    type="email"
                    autocomplete="off"
                    maxlength="254"
                    required
                  /><small v-if="fieldError('email')" class="field-error">{{
                    fieldError("email")
                  }}</small></label
                ><label for="field-role"
                  >Peran<select
                    aria-label="Peran"
                    id="field-role"
                    v-model="form.role"
                  >
                    <option value="user">Pengguna</option>
                    <option value="admin">Admin</option>
                  </select></label
                ><label for="field-password"
                  >{{ editing ? "Kata sandi baru (opsional)" : "Kata sandi"
                  }}<input
                    :aria-label="
                      editing ? 'Kata sandi baru (opsional)' : 'Kata sandi'
                    "
                    id="field-password"
                    v-model="form.password"
                    type="password"
                    autocomplete="new-password"
                    minlength="8"
                    maxlength="72"
                    :required="!editing"
                  /><small
                    >8 karakter atau lebih, maksimal 72 byte.</small
                  ></label
                ><label v-if="!editing" for="field-confirm_password"
                  >Ulangi kata sandi<input
                    id="field-confirm_password"
                    v-model="form.confirm_password"
                    type="password"
                    autocomplete="new-password"
                    required /></label></template
              ><label
                v-if="['users', 'rooms'].includes(resource)"
                class="checkbox-label"
                ><input v-model="form.is_active" type="checkbox" />{{
                  resource === "users" ? "Akun aktif" : "Ruangan beroperasi"
                }}</label
              ><label v-if="resource === 'holidays'" for="field-holiday_date"
                >Tanggal libur<input
                  id="field-holiday_date"
                  v-model="form.holiday_date"
                  type="date"
                  required /></label
              ><template v-if="resource === 'bookings'"
                ><label for="field-user_id"
                  >Pemesan<select
                    aria-label="Pemesan"
                    id="field-user_id"
                    v-model.number="form.user_id"
                    :disabled="!!editing"
                    required
                  >
                    <option value="" disabled>Pilih pengguna</option>
                    <option
                      v-for="u in users.filter(
                        (u) => u.is_active || u.id === form.user_id,
                      )"
                      :key="u.id"
                      :value="u.id"
                    >
                      {{ u.name }} · {{ u.email }}
                    </option>
                  </select></label
                ><label for="field-room_id"
                  >Ruangan<select
                    aria-label="Ruangan"
                    id="field-room_id"
                    v-model.number="form.room_id"
                    required
                  >
                    <option value="" disabled>Pilih ruangan</option>
                    <option
                      v-for="r in rooms.filter(
                        (r) => r.is_active || r.id === form.room_id,
                      )"
                      :key="r.id"
                      :value="r.id"
                    >
                      {{ r.name }} · {{ r.capacity }} orang
                    </option>
                  </select></label
                ><label for="field-usage_date"
                  >Tanggal pemakaian<input
                    id="field-usage_date"
                    v-model="form.usage_date"
                    type="date"
                    :min="todayWib()"
                    required /></label
                ><label for="field-time_slot_id"
                  >Slot WIB<select
                    aria-label="Slot WIB"
                    id="field-time_slot_id"
                    v-model.number="form.time_slot_id"
                    required
                  >
                    <option value="" disabled>Pilih slot</option>
                    <option v-for="s in slots" :key="s.id" :value="s.id">
                      {{ slotLabel(s) }}
                    </option>
                  </select></label
                >
                <p class="small muted form-wide">
                  Aturan satu booking per tanggal dan konflik slot tetap
                  diperiksa saat menyimpan.
                </p></template
              >
              <div class="actions form-wide">
                <button class="button" :disabled="busy">
                  {{ busy ? "Menyimpan…" : "Simpan" }}</button
                ><button
                  type="button"
                  class="button secondary"
                  :disabled="busy"
                  @click="editor = false"
                >
                  Batal
                </button>
              </div>
            </form>
          </section>
          <section v-if="removeTarget" class="cancel-confirm">
            <h2>
              {{ actionName }}
              {{ removeTarget.name || removeTarget.room?.name || "data ini" }}?
            </h2>
            <p>
              {{
                ["users", "rooms", "bookings"].includes(resource)
                  ? "Riwayat booking akan tetap tersimpan."
                  : "Periksa kembali sebelum melanjutkan."
              }}
            </p>
            <FormErrors :error="formError" />
            <div class="actions">
              <button class="button danger" :disabled="busy" @click="remove">
                {{
                  busy ? "Memproses…" : `Ya, ${actionName.toLowerCase()}`
                }}</button
              ><button
                class="button secondary"
                :disabled="busy"
                @click="removeTarget = null"
              >
                Batal
              </button>
            </div>
          </section>
          <div class="list-tools">
            <label
              >Cari {{ labels[resource].toLowerCase()
              }}<input
                v-model="query"
                type="search"
                placeholder="Nama, tanggal, atau ID" /></label
            ><span class="muted" role="status">{{ filtered.length }} data</span>
          </div>
          <div class="admin-table-wrap">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>
                    {{
                      resource === "bookings"
                        ? "Ruangan / pemesan"
                        : resource === "holidays"
                          ? "Hari libur"
                          : "Nama"
                    }}
                  </th>
                  <th>
                    {{
                      resource === "rooms"
                        ? "Kapasitas / fasilitas"
                        : resource === "bookings"
                          ? "Jadwal WIB"
                          : resource === "users"
                            ? "Email / peran"
                            : "Identitas"
                    }}
                  </th>
                  <th v-if="['users', 'rooms', 'bookings'].includes(resource)">
                    Status
                  </th>
                  <th>Aksi</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in filtered" :key="keyOf(row)">
                  <td>
                    <strong>{{ row.name || row.room?.name }}</strong
                    ><small v-if="resource === 'bookings'"
                      >{{ row.user.name }} · {{ row.user.email }}</small
                    ><small v-if="resource === 'rooms'">{{
                      row.description
                    }}</small>
                  </td>
                  <td>
                    <template v-if="resource === 'rooms'"
                      >{{ row.capacity }} orang<small>{{
                        row.facilities.map((f) => f.name).join(", ")
                      }}</small></template
                    ><template v-else-if="resource === 'bookings'"
                      >{{ displayDate(row.usage_date)
                      }}<small>{{ slotLabel(row.time_slot) }}</small>
                      <p
                        v-for="conflict in row.operational_conflicts"
                        :key="conflict"
                        class="field-error"
                      >
                        {{ conflict }}
                      </p></template
                    ><template v-else-if="resource === 'users'"
                      >{{ row.email
                      }}<small>{{
                        row.role === "admin" ? "Admin" : "Pengguna"
                      }}</small></template
                    ><template v-else>{{
                      resource === "holidays"
                        ? displayDate(row.holiday_date)
                        : `#${row.id}`
                    }}</template>
                  </td>
                  <td v-if="['users', 'rooms', 'bookings'].includes(resource)">
                    <span
                      class="status-pill"
                      :class="
                        resource === 'bookings'
                          ? row.status
                          : row.is_active
                            ? 'upcoming'
                            : 'cancelled'
                      "
                      >{{
                        resource === "bookings"
                          ? statusLabel(row.status)
                          : row.is_active
                            ? "Aktif"
                            : "Nonaktif"
                      }}</span
                    >
                  </td>
                  <td>
                    <div class="table-actions">
                      <button
                        class="text-button"
                        :disabled="resource === 'bookings' && !canEdit(row)"
                        @click="openForm(row)"
                      >
                        Edit</button
                      ><button
                        class="text-button danger-text"
                        :disabled="resource === 'bookings' && !canEdit(row)"
                        @click="
                          removeTarget = row;
                          editor = false;
                          formError = '';
                        "
                      >
                        {{ actionName }}
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="!filtered.length">
                  <td
                    :colspan="
                      ['users', 'rooms', 'bookings'].includes(resource) ? 4 : 3
                    "
                  >
                    Belum ada data yang cocok.
                  </td>
                </tr>
              </tbody>
            </table>
          </div></template
        ></template
      ><RouterLink v-if="!valid" class="button" to="/admin"
        >Kembali ke ringkasan</RouterLink
      >
    </div>
  </div>
</template>
