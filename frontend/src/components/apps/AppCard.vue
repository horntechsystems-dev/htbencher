<template>
  <div class="rounded-lg border bg-surface-white p-6 shadow-sm ring-1 ring-outline-gray-2 transition-all hover:shadow-md">
    <div class="flex items-start justify-between">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-lg bg-surface-gray-2 flex items-center justify-center text-ink-gray-7 border">
          <Package class="h-5 w-5" />
        </div>
        <div>
          <h3 class="font-semibold text-ink-gray-9">{{ app.title || app.name }}</h3>
          <p class="text-xs text-ink-gray-5 font-mono">{{ app.name }}</p>
        </div>
      </div>
    </div>

    <p class="mt-4 text-sm text-ink-gray-6 line-clamp-2 min-h-[2.5rem]">
      {{ app.description || 'No description provided.' }}
    </p>

    <div class="mt-4 flex items-center justify-between">
      <div class="text-xs font-medium text-ink-gray-4">
        v{{ app.version || '0.0.1' }}
      </div>
      <div class="flex gap-2">
        <Button variant="subtle" size="sm" @click="$emit('update', app)">
          Update
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Package } from "lucide-vue-next"

defineProps({
	app: Object,
})

defineEmits(["update", "uninstall"])
</script>
