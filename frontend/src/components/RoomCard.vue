<script setup>
import AppIcon from "./AppIcon.vue";
defineProps({ room: Object });
</script>
<template>
  <article class="room-card">
    <RouterLink
      :to="`/rooms/${room.id}`"
      class="room-image-link"
      :aria-label="`Lihat ${room.name}`"
      ><img
        :src="room.thumbnail"
        :alt="`Ilustrasi suasana ${room.name}`"
        loading="lazy"
        width="960"
        height="640"
        @error="$event.target.src = '/images/room-fallback.svg'"
    /></RouterLink>
    <div class="room-card-body">
      <div class="row-between">
        <span class="meta"
          ><AppIcon name="people" /> {{ room.capacity }} orang</span
        ><span class="free">Gratis</span>
      </div>
      <h3>
        <RouterLink :to="`/rooms/${room.id}`">{{
          room.name.replace("Ruang ", "")
        }}</RouterLink>
      </h3>
      <p class="facilities-line">
        {{
          room.facilities
            .slice(0, 3)
            .map((f) => f.name)
            .join(" · ")
        }}
      </p>
      <RouterLink class="card-action" :to="`/rooms/${room.id}`"
        >Lihat jadwal <AppIcon name="arrow"
      /></RouterLink>
    </div>
  </article>
</template>
