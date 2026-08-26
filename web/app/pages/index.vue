<template>
  <div class="home">
    <div class="hero">
      <h2>{{ totalStories }} cuentos para explorar</h2>
      <div class="search-bar">
        <input
          v-model="search"
          type="text"
          placeholder="Buscar por título o autor..."
          class="search-input"
          @input="onSearch"
        />
      </div>
      <div class="filters">
        <select v-model="authorFilter" class="author-select" @change="onAuthorFilter">
          <option value="">Todos los autores</option>
          <option v-for="a in authors" :key="a" :value="a">{{ a }}</option>
        </select>
        <button v-if="search || authorFilter" class="clear-btn" @click="clearFilters">
          Limpiar filtros
        </button>
      </div>
    </div>

    <div class="results-info" v-if="search || authorFilter">
      <span>{{ filteredStories.length }} resultado{{ filteredStories.length !== 1 ? 's' : '' }}</span>
    </div>

    <div class="grid">
      <StoryCard v-for="story in displayedStories" :key="story.slug" :story="story" />
    </div>

    <div v-if="displayedStories.length < filteredStories.length" class="load-more">
      <button @click="loadMore" class="load-more-btn">
        Cargar más ({{ filteredStories.length - displayedStories.length }} restantes)
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useCuentosStore } from '~/stores/cuentos'

const store = useCuentosStore()

await store.fetchStories()

const search = ref('')
const authorFilter = ref('')
const displayCount = ref(60)

const totalStories = computed(() => store.totalStories)
const authors = computed(() => store.authors)
const filteredStories = computed(() => store.filteredStories)

const displayedStories = computed(() => filteredStories.value.slice(0, displayCount.value))

function onSearch() {
  store.setSearch(search.value)
  displayCount.value = 60
}

function onAuthorFilter() {
  store.setAuthor(authorFilter.value)
  displayCount.value = 60
}

function clearFilters() {
  search.value = ''
  authorFilter.value = ''
  store.clearFilters()
  displayCount.value = 60
}

function loadMore() {
  displayCount.value += 60
}
</script>

<style scoped>
.hero {
  text-align: center;
  margin-bottom: 3rem;
}

.hero h2 {
  font-family: var(--font-display);
  font-size: 2rem;
  color: var(--color-text);
  margin-bottom: 1.5rem;
}

.search-bar {
  max-width: 500px;
  margin: 0 auto 1rem;
}

.search-input {
  width: 100%;
  padding: 0.875rem 1.25rem;
  border: 2px solid var(--color-border);
  border-radius: 50px;
  font-size: 1rem;
  font-family: var(--font-body);
  background: var(--color-card-bg);
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.filters {
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
}

.author-select {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-family: var(--font-body);
  font-size: 0.9rem;
  background: var(--color-card-bg);
  cursor: pointer;
}

.clear-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-accent);
  border-radius: 8px;
  background: transparent;
  color: var(--color-accent);
  font-family: var(--font-body);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: var(--color-accent);
  color: white;
}

.results-info {
  text-align: center;
  color: var(--color-text-muted);
  margin-bottom: 2rem;
  font-size: 0.9rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.load-more {
  text-align: center;
  margin-top: 3rem;
}

.load-more-btn {
  padding: 0.875rem 2rem;
  border: 2px solid var(--color-accent);
  border-radius: 50px;
  background: transparent;
  color: var(--color-accent);
  font-family: var(--font-body);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.load-more-btn:hover {
  background: var(--color-accent);
  color: white;
}

@media (max-width: 640px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .hero h2 {
    font-size: 1.5rem;
  }
}
</style>
