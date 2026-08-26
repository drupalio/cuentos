<template>
  <div class="story-page" v-if="story">
    <div class="story-header">
      <NuxtLink to="/" class="back-link">← Volver</NuxtLink>
      <span class="story-num">#{{ story.num }}</span>
      <h1 class="story-title">{{ story.title }}</h1>
      <p class="story-author" v-if="story.author">{{ story.author }}</p>
      <a v-if="story.source" :href="story.source" target="_blank" rel="noopener" class="source-link">
        Ver en Lecturia.org ↗
      </a>
    </div>

    <div class="story-image" v-if="story.image">
      <img :src="`/images/${story.image}`" :alt="story.title" />
    </div>

    <article class="story-body" v-html="renderedBody"></article>

    <div class="story-nav">
      <NuxtLink v-if="prevStory" :to="`/cuento/${prevStory.slug}`" class="nav-link prev">
        ← {{ prevStory.title }}
      </NuxtLink>
      <span v-else></span>
      <NuxtLink v-if="nextStory" :to="`/cuento/${nextStory.slug}`" class="nav-link next">
        {{ nextStory.title }} →
      </NuxtLink>
    </div>
  </div>
  <div v-else class="not-found">
    <h2>Cuento no encontrado</h2>
    <NuxtLink to="/">Volver al inicio</NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { useCuentosStore } from '~/stores/cuentos'

const route = useRoute()
const store = useCuentosStore()

await store.fetchStories()

const slug = route.params.slug as string
const story = computed(() => store.getStoryBySlug(slug))

const prevStory = computed(() => {
  if (!story.value) return null
  return store.stories.find(s => s.num === story.value!.num - 1)
})

const nextStory = computed(() => {
  if (!story.value) return null
  return store.stories.find(s => s.num === story.value!.num + 1)
})

function renderMarkdown(md: string): string {
  return md
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/gs, (match) => `<ul>${match}</ul>`)
    .split('\n\n')
    .map(p => {
      p = p.trim()
      if (!p) return ''
      if (p.startsWith('<h') || p.startsWith('<ul')) return p
      return `<p>${p}</p>`
    })
    .filter(Boolean)
    .join('\n')
}

const renderedBody = computed(() => {
  if (!story.value) return ''
  return renderMarkdown(story.value.body)
})

useHead({
  title: computed(() => story.value ? `${story.value.title} — Cuentos de Lecturia` : 'Cuento no encontrado'),
})
</script>

<style scoped>
.story-page {
  max-width: 720px;
  margin: 0 auto;
}

.story-header {
  margin-bottom: 2rem;
}

.back-link {
  display: inline-block;
  color: var(--color-accent);
  font-size: 0.9rem;
  margin-bottom: 1rem;
  transition: opacity 0.2s;
}

.back-link:hover {
  opacity: 0.7;
}

.story-num {
  display: block;
  font-size: 0.8rem;
  color: var(--color-accent);
  font-weight: 600;
  letter-spacing: 0.1em;
  margin-bottom: 0.5rem;
}

.story-title {
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 0.75rem;
  color: var(--color-text);
}

.story-author {
  font-size: 1.1rem;
  color: var(--color-accent);
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.source-link {
  display: inline-block;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  border-bottom: 1px dashed var(--color-border);
  transition: color 0.2s;
}

.source-link:hover {
  color: var(--color-accent);
}

.story-image {
  margin-bottom: 2rem;
  border-radius: 12px;
  overflow: hidden;
}

.story-image img {
  width: 100%;
  height: auto;
  display: block;
}

.story-body {
  font-size: 1.1rem;
  line-height: 1.85;
  color: var(--color-text);
}

.story-body :deep(p) {
  margin-bottom: 1.25rem;
  text-align: justify;
}

.story-body :deep(h2),
.story-body :deep(h3) {
  font-family: var(--font-display);
  margin: 2rem 0 1rem;
  color: var(--color-text);
}

.story-body :deep(ul) {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.story-body :deep(li) {
  margin-bottom: 0.5rem;
}

.story-body :deep(strong) {
  font-weight: 600;
}

.story-body :deep(em) {
  font-style: italic;
}

.story-nav {
  display: flex;
  justify-content: space-between;
  margin-top: 4rem;
  padding-top: 2rem;
  border-top: 1px solid var(--color-border);
}

.nav-link {
  font-size: 0.9rem;
  color: var(--color-accent);
  max-width: 45%;
  transition: opacity 0.2s;
}

.nav-link:hover {
  opacity: 0.7;
}

.nav-link.next {
  text-align: right;
  margin-left: auto;
}

.not-found {
  text-align: center;
  padding: 4rem 0;
}

.not-found h2 {
  margin-bottom: 1rem;
}

.not-found a {
  color: var(--color-accent);
}

@media (max-width: 640px) {
  .story-title {
    font-size: 1.75rem;
  }

  .story-body {
    font-size: 1rem;
  }
}
</style>
