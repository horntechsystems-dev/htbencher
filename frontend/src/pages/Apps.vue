<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Applications</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">Manage installed applications across benches.</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <Button variant="subtle" @click="showGithubInstallModal = true">
          <Github class="mr-2 h-4 w-4" />
          GitHub
        </Button>
        <GradientButton @click="showInstallModal = true">
          <Download class="mr-2 h-4 w-4" />
          Install App
        </GradientButton>
      </div>
    </div>

    <!-- Search -->
    <div class="relative max-w-md">
      <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search apps..."
        class="w-full rounded-xl border-gray-200 bg-white py-2.5 pl-10 text-sm shadow-sm transition-all focus:border-gray-900 focus:ring-gray-900 dark:border-gray-800 dark:bg-gray-800/50 dark:text-white dark:focus:border-white dark:focus:ring-white"
      />
    </div>

    <!-- App List -->
    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
      <GlassCard
        v-for="app in filteredApps"
        :key="app.name"
        class="group relative overflow-hidden transition-all hover:-translate-y-1 hover:shadow-2xl"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-pink-100 text-pink-600 dark:bg-pink-900/20 dark:text-pink-400">
              <Package class="h-5 w-5" />
            </div>
            <div>
              <h3 class="font-bold text-gray-900 dark:text-white">{{ app.title || app.app_title || app.app_name }}</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400">v{{ app.version || app.app_version || '0.0.1' }}</p>
            </div>
          </div>
          <div class="flex gap-1">
             <Button variant="ghost" class="h-8 w-8 p-0 text-gray-400 hover:text-gray-900 dark:hover:text-white">
                <MoreVertical class="h-4 w-4" />
             </Button>
          </div>
        </div>

        <p class="mt-4 line-clamp-2 text-sm text-gray-600 dark:text-gray-300">
          {{ app.description || app.app_description || 'No description provided.' }}
        </p>

        <div class="mt-4 flex items-center justify-between border-t border-gray-100 pt-4 dark:border-gray-800">
          <span class="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-400">
            {{ app.app_name }}
          </span>
          <div class="flex gap-2">
            <button
               class="text-xs font-medium text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
               @click="handleUpdate(app)"
            >
              Check Updates
            </button>
          </div>
        </div>
      </GlassCard>

      <!-- Empty State -->
      <div v-if="!appList.data?.length && !appList.loading" class="col-span-full flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-gray-200 py-20 text-center dark:border-gray-700">
        <div class="flex h-16 w-16 items-center justify-center rounded-full bg-gray-50 dark:bg-gray-800">
          <Package class="h-8 w-8 text-gray-400 dark:text-gray-500" />
        </div>
        <h3 class="mt-4 text-lg font-semibold text-gray-900 dark:text-white">No apps installed</h3>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Install apps to extend functionality.</p>
        <GradientButton class="mt-6" @click="showInstallModal = true">
          Install App
        </GradientButton>
      </div>

      <!-- Loading State -->
      <div v-if="appList.loading" class="col-span-full grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <SkeletonLoader v-for="i in 3" :key="i" height="200px" class="rounded-2xl" />
      </div>
    </div>

    <InstallAppModal
      v-model="showInstallModal"
      @installed="appList.reload()"
    />

    <InstallAppWizard
      v-model="showGithubInstallModal"
      @installed="appList.reload()"
    />
  </div>
</template>

<script setup>
import InstallAppModal from "@/components/apps/InstallAppModal.vue"
import InstallAppWizard from "@/components/apps/InstallAppWizard.vue"
import GlassCard from "@/components/ui/GlassCard.vue"
import GradientButton from "@/components/ui/GradientButton.vue"
import SkeletonLoader from "@/components/ui/SkeletonLoader.vue"
import { useApp } from "@/composables/useApp"
import { Download, Github, MoreVertical, Package, Search } from "lucide-vue-next"
import { computed, ref } from "vue"

const showInstallModal = ref(false)
const showGithubInstallModal = ref(false)
const searchQuery = ref("")

const { appList } = useApp()

const filteredApps = computed(() => {
  if (!appList.data) return []
  if (!searchQuery.value) return appList.data
  
  const query = searchQuery.value.toLowerCase()
  return appList.data.filter(app => 
    (app.app_name?.toLowerCase().includes(query)) ||
    (app.app_title?.toLowerCase().includes(query))
  )
})

function handleUpdate(app) {
  console.log("Updating app:", app.name)
}

function handleUninstall(app) {
  console.log("Uninstalling app:", app.name)
}
</script>
