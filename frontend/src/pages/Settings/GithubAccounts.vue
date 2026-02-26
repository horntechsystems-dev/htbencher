<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">GitHub Accounts</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">Manage your GitHub SSH accounts for app installations.</p>
      </div>
      <GradientButton @click="showAddModal = true">
        <Plus class="mr-2 h-4 w-4" />
        Add Account
      </GradientButton>
    </div>

    <!-- Accounts List -->
    <div v-if="accounts.length" class="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
      <GithubAccountCard
        v-for="account in accounts"
        :key="account.name"
        :account="account"
        @copy-public-key="handleCopyPublicKey"
      />
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading.accounts" class="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-gray-200 py-20 text-center dark:border-gray-700">
      <div class="flex h-16 w-16 items-center justify-center rounded-full bg-gray-50 dark:bg-gray-800">
        <Github class="h-8 w-8 text-gray-400 dark:text-gray-500" />
      </div>
      <h3 class="mt-4 text-lg font-semibold text-gray-900 dark:text-white">No accounts found</h3>
      <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Add your first GitHub account to start installing private apps.</p>
      <GradientButton class="mt-6" @click="showAddModal = true">
        Add GitHub Account
      </GradientButton>
    </div>

    <!-- Loading State -->
    <div v-if="loading.accounts" class="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
      <SkeletonLoader v-for="i in 3" :key="i" height="200px" class="rounded-2xl" />
    </div>

    <AddGithubAccountModal
      v-model="showAddModal"
      :loading="loading.addingAccount"
      @submit="handleAddAccount"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { Plus, Github } from "lucide-vue-next"
import GradientButton from "@/components/ui/GradientButton.vue"
import SkeletonLoader from "@/components/ui/SkeletonLoader.vue"
import GithubAccountCard from "@/components/github/GithubAccountCard.vue"
import AddGithubAccountModal from "@/components/github/AddGithubAccountModal.vue"
import { useGithub } from "@/composables/useGithub"

const showAddModal = ref(false)
const { accounts, loading, fetchAccounts, addAccount } = useGithub()

onMounted(() => {
  fetchAccounts()
})

async function handleAddAccount(form) {
  try {
    await addAccount(form)
    showAddModal.value = false
  } catch (err) {
    console.error("Failed to add account", err)
  }
}

function handleCopyPublicKey(account) {
  // Logic to show public key in a modal or copy it
  navigator.clipboard.writeText(account.ssh_public_key)
  alert("Public key copied to clipboard! Add it to your GitHub account settings.")
}
</script>
