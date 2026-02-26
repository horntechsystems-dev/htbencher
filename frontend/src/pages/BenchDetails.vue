
<template>
  <div v-if="bench" class="space-y-6">
    <div class="flex items-center gap-4">
        <button @click="$router.back()" class="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">
            <ArrowLeft class="h-5 w-5" />
        </button>
        <div>
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ bench.name }}</h2>
            <div class="flex items-center gap-2 text-sm text-gray-500">
                <span class="font-mono">{{ bench.path }}</span>
                <span>&bull;</span>
                <StatusIndicator :status="bench.status" />
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
        <StatsCard label="Sites" :value="bench.total_sites || 0" :icon="Globe" />
        <StatsCard label="Apps" :value="bench.total_apps || 0" :icon="Package" />
        <StatsCard label="Python" :value="bench.python_version || '3.11'" :icon="Terminal" />
    </div>

    <div v-else-if="activeTab === 'apps'" class="space-y-6">
        <div class="flex items-center justify-between">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white">Installed Apps</h3>
            <GradientButton @click="showInstallWizard = true">
                <Plus class="mr-2 h-4 w-4" />
                Install App
            </GradientButton>
        </div>

        <div v-if="loading.apps" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SkeletonLoader v-for="i in 2" :key="i" height="100px" />
        </div>
        <div v-else-if="benchApps.length === 0" class="p-12 text-center rounded-2xl border-2 border-dashed border-gray-100 dark:border-gray-800">
            <Package class="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h4 class="text-gray-900 dark:text-white font-medium">No Apps Installed</h4>
            <p class="text-sm text-gray-500 mt-1">This bench doesn't have any apps yet.</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <GlassCard v-for="app in benchApps" :key="app" class="flex items-center justify-between p-4">
                <div class="flex items-center gap-4">
                    <div class="h-10 w-10 rounded-lg bg-gray-100 flex items-center justify-center dark:bg-gray-800">
                        <Package class="h-5 w-5 text-gray-500" />
                    </div>
                    <div>
                        <div class="font-bold text-gray-900 dark:text-white">{{ app }}</div>
                        <div class="text-xs text-gray-500">Installed</div>
                    </div>
                </div>
                <Button variant="subtle" class="text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20" @click="handleUninstall(app)">
                    Uninstall
                </Button>
            </GlassCard>
        </div>
    </div>

    <InstallAppWizard 
        v-model="showInstallWizard" 
        :initial-bench="bench.name"
        @installed="fetchBenchApps(bench.name)"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import { useRoute } from "vue-router"
import { useBench } from "@/composables/useBench"
import { useAppInstaller } from "@/composables/useAppInstaller"
import { ArrowLeft, Package, Globe, Terminal, Plus } from "lucide-vue-next"
import GlassCard from "@/components/ui/GlassCard.vue"
import GradientButton from "@/components/ui/GradientButton.vue"
import StatsCard from "@/components/ui/StatsCard.vue"
import StatusIndicator from "@/components/ui/StatusIndicator.vue"
import SkeletonLoader from "@/components/ui/SkeletonLoader.vue"
import InstallAppWizard from "@/components/apps/InstallAppWizard.vue"

const route = useRoute()
const { benchList, fetchBenchApps, benchApps, loading } = useBench()
const { uninstallFromBench } = useAppInstaller()

const activeTab = ref('apps')
const showInstallWizard = ref(false)

const tabs = [
    { id: 'overview', name: 'Overview' },
    { id: 'apps', name: 'Apps' },
    { id: 'logs', name: 'Logs' }
]

const bench = computed(() => benchList.data.find(b => b.name === route.params.id))

onMounted(async () => {
    await benchList.reload()
    if (bench.value) {
        await fetchBenchApps(bench.value.name)
    }
})

async function handleUninstall(appName) {
    if (confirm(`Are you sure you want to uninstall ${appName}?`)) {
        await uninstallFromBench(bench.value.name, appName)
        await fetchBenchApps(bench.value.name)
    }
}
</script>
