import { ref, reactive, computed } from "vue"
import { benches } from "@/services/htbencherApi"

export function useBench() {
    const data = ref([])
    const benchApps = ref([])
    const loading = reactive({
        list: false,
        apps: false
    })
    const state = reactive({
        restarting: null
    })

    const benchList = reactive({
        data,
        loading: computed(() => loading.list),
        reload: fetchBenches
    })

    async function fetchBenches() {
        loading.list = true
        try {
            const response = await benches.getAll()
            data.value = response
        } finally {
            loading.list = false
        }
    }

    async function fetchBenchApps(benchName) {
        loading.apps = true
        try {
            const response = await benches.getInstalledApps(benchName)
            benchApps.value = response
        } finally {
            loading.apps = false
        }
    }

    async function restart(benchName) {
        state.restarting = benchName
        try {
            await benches.restart(benchName)
        } finally {
            state.restarting = null
        }
    }

    return {
        benchList,
        benchApps,
        loading,
        state,
        fetchBenches,
        fetchBenchApps,
        restart
    }
}
