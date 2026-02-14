<template>
  <div class="space-y-2">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Select Repository</label>
    <div class="relative">
      <GlassInput
        v-model="search"
        placeholder="Search repositories..."
        class="mb-2"
      />
      <div v-if="loading" class="flex justify-center py-4">
        <LoadingIndicator />
      </div>
      <div v-else class="max-h-60 overflow-y-auto rounded-xl border border-gray-200 dark:border-gray-700">
        <div
          v-for="repo in filteredRepos"
          :key="repo.full_name"
          class="cursor-pointer border-b border-gray-100 p-3 last:border-0 hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-gray-800/50"
          :class="{ 'bg-blue-50 dark:bg-blue-900/20': modelValue?.full_name === repo.full_name }"
          @click="$emit('update:modelValue', repo)"
        >
          <div class="font-medium text-gray-900 dark:text-white">{{ repo.name }}</div>
          <div class="text-xs text-gray-500">{{ repo.full_name }}</div>
        </div>
        <div v-if="!filteredRepos.length" class="p-4 text-center text-sm text-gray-500">
          No repositories found.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import GlassInput from "@/components/ui/GlassInput.vue"

const props = defineProps({
  modelValue: Object,
  repositories: {
    type: Array,
    default: () => []
  },
  loading: Boolean
})

defineEmits(['update:modelValue'])

const search = ref("")

const filteredRepos = computed(() => {
  if (!search.value) return props.repositories
  const s = search.value.toLowerCase()
  return props.repositories.filter(r => 
    r.name.toLowerCase().includes(s) || r.full_name.toLowerCase().includes(s)
  )
})
</script>
