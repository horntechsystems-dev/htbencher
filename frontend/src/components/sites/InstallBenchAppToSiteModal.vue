<template>
  <GlassModal
    :model-value="modelValue"
    title="Install App from Bench"
    @update:model-value="handleClose"
  >
    <div v-if="!isProcessing && !isComplete">
        <div class="space-y-4">
            <p class="text-sm text-gray-500 dark:text-gray-400">
                Install an application that is already available on the <strong>{{ benchName }}</strong> bench to the site <strong>{{ siteName }}</strong>.
            </p>

            <div v-if="loadingApps" class="py-4 text-center">
                <p class="text-sm text-gray-500">Loading available apps...</p>
            </div>
            
            <div v-else-if="appOptions.length === 0" class="py-4 text-center">
                <p class="text-sm text-red-500">No available apps found on this bench.</p>
            </div>

            <GlassSelect
              v-else
              v-model="selectedApp"
              label="Select App"
              :options="appOptions"
              placeholder="Choose an app..."
              required
            />
        </div>
    </div>

    <!-- Processing state -->
    <div v-else class="space-y-4">
        <div class="flex items-center justify-between">
            <h4 class="text-sm font-semibold text-gray-900 dark:text-white">
                {{ isComplete ? (hasError ? 'Task Failed' : 'Task Completed') : 'Installing App...' }}
            </h4>
            <StatusIndicator :status="isComplete ? (hasError ? 'Failed' : 'Active') : 'Active'" />
        </div>
        
        <ProcessLog 
            :logs="logs" 
            :progress="progress" 
            :status="statusMessage"
        />
        
        <div v-if="isComplete" class="rounded-lg bg-green-50 p-4 text-sm text-green-700 dark:bg-green-900/30 dark:text-green-400" :class="{'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400': hasError}">
            {{ hasError ? 'Installation failed. Check logs.' : 'App installed successfully!' }}
        </div>
    </div>

    <template #actions>
      <Button
        v-if="!isProcessing && !isComplete"
        variant="subtle"
        @click="handleClose"
      >
        Cancel
      </Button>
      
      <GradientButton
        v-if="!isProcessing && !isComplete"
        :loading="isProcessing"
        :disabled="!selectedApp"
        @click="handleInstall"
      >
        Install App
      </GradientButton>
      
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
import GlassModal from "@/components/ui/GlassModal.vue"
import GlassSelect from "@/components/ui/GlassSelect.vue"
import GradientButton from "@/components/ui/GradientButton.vue"
import ProcessLog from "@/components/ui/ProcessLog.vue"
import StatusIndicator from "@/components/ui/StatusIndicator.vue"
import { benches, sites, tasks } from "@/services/htbencherApi"
import { useSocket } from "@/socket"
import { onMounted, onUnmounted, ref, watch } from "vue"

const props = defineProps({
  modelValue: Boolean,
  benchName: String,
  siteName: String
})

const emit = defineEmits(["update:modelValue", "installed"])

const loadingApps = ref(false)
const appOptions = ref([])
const selectedApp = ref("")

const isProcessing = ref(false)
const isComplete = ref(false)
const hasError = ref(false)
const progress = ref(0)
const statusMessage = ref("Initializing...")
const logs = ref([])
const taskId = ref(null)
const isPolling = ref(false)

const socket = useSocket()

watch(() => props.modelValue, (newVal) => {
    if (newVal) {
        selectedApp.value = ""
        fetchApps()
    }
})

async function fetchApps() {
    if (!props.benchName) return
    loadingApps.value = true
    try {
        const res = await benches.getInstalledApps(props.benchName)
        appOptions.value = (res.message || res || []).map(app => ({ label: app, value: app }))
    } catch (e) {
        console.error("Failed to fetch bench apps", e)
        appOptions.value = []
    } finally {
        loadingApps.value = false
    }
}

async function handleInstall() {
    if (!selectedApp.value) return

    isProcessing.value = true
    isComplete.value = false
    hasError.value = false
    logs.value = []
    progress.value = 0
    statusMessage.value = "Starting installation..."

    try {
        const res = await sites.installApp(props.siteName, selectedApp.value)
        if (res.task_id) {
            taskId.value = res.task_id
            statusMessage.value = "Installation queued..."
            
            setupSocketListeners(res.task_id)
            startPolling(res.task_id)
        }
    } catch (err) {
        console.error(err)
        hasError.value = true
        isProcessing.value = false
        isComplete.value = true
        statusMessage.value = "Failed to start installation."
    }
}

function startPolling(id) {
    isPolling.value = true
    poll(id)
}

async function poll(id) {
    if (!isPolling.value || !id) return

    try {
        const res = await tasks.getStatus(id)
        if (res && res.logs) {
            const newLogs = res.logs.filter(l => 
                !logs.value.some(existing => existing.message === l.log && existing.time.includes(new Date(l.timestamp).toLocaleTimeString().split(' ')[0]))
            )
            
            if (newLogs.length > 0) {
                newLogs.forEach(l => {
                    logs.value.push({ time: new Date(l.timestamp).toLocaleTimeString(), message: l.log, error: l.error })
                })
            }
        }

        if (res && (res.status === 'success' || res.status === 'failed')) {
            isComplete.value = true
            isProcessing.value = false
            hasError.value = res.status === 'failed'
            statusMessage.value = res.status === 'success' ? 'Completed' : 'Failed'
            if (res.status === 'success') progress.value = 100
            isPolling.value = false
            return
        }
    } catch (e) {}

    if (isPolling.value) {
        setTimeout(() => poll(id), 2000)
    }
}

function setupSocketListeners(id) {
    if (!socket || !socket.connected) return

    socket.on('htbench_task_progress', (data) => {
        if (data.task_id === id) {
            progress.value = data.percentage
            statusMessage.value = data.status
        }
    })

    socket.on('htbench_task_log', (data) => {
        if (data.task_id === id) {
             if (!logs.value.some(l => l.message === data.log)) {
                 logs.value.push({ time: new Date().toLocaleTimeString(), message: data.log, error: data.error })
             }
        }
    })

    socket.on('htbench_task_complete', (data) => {
        if (data.task_id === id) {
            isComplete.value = true
            isProcessing.value = false
            hasError.value = data.status !== 'success'
            statusMessage.value = data.status === 'success' ? 'Completed' : 'Failed'
            if (data.status === 'success') progress.value = 100
            isPolling.value = false
        }
    })
}

function reset() {
    selectedApp.value = ""
    taskId.value = null
    isProcessing.value = false
    isComplete.value = false
    logs.value = []
    
    if (socket) {
        socket.off('htbench_task_progress')
        socket.off('htbench_task_log')
        socket.off('htbench_task_complete')
    }
}

function handleClose() {
    if (isProcessing.value) {
        if(!confirm("Installation is running. Are you sure you want to close?")) return
    }
    emit("update:modelValue", false)
    reset()
}

function finish() {
    emit("installed")
    emit("update:modelValue", false)
    reset()
}

onUnmounted(() => {
    if (socket) {
        socket.off('htbench_task_progress')
        socket.off('htbench_task_log')
        socket.off('htbench_task_complete')
    }
})
</script>
