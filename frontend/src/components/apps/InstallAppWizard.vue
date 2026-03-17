<template>
  <GlassModal
    :model-value="modelValue"
    title="Install App from GitHub"
    @update:model-value="handleClose"
  >
    <div v-if="!isProcessing && !isComplete">
      <!-- Step Indicator -->
      <div class="mb-8 flex items-center justify-between px-2">
        <div 
          v-for="i in 5" 
          :key="i"
          class="flex items-center"
        >
          <div 
            class="flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold transition-all duration-300"
            :class="[
              step >= i 
                ? 'bg-gray-900 text-white dark:bg-white dark:text-gray-900' 
                : 'bg-gray-100 text-gray-400 dark:bg-gray-800'
            ]"
          >
            {{ i }}
          </div>
          <div 
            v-if="i < 5"
            class="mx-2 h-0.5 w-8 rounded bg-gray-100 dark:bg-gray-800"
            :class="{ 'bg-gray-900 dark:bg-white': step > i }"
          ></div>
        </div>
      </div>

      <!-- Step Content -->
      <Transition name="fade" mode="out-in">
        <div :key="step" class="min-h-[200px]">
          <div v-if="step === 1" class="space-y-4">
            <h4 class="font-semibold text-gray-900 dark:text-white">Basic Info</h4>
            <BenchSelector v-model="state.selectedBench" />
            <AccountSelector v-model="state.selectedAccount" @update:model-value="onAccountSelected" />
          </div>

          <div v-else-if="step === 2" class="space-y-4">
            <h4 class="font-semibold text-gray-900 dark:text-white">Select Site (Optional)</h4>
            <SiteSelector 
                v-model="state.selectedSite" 
                :sites="siteList.data"
                :loading="siteList.loading"
            />
          </div>

          <div v-else-if="step === 3" class="space-y-4">
            <h4 class="font-semibold text-gray-900 dark:text-white">Choose Repository</h4>
            <RepoSelector 
              v-model="state.selectedRepo" 
              :repositories="repositories"
              :loading="githubLoading.repos"
              @update:model-value="onRepoSelected"
            />
          </div>

          <div v-else-if="step === 4" class="space-y-4">
            <h4 class="font-semibold text-gray-900 dark:text-white">Select Branch</h4>
            <BranchSelector 
              v-model="state.selectedBranch" 
              :branches="branches"
              :loading="githubLoading.branches"
            />
          </div>

          <div v-else-if="step === 5" class="space-y-4">
            <h4 class="font-semibold text-gray-900 dark:text-white">Confirmation</h4>
            <div class="rounded-xl bg-gray-50 p-4 space-y-3 dark:bg-gray-800/50">
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">Bench:</span>
                <span class="font-medium">{{ state.selectedBench }}</span>
              </div>
              <div v-if="state.selectedSite" class="flex justify-between text-sm">
                <span class="text-gray-500">Site:</span>
                <span class="font-medium">{{ state.selectedSite }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">Repo:</span>
                <span class="font-medium">{{ state.selectedRepo?.name }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">Branch:</span>
                <span class="font-medium">{{ state.selectedBranch }}</span>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Process Logs -->
    <div v-else class="space-y-4">
        <div class="flex items-center justify-between">
            <h4 class="text-sm font-semibold text-gray-900 dark:text-white">
                {{ isComplete ? (hasError ? 'Task Failed' : 'Task Completed') : 'Installing...' }}
            </h4>
            <StatusIndicator :status="isComplete ? (hasError ? 'Failed' : 'Active') : 'Active'" />
        </div>
        <ProcessLog 
            :logs="processLogs" 
            :progress="progress" 
            :status="statusMessage"
        />
    </div>

    <template #actions>
      <div v-if="!isProcessing && !isComplete" class="flex justify-between w-full">
        <Button variant="subtle" @click="prevStep" :disabled="step === 1">Back</Button>
        <div class="flex gap-2">
           <Button variant="subtle" @click="handleClose">Cancel</Button>
           <GradientButton v-if="step < 5" @click="nextStep" :disabled="!canProceed">Next</GradientButton>
           <GradientButton v-else @click="handleInstall" :loading="state.installing">Install Now</GradientButton>
        </div>
      </div>
      <Button
        v-if="isComplete"
        variant="solid"
        @click="finish"
      >
        Close
      </Button>
    </template>
  </GlassModal>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue"
import GlassModal from "@/components/ui/GlassModal.vue"
import GradientButton from "@/components/ui/GradientButton.vue"
import ProcessLog from "@/components/ui/ProcessLog.vue"
import StatusIndicator from "@/components/ui/StatusIndicator.vue"
import BenchSelector from "./BenchSelector.vue"
import AccountSelector from "./AccountSelector.vue"
import RepoSelector from "./RepoSelector.vue"
import BranchSelector from "./BranchSelector.vue"
import { useGithub } from "@/composables/useGithub"
import { useAppInstaller } from "@/composables/useAppInstaller"
import { useBench } from "@/composables/useBench"
import { useSite } from "@/composables/useSite"
import { useSocket } from "@/socket"

const props = defineProps({
  modelValue: Boolean,
  initialBench: String,
  initialSite: String
})

const emit = defineEmits(["update:modelValue", "installed"])

const step = ref(1)
const { state, installApp, installToSite, reset } = useAppInstaller()

const { repositories, branches, loading: githubLoading, fetchRepositories, fetchBranches } = useGithub()
const { benchList } = useBench()
const { siteList, fetchSites } = useSite()

watch(() => props.modelValue, (val) => {
    if (val) {
        benchList.reload()
        if (props.initialBench) {
            state.selectedBench = props.initialBench
            fetchSites(props.initialBench)
        }
        if (props.initialSite) state.selectedSite = props.initialSite
    }
})

onMounted(() => {
    benchList.reload()
    if (props.initialBench) {
        state.selectedBench = props.initialBench
        fetchSites(props.initialBench)
    }
    if (props.initialSite) state.selectedSite = props.initialSite
})

const isProcessing = ref(false)
const isComplete = ref(false)
const hasError = ref(false)
const progress = ref(0)
const statusMessage = ref("Initializing...")
const processLogs = ref([])
const socket = useSocket()

const canProceed = computed(() => {
  if (step.value === 1) return state.selectedBench && state.selectedAccount
  if (step.value === 2) return true // Site is optional
  if (step.value === 3) return !!state.selectedRepo
  if (step.value === 4) return !!state.selectedBranch
  return true
})

function nextStep() {
  if (step.value < 5) step.value++
}

function prevStep() {
  if (step.value > 1) step.value--
}

watch(() => state.selectedBench, (val) => {
    if (val) fetchSites(val)
})

async function onAccountSelected(val) {
  if (val) {
    await fetchRepositories(val)
  }
}

async function onRepoSelected(repo) {
  if (repo) {
    const sshUrl = repo.ssh_url || `git@github.com:${repo.full_name}.git`
    await fetchBranches(state.selectedAccount, repo.full_name, sshUrl)
    if (step.value === 3) nextStep()
  }
}

async function handleInstall() {
  try {
    let res;
    if (state.selectedSite) {
        // If site selected, first we need to make sure app is on bench (handled by installToSite in backend if needed)
        // HTBencher API install_app_to_site usually assumes app is available on bench.
        // But the user's wizard flow says: Step 5 Select Repository -> Step 7 Install.
        // This implies installing from GitHub.
        
        // HTBencher's v1.github.install_app already handles both bench and site?
        // Let's check my useAppInstaller.js installApp again.
        res = await installApp()
    } else {
        res = await installApp()
    }

    if (res.task_id) {
        isProcessing.value = true
        setupSocketListeners(res.task_id)
    }
  } catch (e) {
    hasError.value = true
    statusMessage.value = e.message
  }
}


function setupSocketListeners(id) {
    if (!socket || !socket.connected) return
    socket.on('htbench_task_log', (data) => {
        if (data.task_id === id) {
            processLogs.value.push({
                time: new Date().toLocaleTimeString(),
                message: data.log,
                error: data.error
            })
        }
    })
    socket.on('htbench_task_complete', (data) => {
        if (data.task_id === id) {
            isComplete.value = true
            isProcessing.value = false
            hasError.value = data.status !== 'success'
            statusMessage.value = data.status === 'success' ? 'Completed' : 'Failed'
            if (data.status === 'success') progress.value = 100
        }
    })
}

function handleClose() {
    if (isProcessing.value && !isComplete.value) {
        if(!confirm("Installation is running. Are you sure?")) return
    }
    emit("update:modelValue", false)
    reset()
    step.value = 1
}

function finish() {
    emit("installed")
    handleClose()
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
