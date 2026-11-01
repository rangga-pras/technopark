<script setup>
defineProps({
  loading: Boolean,
  error: String,
  empty: Boolean,
  emptyText: { type: String, default: "Belum ada data." },
});
defineEmits(["retry"]);
</script>
<template>
  <div v-if="loading" class="state" role="status">
    <span class="spinner"></span> Memuat data…
  </div>
  <div v-else-if="error" class="state error" role="alert">
    <p>{{ error }}</p>
    <button class="button secondary" @click="$emit('retry')">Coba lagi</button>
  </div>
  <div v-else-if="empty" class="state">
    <h2>Tidak ada hasil</h2>
    <p>{{ emptyText }}</p>
    <slot />
  </div>
</template>
