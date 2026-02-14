<template>
  <Dialog
    v-bind="$attrs"
    :title="`Logs for ${bench.name}`"
    size="xl"
  >
    <template #body>
      <div class="rounded-lg bg-ink-gray-9 p-4 font-mono text-xs text-surface-white h-96 overflow-y-auto">
        <div v-if="logs.loading" class="flex items-center justify-center h-full">
          <LoadingIndicator />
        </div>
        <div v-else-if="logs.data" v-html="formattedLogs"></div>
        <div v-else class="text-ink-gray-4">No logs available</div>
      </div>
    </template>
    <template #actions>
      <Button variant="subtle" @click="$emit('update:modelValue', false)">
        Close
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed } from "vue"

const props = defineProps({
	bench: Object,
})

defineEmits(["update:modelValue"])

// Disabled until htbencher.api.get_bench_logs endpoint is created
/*
const logs = createResource({
	url: "htbencher.api.get_bench_logs",
	makeParams() {
		return { bench_name: props.bench.name }
	},
	auto: true,
})
*/

const logs = {
	loading: false,
	data: "Bench logs endpoint not yet implemented.\nThis feature will be available soon."
}

const formattedLogs = computed(() => {
	if (!logs.data) return ""
	// simple colorization for demo - in reality, you might use a library or backend formatting
	return logs.data
		.replace(/INFO/g, '<span class="text-ink-blue-2">INFO</span>')
		.replace(/ERROR/g, '<span class="text-ink-red-3">ERROR</span>')
		.replace(/WARNING/g, '<span class="text-ink-orange-3">WARNING</span>')
		.replace(/\n/g, "<br>")
})
</script>
