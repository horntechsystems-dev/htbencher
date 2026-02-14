<template>
  <span class="inline-flex items-center gap-2 rounded-full border px-2.5 py-0.5 text-xs font-medium backdrop-blur-sm transition-colors"
    :class="statusStyles"
  >
    <span class="relative flex h-2 w-2">
      <span
        class="absolute inline-flex h-full w-full animate-ping rounded-full opacity-75"
        :class="pingColor"
      ></span>
      <span
        class="relative inline-flex h-2 w-2 rounded-full"
        :class="dotColor"
      ></span>
    </span>
    {{ label || status }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
  },
  label: String,
})

const colorMap = {
  Active: 'green',
  Running: 'green',
  Success: 'green',
  Stopped: 'gray',
  Failed: 'red',
  Error: 'red',
  Warning: 'orange',
  Pending: 'yellow',
}

const styles = {
  green: {
    container: 'bg-green-50/50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-800',
    dot: 'bg-green-500',
    ping: 'bg-green-400',
  },
  red: {
    container: 'bg-red-50/50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-800',
    dot: 'bg-red-500',
    ping: 'bg-red-400',
  },
  yellow: {
    container: 'bg-yellow-50/50 text-yellow-700 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-300 dark:border-yellow-800',
    dot: 'bg-yellow-500',
    ping: 'bg-yellow-400',
  },
  orange: {
    container: 'bg-orange-50/50 text-orange-700 border-orange-200 dark:bg-orange-900/20 dark:text-orange-300 dark:border-orange-800',
    dot: 'bg-orange-500',
    ping: 'bg-orange-400',
  },
  gray: {
    container: 'bg-gray-50/50 text-gray-700 border-gray-200 dark:bg-gray-800/50 dark:text-gray-300 dark:border-gray-700',
    dot: 'bg-gray-500',
    ping: 'bg-gray-400',
  },
}

const statusKey = computed(() => {
  return colorMap[props.status] || 'gray'
})

const statusStyles = computed(() => styles[statusKey.value].container)
const dotColor = computed(() => styles[statusKey.value].dot)
const pingColor = computed(() => styles[statusKey.value].ping)
</script>
