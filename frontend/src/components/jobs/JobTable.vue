<template>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-outline-gray-1">
      <thead class="bg-surface-gray-1">
        <tr>
          <th class="px-6 py-3 text-left text-xs font-semibold text-ink-gray-4 uppercase tracking-wider">Job ID</th>
          <th class="px-6 py-3 text-left text-xs font-semibold text-ink-gray-4 uppercase tracking-wider">Method</th>
          <th class="px-6 py-3 text-left text-xs font-semibold text-ink-gray-4 uppercase tracking-wider">Status</th>
          <th class="px-6 py-3 text-left text-xs font-semibold text-ink-gray-4 uppercase tracking-wider">Creation</th>
          <th class="px-6 py-3 text-right text-xs font-semibold text-ink-gray-4 uppercase tracking-wider">Actions</th>
        </tr>
      </thead>
      <tbody class="bg-surface-white divide-y divide-outline-gray-1">
        <tr v-for="job in jobs" :key="job.name" class="hover:bg-surface-gray-1 transition-colors">
          <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-ink-gray-9">
            #{{ job.name.substring(0, 8) }}
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-ink-gray-7">
            {{ job.method }}
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            <StatusBadge :status="job.status" :label="job.status" />
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-ink-gray-5">
            {{ job.creation }}
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
            <Button variant="subtle" size="sm" @click="$emit('viewLogs', job)">
              View Logs
            </Button>
          </td>
        </tr>
        <tr v-if="!jobs.length && !loading">
          <td colspan="5" class="px-6 py-20 text-center text-sm text-ink-gray-4">
            No jobs recorded.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import StatusBadge from "@/components/ui/StatusBadge.vue"

defineProps({
	jobs: Array,
	loading: Boolean,
})

defineEmits(["viewLogs"])
</script>
