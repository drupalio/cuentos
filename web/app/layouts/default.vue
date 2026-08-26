<template>
  <div class="site">
    <header class="site-header">
      <div class="container header-inner">
        <NuxtLink to="/" class="site-logo">Cuentos de Lecturia</NuxtLink>
        <nav class="header-nav">
          <NuxtLink to="/">Portada</NuxtLink>
          <NuxtLink to="/autores">Autores</NuxtLink>
          <a href="https://lecturia.org" target="_blank" rel="noopener">Lecturia.org</a>
          <button class="search-toggle" @click="store.toggleSearch()" aria-label="Buscar">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </button>
        </nav>
        <button class="mobile-menu-btn" @click="mobileOpen = !mobileOpen" aria-label="Menu">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
        </button>
      </div>
      <div v-if="mobileOpen" class="container" style="padding-bottom: 1rem;">
        <nav style="display: flex; flex-direction: column; gap: 0.75rem;">
          <NuxtLink to="/" @click="mobileOpen = false">Portada</NuxtLink>
          <a href="https://lecturia.org" target="_blank" rel="noopener">Lecturia.org</a>
        </nav>
      </div>
    </header>

    <main class="site-main">
      <div class="container">
        <slot />
      </div>
    </main>

    <footer class="site-footer">
      <div class="container footer-inner">
        <div class="footer-links">
          <a href="https://lecturia.org" target="_blank" rel="noopener">Lecturia.org</a>
        </div>
        <p class="footer-copy">&copy; 2026 &middot; Cuentos de Lecturia</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useCuentosStore } from '~/stores/cuentos'
const store = useCuentosStore()
const mobileOpen = ref(false)
</script>

<style scoped>
.site {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.site-main {
  flex: 1;
  padding: 2.5rem 0;
}
</style>
