<template>
  <div class="home">
    <div class="section-heading">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" fill="currentColor"><path d="M0 48V432c0 26.5 21.5 48 48 48H48c26.5 0 48-21.5 48-48V48C96 21.5 74.5 0 48 0H0zm0 0C21.5 0 48 21.5 48 48V432c0 26.5-21.5 48-48 48H0V0zm336 0v432c0 26.5-21.5 48-48 48H288c-26.5 0-48-21.5-48-48V48c0-26.5 21.5-48 48-48h48zM336 0c26.5 0 48 21.5 48 48V432c0 26.5-21.5 48-48 48H288V0h48z"/></svg>
      <h2>Cuentos completos</h2>
    </div>

    <div class="masonry-grid">
      <div
        v-for="story in displayedStories"
        :key="story.slug"
        class="masonry-item"
      >
        <StoryCard :story="story" />
      </div>
    </div>

    <div v-if="displayedStories.length < totalFiltered" class="load-more">
      <button class="load-more-btn" @click="loadMore">
        Ver más cuentos
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 512" fill="currentColor"><path d="M224.3 273l-136 136c-9.4 9.4-24.6 9.4-33.9 0l-22.6-22.6c-9.4-9.4-9.4-24.6 0-33.9l96.4-96.4-96.4-96.4c-9.4-9.4-9.4-24.6 0-33.9L54.3 103c9.4-9.4 24.6-9.4 33.9 0l136 136c9.5 9.4 9.5 24.6.1 34z"/></svg>
      </button>
    </div>

    <!-- Search overlay -->
    <Teleport to="body">
      <div class="search-overlay" :class="{ active: showSearch }" @click.self="store.closeSearch()">
        <div class="search-box">
          <button class="search-close" @click="store.closeSearch()" aria-label="Cerrar">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
          <input
            ref="searchInput"
            v-model="searchQuery"
            type="text"
            placeholder="Buscar..."
            @input="onSearch"
            @keydown.escape="store.closeSearch()"
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

const searchQuery = ref('')
const displayCount = ref(80)
const searchInput = ref<HTMLInputElement>()

const showSearch = computed(() => store.showSearch)
const totalFiltered = computed(() => store.filteredStories.length)
const displayedStories = computed(() => store.filteredStories.slice(0, displayCount.value))

function onSearch() {
  store.setSearch(searchQuery.value)
  displayCount.value = 80
}

function loadMore() {
  displayCount.value += 80
}

watch(showSearch, (val) => {
  if (val) {
    nextTick(() => searchInput.value?.focus())
  }
})

useHead({
  title: 'Cuentos de Lecturia',
})
</script>
