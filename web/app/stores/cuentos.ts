import { defineStore } from 'pinia'

export interface Story {
  slug: string
  num: number
  title: string
  author: string
  source: string
  image: string
  excerpt: string
  body: string
}

export const useCuentosStore = defineStore('cuentos', {
  state: () => ({
    stories: [] as Story[],
    loaded: false,
    searchQuery: '',
    selectedAuthor: '',
  }),

  getters: {
    filteredStories(): Story[] {
      let result = this.stories
      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase()
        result = result.filter(
          s =>
            s.title.toLowerCase().includes(q) ||
            s.author.toLowerCase().includes(q),
        )
      }
      if (this.selectedAuthor) {
        result = result.filter(s => s.author === this.selectedAuthor)
      }
      return result
    },

    authors(): string[] {
      const set = new Set(this.stories.map(s => s.author).filter(Boolean))
      return Array.from(set).sort()
    },

    totalStories(): number {
      return this.stories.length
    },

    getStoryBySlug: (state) => {
      return (slug: string) => state.stories.find(s => s.slug === slug)
    },

    getStoriesByAuthor: (state) => {
      return (author: string) => state.stories.filter(s => s.author === author)
    },

    paginatedStories(): Story[] {
      return this.filteredStories
    },
  },

  actions: {
    async fetchStories() {
      if (this.loaded) return
      const data = await $fetch<Story[]>('/cuentos.json')
      this.stories = data
      this.loaded = true
    },

    setSearch(query: string) {
      this.searchQuery = query
    },

    setAuthor(author: string) {
      this.selectedAuthor = author
    },

    clearFilters() {
      this.searchQuery = ''
      this.selectedAuthor = ''
    },
  },
})
