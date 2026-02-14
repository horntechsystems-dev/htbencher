import { ref, reactive, computed } from "vue"
import { sites } from "@/services/htbencherApi"

export function useSite() {
    const data = ref([])
    const siteApps = ref([])
    const loading = reactive({
        list: false,
        apps: false
    })
    const state = reactive({
        backingUp: null
    })

    const siteList = reactive({
        data,
        loading: computed(() => loading.list),
        reload: fetchSites
    })

    async function fetchSites(benchName = null) {
        loading.list = true
        try {
            const response = await sites.getAll(benchName)
            data.value = response
        } finally {
            loading.list = false
        }
    }

    async function fetchSiteApps(siteName) {
        loading.apps = true
        try {
            const response = await sites.getInstalledApps(siteName)
            siteApps.value = response
        } finally {
            loading.apps = false
        }
    }

    async function backup(benchName) {
        state.backingUp = benchName
        try {
            await sites.backup(benchName)
        } finally {
            state.backingUp = null
        }
    }

    return {
        siteList,
        siteApps,
        loading,
        state,
        fetchSites,
        fetchSiteApps,
        backup
    }
}
