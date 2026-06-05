<script setup>
defineProps({
  eyebrow: { type: String, default: '' },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
})
</script>

<template>
  <header class="page-header-block">
    <div class="page-header-text">
      <p v-if="eyebrow" class="page-eyebrow">{{ eyebrow }}</p>
      <h1 class="page-title">{{ title }}</h1>
      <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.actions" class="page-header-actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<style scoped>
.page-header-block {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 36px;
}

.page-eyebrow {
  margin: 0 0 8px;
  font-family: var(--aits-mono);
  font-size: 11px;
  font-weight: 500;
  color: var(--aits-accent);
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.page-title {
  margin: 0 0 10px;
  font-family: var(--aits-display);
  font-size: clamp(26px, 4vw, 34px);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.page-subtitle {
  margin: 0;
  max-width: 520px;
  font-size: 14px;
  color: var(--aits-text-muted);
  line-height: 1.6;
}

.page-header-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
  align-items: center;
}
</style>
