<template>
  <div class="flex flex-col space-y-2">
     <div v-if="progress !== null" class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
        <div class="bg-blue-600 h-2.5 rounded-full transition-all duration-300" :style="{ width: progress + '%' }"></div>
     </div>
     <p v-if="status" class="text-xs font-semibold text-gray-600 dark:text-gray-400 text-right">{{ status }} ... {{ progress }}%</p>

    <div ref="logContainer" class="h-64 overflow-y-auto rounded-lg bg-black p-4 font-mono text-xs text-green-400 shadow-inner">
      <div v-for="(log, index) in logs" :key="index" class="whitespace-pre-wrap break-words">
        <span class="text-gray-500">[{{ log.time }}]</span>
        <span :class="{'text-red-500': log.error, 'text-yellow-400': log.warning}">{{ log.message }}</span>
      </div>
      <div v-if="logs.length === 0" class="text-gray-600 italic">Waiting for logs...</div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from "vue"

const props = defineProps({
  logs: {
    type: Array, // [{ time: 'HH:MM:SS', message: '...', error: false }]
    default: () => [],
  },
  progress: {
    type: Number,
    default: 0,
  },
  status: {
    type: String,
    default: "",
  },
})

const logContainer = ref(null)

// Auto-scroll to bottom when logs update
watch(() => props.logs.length, () => {
    nextTick(() => {
        if (logContainer.value) {
            logContainer.value.scrollTop = logContainer.value.scrollHeight
        }
    })
})
</script>
