<template>
  <div class="story-page" v-if="story">
    <NuxtLink to="/" class="story-back">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
      Volver
    </NuxtLink>

    <div class="story-meta">
      <div class="story-num">#{{ story.num }}</div>
      <h1 class="story-title">{{ story.title }}</h1>
      <p class="story-author" v-if="story.author">{{ story.author }}</p>
      <a
        v-if="story.source"
        :href="story.source"
        target="_blank"
        rel="noopener"
        class="story-source"
      >
        Ver en Lecturia.org
      </a>
    </div>

    <div class="story-cover" v-if="story.image">
      <img :src="`/images/${story.image}`" :alt="story.title" />
    </div>

    <article class="story-content" v-html="renderedBody"></article>

    <div class="story-nav">
      <NuxtLink v-if="prevStory" :to="`/cuento/${prevStory.slug}`">
        &larr; {{ prevStory.title }}
      </NuxtLink>
      <span v-else></span>
      <NuxtLink v-if="nextStory" :to="`/cuento/${nextStory.slug}`" class="next">
        {{ nextStory.title }} &rarr;
      </NuxtLink>
    </div>
  </div>
  <div v-else style="text-align: center; padding: 4rem 0;">
    <h2>Cuento no encontrado</h2>
    <NuxtLink to="/" style="color: var(--text-muted); margin-top: 1rem; display: inline-block;">Volver al inicio</NuxtLink>
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
