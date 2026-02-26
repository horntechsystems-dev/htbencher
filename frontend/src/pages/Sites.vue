<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Sites</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">Manage your Frappe sites and domains.</p>
      </div>
      <GradientButton @click="showCreateModal = true">
        <Plus class="mr-2 h-4 w-4" />
        New Site
      </GradientButton>
    </div>

    <!-- Site List -->
    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
      <GlassCard
        v-for="site in siteList.data"
        :key="site.name"
        class="group relative overflow-hidden transition-all hover:-translate-y-1 hover:shadow-2xl cursor-pointer"
        @click="$router.push({ name: 'SiteDetails', params: { id: site.name } })"
      >
        <div class="absolute top-0 right-0 p-4">
          <StatusIndicator :status="site.status || 'Active'" />
        </div>

        <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-purple-600 text-white shadow-lg dark:bg-purple-500">
          <Globe class="h-6 w-6" />
        </div>

        <h3 class="text-lg font-bold text-gray-900 dark:text-white truncate" :title="site.name">
          {{ site.site_name || site.name }}
        </h3>
        <a
          v-if="site.url"
          :href="site.url"
          target="_blank"
          class="mt-1 flex items-center text-sm text-purple-600 hover:underline dark:text-purple-400"
        >
          {{ site.url }}
          <ExternalLink class="ml-1 h-3 w-3" />
        </a>
        <p v-else class="mt-1 text-sm text-gray-500 italic">No URL configured</p>

        <div class="mt-4 flex items-center text-sm text-gray-500 dark:text-gray-400">
          <Terminal class="mr-2 h-4 w-4" />
          <span>{{ site.bench }}</span>
        </div>

        <div class="mt-6 flex gap-2">
          <Button
            variant="subtle"
            class="flex-1 flex items-center justify-center"
            :loading="state.backingUp === site.bench"
            @click="handleBackup(site)"
          >
            <span class="whitespace-nowrap">Backup</span>
          </Button>
          <Button
            variant="outline"
            class="flex-1 flex items-center justify-center text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
            @click="handleDelete(site)"
          >
            <span class="whitespace-nowrap">Delete</span>
          </Button>
        </div>
      </GlassCard>

      <!-- Empty State -->
      <div v-if="!siteList.data?.length && !siteList.loading" class="col-span-full flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-gray-200 py-20 text-center dark:border-gray-700">
        <div class="flex h-16 w-16 items-center justify-center rounded-full bg-gray-50 dark:bg-gray-800">
          <Globe class="h-8 w-8 text-gray-400 dark:text-gray-500" />
        </div>
        <h3 class="mt-4 text-lg font-semibold text-gray-900 dark:text-white">No sites found</h3>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Create a new site to get started.</p>
        <GradientButton class="mt-6" @click="showCreateModal = true">
          Create Site
        </GradientButton>
      </div>

      <!-- Loading State -->
      <div v-if="siteList.loading" class="col-span-full grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <SkeletonLoader v-for="i in 3" :key="i" height="240px" class="rounded-2xl" />
      </div>
    </div>

    <CreateSiteModal
      v-model="showCreateModal"
      @created="siteList.reload()"
    />
  </div>
</template>

<script setup>
import CreateSiteModal from "@/components/sites/CreateSiteModal.vue"
import GlassCard from "@/components/ui/GlassCard.vue"
import GradientButton from "@/components/ui/GradientButton.vue"
import SkeletonLoader from "@/components/ui/SkeletonLoader.vue"
import StatusIndicator from "@/components/ui/StatusIndicator.vue"
import { useSite } from "@/composables/useSite"
import { ExternalLink, Globe, Plus, Terminal } from "lucide-vue-next"
import { onMounted, ref } from "vue"

const showCreateModal = ref(false)
const { siteList, backup, state } = useSite()

onMounted(() => {
  siteList.reload()
})

async function handleBackup(site) {
  await backup(site.bench)
}

function handleDelete(site) {
  // Implement delete logic with confirmation
  console.log("Deleting site:", site.name)
}
</script>
