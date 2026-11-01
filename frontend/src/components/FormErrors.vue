<script setup>
defineProps({ error: String, fields: { type: Array, default: () => [] } });
</script>
<template>
  <div
    v-if="error"
    id="form-errors"
    class="notice error"
    role="alert"
    tabindex="-1"
  >
    <p>{{ error }}</p>
    <ul v-if="fields.length">
      <li v-for="(field, i) in fields" :key="i">
        <a :href="`#field-${field.field}`"
          >{{ field.field || "Formulir" }}: {{ field.message }}</a
        >
      </li>
    </ul>
  </div>
</template>
