<template>
  <div class="rounded-lg border bg-surface-white p-6 shadow-sm ring-1 ring-outline-gray-2 transition-all hover:shadow-md">
    <div class="flex items-start justify-between">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-lg bg-surface-gray-2 flex items-center justify-center text-ink-gray-7 border">
          <Terminal class="h-5 w-5" />
        </div>
        <div>
          <h3 class="font-semibold text-ink-gray-9">{{ bench.name }}</h3>
          <p class="text-xs text-ink-gray-5 font-mono">{{ bench.path }}</p>
        </div>
      </div>
      <StatusBadge :status="bench.status" :label="bench.status" />
    </div>

    <div class="mt-6 flex items-center justify-between text-sm">
      <div class="flex gap-4">
        <div>
          <p class="text-xs text-ink-gray-4 uppercase font-bold tracking-wider">Sites</p>
          <p class="font-medium text-ink-gray-9">{{ bench.total_sites || 0 }}</p>
        </div>
        <div>
          <p class="text-xs text-ink-gray-4 uppercase font-bold tracking-wider">Apps</p>
          <p class="font-medium text-ink-gray-9">{{ bench.total_apps || 0 }}</p>
        </div>
      </div>
    </div>

    <div class="mt-6 flex gap-2">
      <Button class="flex-1" variant="subtle" size="sm" @click="$emit('viewLogs', bench)">
        Logs
      </Button>
      <Button class="flex-1" variant="subtle" size="sm" @click="$emit('restart', bench)">
        Restart
      </Button>
    </div>
  </div>
</template>

<script setup>
import StatusBadge from "@/components/ui/StatusBadge.vue"
import { Terminal } from "lucide-vue-next"

defineProps({
	bench: Object,
})

defineEmits(["restart", "viewLogs"])
</script>
