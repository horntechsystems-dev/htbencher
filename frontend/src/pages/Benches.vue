<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Benches</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">Manage your Frappe Bench environments.</p>
      </div>
      <GradientButton @click="showCreateModal = true">
        <Plus class="mr-2 h-4 w-4" />
        New Bench
      </GradientButton>
    </div>

    <!-- Bench List -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
      <GlassCard
        v-for="bench in benchList.data"
        :key="bench.name"
        class="group relative overflow-hidden transition-all hover:-translate-y-1 hover:shadow-2xl cursor-pointer"
        @click="$router.push({ name: 'BenchDetails', params: { id: bench.name } })"
      >
        <div class="absolute top-0 right-0 p-4">
          <StatusIndicator :status="bench.status || 'Unknown'" />
        </div>

        <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gray-900 text-white shadow-lg dark:bg-white dark:text-gray-900">
          <Terminal class="h-6 w-6" />
        </div>

        <h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ bench.name }}</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ bench.path }}</p>

        <div class="mt-6 space-y-3">
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-500 dark:text-gray-400">Sites</span>
            <span class="font-medium text-gray-900 dark:text-white">{{ bench.total_sites || 0 }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-500 dark:text-gray-400">Apps</span>
            <span class="font-medium text-gray-900 dark:text-white">{{ bench.total_apps || 0 }}</span>
          </div>
        </div>

        <div class="mt-6 flex gap-2">
          <Button
            variant="subtle"
            class="flex-1 flex items-center justify-center"
            @click="handleViewLogs(bench)"
          >
            <span class="whitespace-nowrap">Logs</span>
          </Button>
          <Button
            variant="solid"
            class="flex-1 flex items-center justify-center bg-gray-900 text-white hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100"
            :loading="state.restarting === bench.name"
            @click="handleRestart(bench)"
          >
            <span class="whitespace-nowrap">Restart</span>
          </Button>
        </div>
      </GlassCard>

      <!-- Empty State -->
      <div v-if="!benchList.data?.length && !benchList.loading" class="col-span-full flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-gray-200 py-20 text-center dark:border-gray-700">
        <div class="flex h-16 w-16 items-center justify-center rounded-full bg-gray-50 dark:bg-gray-800">
          <Terminal class="h-8 w-8 text-gray-400 dark:text-gray-500" />
        </div>
        <h3 class="mt-4 text-lg font-semibold text-gray-900 dark:text-white">No benches found</h3>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Get started by creating your first bench environment.</p>
        <GradientButton class="mt-6" @click="showCreateModal = true">
          Create Bench
        </GradientButton>
      </div>

      <!-- Loading State -->
      <div v-if="benchList.loading" class="col-span-full grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
        <SkeletonLoader v-for="i in 3" :key="i" height="280px" class="rounded-2xl" />
      </div>
    </div>

    <BenchLogModal
      v-if="selectedBench"
      v-model="showLogModal"
      :bench="selectedBench"
    />

    <CreateBenchModal
      v-model="showCreateModal"
      @created="benchList.reload()"
    />
  </div>
</template>

<script setup>
import BenchLogModal from "@/components/benches/BenchLogModal.vue"
import CreateBenchModal from "@/components/benches/CreateBenchModal.vue"
import GlassCard from "@/components/ui/GlassCard.vue"
import GradientButton from "@/components/ui/GradientButton.vue"
import SkeletonLoader from "@/components/ui/SkeletonLoader.vue"
import StatusIndicator from "@/components/ui/StatusIndicator.vue"
import { useBench } from "@/composables/useBench"
import { Plus, Terminal } from "lucide-vue-next"
import { onMounted, ref } from "vue"
 
const showCreateModal = ref(false)
const showLogModal = ref(false)
const selectedBench = ref(null)
 
const { benchList, restart, state } = useBench()

onMounted(() => {
  benchList.reload()
})

async function handleRestart(bench) {
  await restart(bench.name)
}

function handleViewLogs(bench) {
  selectedBench.value = bench
  showLogModal.value = true
}
</script>
