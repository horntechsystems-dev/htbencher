<template>
  <div class="relative overflow-hidden rounded-2xl border border-white/20 bg-white/70 shadow-xl backdrop-blur-xl transition-all hover:shadow-2xl dark:border-white/10 dark:bg-gray-900/60">
    <div class="absolute inset-0 bg-gradient-to-br from-white/40 to-white/0 opacity-50 dark:from-white/10"></div>
    <div class="relative h-full p-6">
      <slot />
    </div>
  </div>
</template>
