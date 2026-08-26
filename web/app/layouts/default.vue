<template>
  <div class="layout">
    <header class="header">
      <div class="container">
        <NuxtLink to="/" class="logo">
          <h1>Cuentos de Lecturia</h1>
          <span class="subtitle">Recopilación literaria</span>
        </NuxtLink>
      </div>
    </header>
    <main class="main">
      <div class="container">
        <slot />
      </div>
    </main>
    <footer class="footer">
      <div class="container">
        <p>Hecho con fines de preservación literaria y estudio.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  background: var(--color-card-bg);
  border-bottom: 1px solid var(--color-border);
  padding: 1.5rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
}

.logo {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.logo h1 {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.02em;
}

.logo .subtitle {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.main {
  flex: 1;
  padding: 3rem 0;
}

.footer {
  border-top: 1px solid var(--color-border);
  padding: 2rem 0;
  text-align: center;
  color: var(--color-text-muted);
  font-size: 0.85rem;
}
</style>
