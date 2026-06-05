<template>
  <div class="scanline" aria-hidden="true">
    <div class="scanline-grid" />
    <div class="scanline-beam" />
    <div class="scanline-noise" />
  </div>
</template>

<style scoped>
.scanline {
  pointer-events: none;
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
}

.scanline-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(77, 255, 145, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(77, 255, 145, 0.03) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse 70% 60% at 50% 0%, black, transparent 75%);
}

.scanline-beam {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(77, 255, 145, 0.04) 50%,
    transparent 100%
  );
  background-size: 100% 6px;
  animation: beam-drift 8s linear infinite;
  opacity: 0.5;
}

.scanline-noise {
  position: absolute;
  inset: 0;
  opacity: 0.035;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

@keyframes beam-drift {
  from { background-position: 0 0; }
  to { background-position: 0 100vh; }
}

@media (prefers-reduced-motion: reduce) {
  .scanline-beam {
    animation: none;
  }
}
</style>
