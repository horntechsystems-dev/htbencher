
import { ref, reactive } from "vue"
import { github, apps } from "@/services/htbencherApi"

export function useAppInstaller() {
    const state = reactive({
        selectedBench: null,
        selectedAccount: null,
        selectedRepo: null,
        selectedBranch: null,
        selectedSite: null,
        installing: false,
        taskId: null
    })

    async function installApp() {
        state.installing = true
        try {
            const response = await github.installApp({
                bench_name: state.selectedBench,
                account_name: state.selectedAccount,
                repo_full_name: state.selectedRepo.full_name,
                repo_ssh_url: state.selectedRepo.ssh_url,
                branch: state.selectedBranch
            })
            state.taskId = response.task_id
            return response
        } finally {
            state.installing = false
        }
    }

    async function installToSite(siteName, appName) {
        state.installing = true
        try {
            const response = await apps.installToSite(siteName, appName)
            state.taskId = response.task_id
            return response
        } finally {
            state.installing = false
        }
    }

    async function uninstallFromBench(benchName, appName) {
        state.installing = true
        try {
            const response = await apps.uninstallFromBench(benchName, appName)
            state.taskId = response.task_id
            return response
        } finally {
            state.installing = false
        }
    }

    async function uninstallFromSite(siteName, appName) {
        state.installing = true
        try {
            const response = await apps.uninstallFromSite(siteName, appName)
            state.taskId = response.task_id
            return response
        } finally {
            state.installing = false
        }
    }

    function reset() {
        state.selectedBench = null
        state.selectedAccount = null
        state.selectedRepo = null
        state.selectedBranch = null
        state.selectedSite = null
        state.taskId = null
    }

    return {
        state,
        installApp,
        installToSite,
        uninstallFromBench,
        uninstallFromSite,
        reset
    }
}
