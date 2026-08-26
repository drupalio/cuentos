<template>
  <div class="home">
    <!-- Author list view -->
    <div v-if="!selectedAuthor" class="authors-view">
      <div class="section-heading">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" fill="currentColor"><path d="M0 48V432c0 26.5 21.5 48 48 48H48c26.5 0 48-21.5 48-48V48C96 21.5 74.5 0 48 0H0zm0 0C21.5 0 48 21.5 48 48V432c0 26.5-21.5 48-48 48H0V0zm336 0v432c0 26.5-21.5 48-48 48H288c-26.5 0-48-21.5-48-48V48c0-26.5 21.5-48 48-48h48zM336 0c26.5 0 48 21.5 48 48V432c0 26.5-21.5 48-48 48H288V0h48z"/></svg>
        <h2>Autores</h2>
      </div>

      <div class="authors-grid">
        <button
          v-for="author in authorsWithCount"
          :key="author.name"
          class="author-card"
          @click="selectAuthor(author.name)"
        >
          <div class="author-avatar" :style="{ '--scale': author.count / maxCount }">
            {{ author.initials }}
          </div>
          <div class="author-info">
            <div class="author-name">{{ author.name }}</div>
            <div class="author-count">{{ author.count }} {{ author.count === 1 ? 'cuento' : 'cuentos' }}</div>
          </div>
          <div class="author-bar" :style="{ width: (author.count / maxCount * 100) + '%' }"></div>
        </button>
      </div>
    </div>

    <!-- Stories by author view -->
    <div v-else class="stories-view">
      <div class="section-heading">
        <button class="back-btn" @click="clearAuthor">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 512" fill="currentColor"><path d="M224.3 273l-136 136c-9.4 9.4-24.6 9.4-33.9 0l-22.6-22.6c-9.4-9.4-9.4-24.6 0-33.9l96.4-96.4-96.4-96.4c-9.4-9.4-9.4-24.6 0-33.9L54.3 103c9.4-9.4 24.6-9.4 33.9 0l136 136c9.5 9.4 9.5 24.6.1 34z"/></svg>
        </button>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" fill="currentColor"><path d="M0 48V432c0 26.5 21.5 48 48 48H48c26.5 0 48-21.5 48-48V48C96 21.5 74.5 0 48 0H0zm0 0C21.5 0 48 21.5 48 48V432c0 26.5-21.5 48-48 48H0V0zm336 0v432c0 26.5-21.5 48-48 48H288c-26.5 0-48-21.5-48-48V48c0-26.5 21.5-48 48-48h48zM336 0c26.5 0 48 21.5 48 48V432c0 26.5-21.5 48-48 48H288V0h48z"/></svg>
        <h2>{{ selectedAuthor }}</h2>
        <span class="author-stories-count">{{ authorStories.length }} cuentos</span>
      </div>

      <div class="masonry-grid">
        <div
          v-for="story in displayedAuthorStories"
          :key="story.slug"
          class="masonry-item"
        >
          <StoryCard :story="story" />
        </div>
      </div>

      <div v-if="displayedAuthorStories.length < authorStories.length" class="load-more">
        <button class="load-more-btn" @click="loadMore">
          Ver más cuentos
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 512" fill="currentColor"><path d="M224.3 273l-136 136c-9.4 9.4-24.6 9.4-33.9 0l-22.6-22.6c-9.4-9.4-9.4-24.6 0-33.9l96.4-96.4-96.4-96.4c-9.4-9.4-9.4-24.6 0-33.9L54.3 103c9.4-9.4 24.6-9.4 33.9 0l136 136c9.5 9.4 9.5 24.6.1 34z"/></svg>
        </button>
      </div>
    </div>

    <!-- Search overlay -->
    <Teleport to="body">
      <div class="search-overlay" :class="{ active: showSearch }" @click.self="showSearch = false">
        <div class="search-box">
          <input
            ref="searchInput"
            v-model="searchQuery"
            type="text"
            placeholder="Buscar..."
            @input="onSearch"
            @keydown.escape="showSearch = false"
          />
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { useCuentosStore } from '~/stores/cuentos'

const store = useCuentosStore()
await store.fetchStories()

const route = useRoute()
const router = useRouter()

const searchQuery = ref('')
const showSearch = ref(false)
const displayCount = ref(80)
const searchInput = ref<HTMLInputElement>()

const selectedAuthor = computed(() => {
  const author = route.query.author as string
  return author || ''
})

const authorsWithCount = computed(() => {
  const counts = new Map<string, number>()
  for (const story of store.stories) {
    if (story.author) {
      counts.set(story.author, (counts.get(story.author) || 0) + 1)
    }
  }
  return Array.from(counts.entries())
    .map(([name, count]) => ({
      name,
      count,
      initials: name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase(),
    }))
    .sort((a, b) => b.count - a.count)
})

const maxCount = computed(() => {
  if (authorsWithCount.value.length === 0) return 1
  return authorsWithCount.value[0].count
})

const authorStories = computed(() => {
  if (!selectedAuthor.value) return []
  return store.stories.filter(s => s.author === selectedAuthor.value)
})

const displayedAuthorStories = computed(() => {
  return authorStories.value.slice(0, displayCount.value)
})

function selectAuthor(name: string) {
  router.push({ query: { author: name } })
}

function clearAuthor() {
  router.push({ query: {} })
  displayCount.value = 80
}

function loadMore() {
  displayCount.value += 80
}

function onSearch() {
  store.setSearch(searchQuery.value)
  displayCount.value = 80
}

watch(selectedAuthor, () => {
  displayCount.value = 80
})

defineExpose({ showSearch })

watch(showSearch, (val) => {
  if (val) {
    nextTick(() => searchInput.value?.focus())
  }
})

useHead({
  title: () => selectedAuthor.value ? `${selectedAuthor.value} - Autores` : 'Autores',
})
</script>

<style scoped>
.authors-view {
  max-width: 800px;
  margin: 0 auto;
}

.authors-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.author-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
  overflow: hidden;
  text-align: left;
  width: 100%;
}

.author-card:hover {
  border-color: var(--accent);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  transform: translateX(4px);
}

.author-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--accent);
  color: var(--white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 700;
  flex-shrink: 0;
  transform: scale(calc(0.7 + var(--scale) * 0.3));
}

.author-info {
  flex: 1;
  min-width: 0;
}

.author-name {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 0.125rem;
}

.author-count {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.author-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: var(--accent);
  opacity: 0.15;
  transition: width 0.4s ease, opacity 0.25s ease;
}

.author-card:hover .author-bar {
  opacity: 0.4;
}

.stories-view .section-heading {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.back-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  padding: 0.5rem;
  display: flex;
  align-items: center;
  transition: color 0.2s;
  margin-left: -0.5rem;
}

.back-btn:hover {
  color: var(--text);
}

.back-btn svg {
  width: 1rem;
  height: 1rem;
}

.author-stories-count {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-left: auto;
}
</style>
