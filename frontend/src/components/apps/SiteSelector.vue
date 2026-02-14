
<template>
  <div class="space-y-2">
    <div 
      v-if="loading"
      class="flex h-12 items-center justify-center rounded-xl bg-gray-50 dark:bg-gray-800/50"
    >
      <svg class="h-5 w-5 animate-spin text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10" stroke-opacity="0.25" />
        <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round" />
      </svg>
    </div>
    <div v-else-if="sites.length === 0" class="text-center p-4 rounded-xl border border-dashed border-gray-200 dark:border-gray-700">
        <p class="text-sm text-gray-500">No sites found on this bench.</p>
    </div>
    <div v-else class="grid grid-cols-1 gap-2">
      <button
        v-for="site in sites"
        :key="site.name"
        @click="$emit('update:modelValue', site.name)"
        class="flex items-center justify-between rounded-xl border p-4 text-left transition-all duration-200"
        :class="[
          modelValue === site.name
            ? 'border-gray-900 bg-gray-50 dark:border-white dark:bg-gray-800/50'
            : 'border-gray-100 hover:border-gray-300 dark:border-gray-800 dark:hover:border-gray-600'
        ]"
      >
        <div class="flex items-center gap-3">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-white shadow-sm dark:bg-gray-700">
            <svg class="h-4 w-4 text-gray-600 dark:text-gray-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-900 dark:text-white">{{ site.site_name }}</div>
            <div class="text-xs text-gray-500">{{ site.root_domain || 'Internal Site' }}</div>
          </div>
        </div>
        <div 
          v-if="modelValue === site.name"
          class="h-2 w-2 rounded-full bg-gray-900 dark:bg-white"
        ></div>
      </button>
      
      <!-- Option to skip site selection (install to bench only) -->
      <button
        @click="$emit('update:modelValue', null)"
        class="flex items-center justify-between rounded-xl border p-4 text-left transition-all duration-200"
        :class="[
          modelValue === null
            ? 'border-gray-900 bg-gray-50 dark:border-white dark:bg-gray-800/50'
            : 'border-gray-100 hover:border-gray-300 dark:border-gray-800 dark:hover:border-gray-600'
        ]"
      >
        <div class="flex items-center gap-3">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-white shadow-sm dark:bg-gray-700 border border-dashed">
            <svg class="h-4 w-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-400">Install to Bench Only</div>
            <div class="text-xs text-gray-500">Skip site installation</div>
          </div>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: String,
  sites: {
    type: Array,
    default: () => []
  },
  loading: Boolean
})

defineEmits(["update:modelValue"])
</script>
