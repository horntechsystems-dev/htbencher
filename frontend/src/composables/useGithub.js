
import { ref } from "vue"
import { github } from "@/services/htbencherApi"

export function useGithub() {
    const accounts = ref([])
    const repositories = ref([])
    const branches = ref([])
    const loading = ref({
        accounts: false,
        repos: false,
        branches: false,
        addingAccount: false
    })

    async function fetchAccounts() {
        loading.value.accounts = true
        try {
            const response = await github.getAccounts()
            accounts.value = response
        } finally {
            loading.value.accounts = false
        }
    }

    async function addAccount(data) {
        loading.value.addingAccount = true
        try {
            await github.addAccount(data)
            await fetchAccounts()
        } finally {
            loading.value.addingAccount = false
        }
    }

    async function fetchRepositories(accountName) {
        loading.value.repos = true
        try {
            const response = await github.getRepos(accountName)
            repositories.value = response
        } finally {
            loading.value.repos = false
        }
    }

    async function fetchBranches(accountName, repoFullName, repoSshUrl) {
        loading.value.branches = true
        try {
            const response = await github.getBranches(accountName, repoFullName, repoSshUrl)
            branches.value = response
        } finally {
            loading.value.branches = false
        }
    }

    return {
        accounts,
        repositories,
        branches,
        loading,
        fetchAccounts,
        addAccount,
        fetchRepositories,
        fetchBranches
    }
}
