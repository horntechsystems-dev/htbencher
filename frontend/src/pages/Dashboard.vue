<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400">Overview of your hosting infrastructure.</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="flex h-2 w-2 rounded-full bg-green-500"></span>
        <span class="text-xs font-medium text-gray-600 dark:text-gray-300">System Operational</span>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <GlassCard class="relative overflow-hidden">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Benches</p>
            <h3 class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
              <span v-if="systemStatus.loading">...</span>
              <span v-else>{{ systemStatus.data?.total_benches || 0 }}</span>
            </h3>
          </div>
          <div class="rounded-lg bg-blue-50 p-2 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400">
            <Terminal class="h-6 w-6" />
          </div>
        </div>
        <div class="mt-4 flex items-center text-xs text-green-600 dark:text-green-400">
          <ArrowUpRight class="mr-1 h-3 w-3" />
          <span>Active</span>
        </div>
      </GlassCard>

      <GlassCard>
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Sites</p>
            <h3 class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
              <span v-if="systemStatus.loading">...</span>
              <span v-else>{{ systemStatus.data?.total_sites || 0 }}</span>
            </h3>
          </div>
          <div class="rounded-lg bg-purple-50 p-2 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400">
            <Globe class="h-6 w-6" />
          </div>
        </div>
        <div class="mt-4 flex items-center text-xs text-gray-500 dark:text-gray-400">
          <span>Across all benches</span>
        </div>
      </GlassCard>

      <GlassCard>
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Apps</p>
            <h3 class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
              <span v-if="systemStatus.loading">...</span>
              <span v-else>{{ systemStatus.data?.total_apps || 0 }}</span>
            </h3>
          </div>
          <div class="rounded-lg bg-pink-50 p-2 text-pink-600 dark:bg-pink-900/20 dark:text-pink-400">
            <Package class="h-6 w-6" />
          </div>
        </div>
      </GlassCard>

      <GlassCard>
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Server Load</p>
            <h3 class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
              <span v-if="systemStatus.loading">...</span>
              <span v-else>{{ systemStatus.data?.server_load || 0 }}%</span>
            </h3>
          </div>
          <div class="rounded-lg bg-orange-50 p-2 text-orange-600 dark:bg-orange-900/20 dark:text-orange-400">
            <Cpu class="h-6 w-6" />
          </div>
        </div>
        <div class="mt-4 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
          <div
            class="h-full rounded-full bg-orange-500 transition-all duration-500"
            :style="{ width: (systemStatus.data?.server_load || 0) + '%' }"
          ></div>
        </div>
      </GlassCard>
    </div>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- System Health -->
      <GlassCard>
        <div class="mb-6 flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">System Health</h3>
          <Button variant="ghost" class="text-xs">View Logs</Button>
        </div>
        <div class="space-y-4">
          <div class="flex items-center justify-between rounded-lg border border-gray-100 p-3 transition-colors hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-gray-800/50">
            <div class="flex items-center gap-3">
              <div class="rounded-md bg-gray-100 p-2 dark:bg-gray-800">
                <Server class="h-4 w-4 text-gray-600 dark:text-gray-300" />
              </div>
              <div>
                <p class="text-sm font-medium text-gray-900 dark:text-white">Background Workers</p>
                <p class="text-xs text-gray-500">Processing background jobs</p>
              </div>
            </div>
            <StatusIndicator :status="systemStatus.data?.workers_status || 'Stopped'" />
          </div>

          <div class="flex items-center justify-between rounded-lg border border-gray-100 p-3 transition-colors hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-gray-800/50">
            <div class="flex items-center gap-3">
              <div class="rounded-md bg-gray-100 p-2 dark:bg-gray-800">
                <Clock class="h-4 w-4 text-gray-600 dark:text-gray-300" />
              </div>
              <div>
                <p class="text-sm font-medium text-gray-900 dark:text-white">Scheduler</p>
                <p class="text-xs text-gray-500">Triggering scheduled events</p>
              </div>
            </div>
            <StatusIndicator :status="systemStatus.data?.scheduler_status || 'Stopped'" />
          </div>

          <div class="flex items-center justify-between rounded-lg border border-gray-100 p-3 transition-colors hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-gray-800/50">
            <div class="flex items-center gap-3">
              <div class="rounded-md bg-gray-100 p-2 dark:bg-gray-800">
                <Database class="h-4 w-4 text-gray-600 dark:text-gray-300" />
              </div>
              <div>
                <p class="text-sm font-medium text-gray-900 dark:text-white">Redis Cache</p>
                <p class="text-xs text-gray-500">In-memory data store</p>
              </div>
            </div>
            <StatusIndicator :status="systemStatus.data?.redis_status || 'Stopped'" />
          </div>
        </div>
      </GlassCard>

      <!-- Active Queues -->
      <GlassCard>
        <div class="mb-6 flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Job Queues</h3>
          <span class="text-xs text-gray-500">Real-time</span>
        </div>
        <div class="space-y-6">
          <div v-if="!systemStatus.data?.queues" class="flex flex-col items-center justify-center py-8 text-center">
            <Layers class="mb-3 h-10 w-10 text-gray-300 dark:text-gray-600" />
            <p class="text-sm text-gray-500">No active queues found</p>
          </div>
          
          <div v-else v-for="(queue, name) in systemStatus.data.queues" :key="name" class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="font-medium text-gray-700 dark:text-gray-300 capitalize">{{ name }}</span>
              <span class="text-gray-500">{{ queue.count }} jobs</span>
            </div>
            <div class="h-2 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
              <div
                class="h-full rounded-full bg-gray-900 transition-all duration-500 dark:bg-white"
                :style="{ width: Math.min(100, (queue.count / 50) * 100) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </GlassCard>
    </div>
  </div>
</template>

<script setup>
import GlassCard from "@/components/ui/GlassCard.vue"
import StatusIndicator from "@/components/ui/StatusIndicator.vue"
import { createResource } from "frappe-ui"
import {
	ArrowUpRight,
	Clock,
	Cpu,
	Database,
	Globe,
	Layers,
	Package,
	Server,
	Terminal,
} from "lucide-vue-next"
import { computed } from "vue"

const systemStatus = createResource({
	url: 'htbencher.api.get_system_status',
	auto: true,
})
</script>
