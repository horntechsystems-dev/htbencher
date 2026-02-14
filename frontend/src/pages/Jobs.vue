<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Background Jobs</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">Monitor and manage background tasks.</p>
      </div>
      <div class="flex gap-2">
        <Button variant="subtle" @click="jobList.reload()" :loading="jobList.loading">
          <RefreshCcw class="mr-2 h-4 w-4" :class="{ 'animate-spin': jobList.loading }" />
          Refresh
        </Button>
      </div>
    </div>

    <!-- Job Stats (Placeholder for now) -->
    <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
      <GlassCard class="p-4">
        <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Active Jobs</p>
        <div class="mt-1 flex items-baseline gap-2">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ activeJobsCount }}
          </h3>
          <span class="inline-flex h-2 w-2 animate-pulse rounded-full bg-green-500"></span>
        </div>
      </GlassCard>
       <GlassCard class="p-4">
        <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Completed (24h)</p>
         <h3 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ completedJobsCount }}
          </h3>
      </GlassCard>
      <GlassCard class="p-4">
        <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Failed (24h)</p>
         <h3 class="text-2xl font-bold text-gray-900 dark:text-white text-red-600 dark:text-red-400">
            {{ failedJobsCount }}
          </h3>
      </GlassCard>
    </div>

    <!-- Job List -->
    <GlassCard class="overflow-hidden p-0">
       <div v-if="jobList.loading && !jobList.data" class="p-6 space-y-4">
          <SkeletonLoader v-for="i in 5" :key="i" height="40px" class="rounded-lg" />
       </div>
       
       <div v-else-if="jobList.data && jobList.data.length > 0" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-800">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Job</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Status</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Created</th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 bg-white dark:divide-gray-800 dark:bg-gray-900">
            <tr v-for="job in jobList.data" :key="job.name" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
              <td class="whitespace-nowrap px-6 py-4">
                <div class="flex flex-col">
                  <span class="font-medium text-gray-900 dark:text-white">{{ job.method }}</span>
                  <span class="text-xs text-gray-500">{{ job.name }}</span>
                </div>
              </td>
              <td class="whitespace-nowrap px-6 py-4">
                <StatusIndicator :status="job.status" />
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                {{ job.creation }}
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                <Button variant="ghost" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300" @click="handleViewLogs(job)">
                  Logs
                </Button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-12 text-center">
        <Layers class="h-10 w-10 text-gray-300 dark:text-gray-600" />
        <p class="mt-2 text-sm text-gray-500 text-gray-500 dark:text-gray-400">No jobs found</p>
      </div>
    </GlassCard>

    <Dialog
      v-if="selectedJob"
      v-model="showLogModal"
    >
      <template #body-title>
        <h3>Job Logs: {{ selectedJob.name }}</h3>
      </template>
      <template #body-content>
        <div class="mt-4 rounded-lg bg-gray-900 p-4 font-mono text-xs text-white max-h-[60vh] overflow-y-auto whitespace-pre-wrap">
          {{ selectedJob.logs || 'No logs available for this job.' }}
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import GlassCard from "@/components/ui/GlassCard.vue"
import SkeletonLoader from "@/components/ui/SkeletonLoader.vue"
import StatusIndicator from "@/components/ui/StatusIndicator.vue"
import { useJobs } from "@/composables/useJobs"
import { Layers, RefreshCcw } from "lucide-vue-next"
import { computed, ref } from "vue"

const showLogModal = ref(false)
const selectedJob = ref(null)

const { jobList } = useJobs()

const activeJobsCount = computed(() => 
  jobList.data?.filter(j => ['Queued', 'Started'].includes(j.status)).length || 0
)

const completedJobsCount = computed(() => 
  jobList.data?.filter(j => j.status === 'Finished').length || 0
)

const failedJobsCount = computed(() => 
  jobList.data?.filter(j => j.status === 'Failed').length || 0
)

function handleViewLogs(job) {
  selectedJob.value = job
  showLogModal.value = true
}
</script>
