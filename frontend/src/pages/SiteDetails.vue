
<template>
  <div v-if="site" class="space-y-6">
    <div class="flex items-center gap-4">
        <button @click="$router.back()" class="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">
            <ArrowLeft class="h-5 w-5" />
        </button>
        <div>
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ site.site_name }}</h2>
            <div class="flex items-center gap-2 text-sm text-gray-500">
                <span class="font-mono text-xs">{{ site.name }}</span>
                <span>&bull;</span>
                <span class="flex items-center gap-1">
                    <Database class="h-3 w-3" />
                    {{ site.bench }}
                </span>
            </div>
        </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-100 dark:border-gray-800">
        <nav class="flex gap-8">
            <button 
                v-for="tab in tabs" 
                :key="tab.id"
                @click="activeTab = tab.id"
                class="pb-4 text-sm font-medium transition-all relative"
                :class="[
                    activeTab === tab.id 
                    ? 'text-gray-900 dark:text-white' 
                    : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                ]"
            >
                {{ tab.name }}
                <div v-if="activeTab === tab.id" class="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-900 dark:bg-white rounded-full"></div>
            </button>
        </nav>
    </div>

    <!-- Tab Content -->
    <div v-if="activeTab === 'overview'" class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatsCard label="Domain" :value="site.root_domain || 'None'" :icon="Globe" />
        <StatsCard label="Bench" :value="site.bench" :icon="Terminal" />
        <StatsCard label="Apps" :value="siteApps.length" :icon="Package" />
    </div>

    <div v-else-if="activeTab === 'apps'" class="space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white shrink-0">Site Apps</h3>
            <div class="flex flex-col sm:flex-row flex-wrap gap-2 w-full sm:w-auto">
                <Button variant="subtle" class="w-full sm:w-auto flex items-center justify-center" @click="showBenchInstallModal = true">
                    <span class="whitespace-nowrap">Install from Bench</span>
                </Button>
                <GradientButton class="w-full sm:w-auto flex items-center justify-center" @click="showInstallWizard = true">
                    <Plus class="mr-2 h-4 w-4" />
                    <span class="whitespace-nowrap">Install from GitHub</span>
                </GradientButton>
            </div>
        </div>

        <div v-if="loading.apps" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SkeletonLoader v-for="i in 2" :key="i" height="80px" />
        </div>
        <div v-else-if="siteApps.length === 0" class="p-12 text-center rounded-2xl border-2 border-dashed border-gray-100 dark:border-gray-800">
            <Package class="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h4 class="text-gray-900 dark:text-white font-medium">No Apps on Site</h4>
            <p class="text-sm text-gray-500 mt-1">This site doesn't have any apps installed yet.</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <GlassCard v-for="app in siteApps" :key="app">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 -m-2">
                    <div class="flex items-center gap-3 overflow-hidden">
                        <div class="h-8 w-8 flex-shrink-0 rounded-lg bg-gray-100 flex items-center justify-center dark:bg-gray-800">
                            <Package class="h-4 w-4 text-gray-500" />
                        </div>
                        <div class="min-w-0">
                            <div class="font-bold text-gray-900 dark:text-white truncate">{{ app }}</div>
                        </div>
                    </div>
                    <Button variant="subtle" class="text-red-500 text-xs px-2 py-1 flex-shrink-0 w-full sm:w-auto flex items-center justify-center" @click="handleUninstall(app)">
                        Uninstall
                    </Button>
                </div>
            </GlassCard>
        </div>
    </div>

    <!-- Modals -->
    <InstallAppWizard 
        v-model="showInstallWizard" 
        :initial-bench="site.bench"
        :initial-site="site.name"
        @installed="fetchSiteApps(site.name)"
    />

    <InstallBenchAppToSiteModal
        v-model="showBenchInstallModal"
        :bench-name="site.bench"
        :site-name="site.name"
        @installed="fetchSiteApps(site.name)"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import { useRoute } from "vue-router"
import { useSite } from "@/composables/useSite"
import { useAppInstaller } from "@/composables/useAppInstaller"
import { ArrowLeft, Package, Globe, Terminal, Plus, Database } from "lucide-vue-next"
import GlassCard from "@/components/ui/GlassCard.vue"
import GradientButton from "@/components/ui/GradientButton.vue"
import StatsCard from "@/components/ui/StatsCard.vue"
import SkeletonLoader from "@/components/ui/SkeletonLoader.vue"
import InstallAppWizard from "@/components/apps/InstallAppWizard.vue"
import InstallBenchAppToSiteModal from "@/components/sites/InstallBenchAppToSiteModal.vue"

const route = useRoute()
const { siteList, fetchSiteApps, siteApps, loading } = useSite()
const { uninstallFromSite } = useAppInstaller()

const activeTab = ref('apps')
const showInstallWizard = ref(false)
const showBenchInstallModal = ref(false)

const tabs = [
    { id: 'overview', name: 'Overview' },
    { id: 'apps', name: 'Apps' }
]

const site = computed(() => siteList.data.find(s => s.name === route.params.id))

onMounted(async () => {
    await siteList.reload()
    if (site.value) {
        await fetchSiteApps(site.value.name)
    }
})

async function handleUninstall(appName) {
    if (confirm(`Are you sure you want to uninstall ${appName} from this site?`)) {
        await uninstallFromSite(site.value.name, appName)
        await fetchSiteApps(site.value.name)
    }
}
</script>
