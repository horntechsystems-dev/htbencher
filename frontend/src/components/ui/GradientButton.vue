<template>
  <button
    class="group relative flex items-center justify-center overflow-hidden rounded-xl bg-gray-900 px-6 py-2.5 text-sm font-semibold text-white shadow-lg transition-all hover:scale-[1.02] hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 disabled:opacity-70 disabled:hover:scale-100 dark:bg-white dark:text-gray-900 dark:ring-offset-gray-900"
    :class="[
      loading ? 'cursor-not-allowed opacity-80' : '',
      block ? 'w-full' : '',
    ]"
    :disabled="loading || disabled"
  >
    <div
      class="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-1000 group-hover:translate-x-full"
    ></div>
    <svg
      v-if="loading"
      class="-ml-1 mr-2 h-4 w-4 animate-spin text-current"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        class="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      ></circle>
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      ></path>
    </svg>
    <slot />
  </button>
</template>

<script setup>
defineProps({
  loading: Boolean,
  disabled: Boolean,
  block: Boolean,
})
</script>
