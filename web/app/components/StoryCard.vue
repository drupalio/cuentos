<template>
  <NuxtLink :to="`/cuento/${story.slug}`" class="story-card">
    <div class="card-image">
      <img
        v-if="story.image"
        :src="`/images/${story.image}`"
        :alt="story.title"
        loading="lazy"
      />
      <div v-else class="card-image-placeholder">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
      </div>
    </div>
    <div class="card-body">
      <div class="card-num">#{{ story.num }}</div>
      <h3 class="card-title">{{ story.title }}</h3>
      <p class="card-author" v-if="story.author">{{ story.author }}</p>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
import type { Story } from '~/stores/cuentos'
defineProps<{ story: Story }>()
</script>
