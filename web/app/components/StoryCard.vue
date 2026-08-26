<template>
  <NuxtLink :to="`/cuento/${story.slug}`" class="card">
    <div class="card-image" v-if="story.image">
      <img :src="`/images/${story.image}`" :alt="story.title" loading="lazy" />
    </div>
    <div class="card-image placeholder" v-else>
      <span class="placeholder-icon">📖</span>
    </div>
    <div class="card-content">
      <span class="card-num">#{{ story.num }}</span>
      <h3 class="card-title">{{ story.title }}</h3>
      <p class="card-author" v-if="story.author">{{ story.author }}</p>
      <p class="card-excerpt">{{ story.excerpt }}</p>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
import type { Story } from '~/stores/cuentos'

defineProps<{ story: Story }>()
</script>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  background: var(--color-card-bg);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
}

.card-image {
  aspect-ratio: 3/2;
  overflow: hidden;
  background: #f0ece6;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.card:hover .card-image img {
  transform: scale(1.05);
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f0e8 0%, #e8e0d4 100%);
}

.placeholder-icon {
  font-size: 3rem;
  opacity: 0.4;
}

.card-content {
  padding: 1.25rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-num {
  font-size: 0.75rem;
  color: var(--color-accent);
  font-weight: 600;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.card-title {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: 0.5rem;
  color: var(--color-text);
}

.card-author {
  font-size: 0.85rem;
  color: var(--color-accent);
  font-weight: 500;
  margin-bottom: 0.75rem;
}

.card-excerpt {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  line-height: 1.5;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
