<template>
  <GlassModal
    :model-value="modelValue"
    title="Create New Bench"
    @update:model-value="handleClose"
  >
    <!-- Step 1: Input Form -->
    <div v-if="!isProcessing && !isComplete">
        <form @submit.prevent="handleCreate">
        <div class="space-y-4">
            <GlassInput
            v-model="form.bench_name"
            label="Bench Name"
            placeholder="e.g. production-bench"
            required
            hint="A unique name for your bench environment."
            />
            
            <GlassSelect
            v-model="form.server"
            label="Target Server"
            :options="serverOptions"
            placeholder="Select a server..."
            required
            hint="The server where this bench will be deployed."
            />
            
            <GlassSelect
            v-if="form.server && pythonOptions.length"
            v-model="form.python_version"
            label="Python Version"
            :options="pythonOptions"
            required
            />
            
            <GlassInput
            v-if="form.server"
            v-model="form.frappe_branch"
            label="Frappe Branch"
            placeholder="version-15"
            hint="Branch or tag to install (e.g. version-14, develop)"
            />
        </div>
        </form>
    </div>

    <!-- Step 2: Processing / Terminal -->
    <div v-else class="space-y-4">
        <div class="flex items-center justify-between">
            <h4 class="text-sm font-semibold text-gray-900 dark:text-white">
                {{ isComplete ? (hasError ? 'Task Failed' : 'Task Completed') : 'Creating Bench...' }}
            </h4>
            <StatusIndicator :status="isComplete ? (hasError ? 'Failed' : 'Active') : 'Active'" />
        </div>
        
        <ProcessLog 
            :logs="logs" 
            :progress="progress" 
            :status="statusMessage"
        />
        
        <div v-if="isComplete" class="rounded-lg bg-green-50 p-4 text-sm text-green-700 dark:bg-green-900/30 dark:text-green-400" :class="{'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400': hasError}">
            {{ hasError ? 'Bench creation failed. Please check the logs above.' : 'Bench created successfully! You can now access it from the dashboard.' }}
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
        :loading="loading"
        @click="handleCreate"
      >
        Start Creation
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
import GlassInput from "@/components/ui/GlassInput.vue"
import GlassModal from "@/components/ui/GlassModal.vue"
import GlassSelect from "@/components/ui/GlassSelect.vue"
import GradientButton from "@/components/ui/GradientButton.vue"
import ProcessLog from "@/components/ui/ProcessLog.vue"
import StatusIndicator from "@/components/ui/StatusIndicator.vue"
import { useBench } from "@/composables/useBench"
import { benches, tasks } from "@/services/htbencherApi"
import { useSocket } from "@/socket" // Import from your socket file
import { createResource } from "frappe-ui"
import { computed, onMounted, onUnmounted, reactive, ref, watch } from "vue"

const props = defineProps({
  modelValue: Boolean,
})

const emit = defineEmits(["update:modelValue", "created"])

// State
const loading = ref(false)
const isProcessing = ref(false)
const isComplete = ref(false)
const hasError = ref(false)
const progress = ref(0)
const statusMessage = ref("Initializing...")
const logs = ref([])
const taskId = ref(null)
const socket = useSocket()

const form = reactive({
	bench_name: "",
	server: "",
    python_version: "",
    frappe_branch: "version-15"
})

// Resources
const serversResource = createResource({
    url: 'frappe.client.get_list',
    params: { doctype: "HT Server", fields: ["name"] },
    auto: true
})

const pythonsResource = createResource({
    url: 'htbencher.api.v1.bench.get_available_pythons',
    params: {},
    auto: false
})

// Computeds
const serverOptions = computed(() => 
    serversResource.data?.map(s => ({ label: s.name, value: s.name })) || []
)

const pythonOptions = computed(() =>
    pythonsResource.data?.map(v => ({ label: v, value: v })) || []
)

// Watchers
watch(() => form.server, (newVal) => {
    if (newVal) {
        pythonsResource.params = { server: newVal }
        pythonsResource.reload().then(() => {
             const data = pythonsResource.data
             // select first available if python3.11 not there
             if (data && data.includes('python3.11')) {
                 form.python_version = 'python3.11'
             } else if (data && data.length > 0) {
                 form.python_version = data[0]
             }
        })
    } else {
        pythonsResource.data = []
        form.python_version = ""
    }
})

const isPolling = ref(false)

// Logic
async function handleCreate() {
    if(!form.bench_name || !form.server || !form.python_version) return

	loading.value = true
    // Reset state
    logs.value = []
    progress.value = 0
    isProcessing.value = false // This will be set to true in the next step
    isComplete.value = false
    hasError.value = false
    statusMessage.value = "Starting..."

	try {
        const res = await benches.create(form)
        if (res.task_id) {
            taskId.value = res.task_id
            isProcessing.value = true
            statusMessage.value = "Task queued..."
            
            // Try Sockets (Secondary)
            setupSocketListeners(res.task_id)
            
            // Start Polling (Primary Fallback)
            startPolling(res.task_id)
        }
	} catch (e) {
        console.error(e)
        loading.value = false
    }
}

async function startPolling(id) {
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
                    logs.value.push({
                        time: new Date(l.timestamp).toLocaleTimeString(),
                        message: l.log,
                        error: l.error
                    })
                })
            }
        }

        if (res && (res.status === 'success' || res.status === 'failed')) {
            isComplete.value = true
            isProcessing.value = false
            loading.value = false
            hasError.value = res.status === 'failed'
            statusMessage.value = res.status === 'success' ? 'Completed' : 'Failed'
            if (res.status === 'success') progress.value = 100
            isPolling.value = false
            return
        }
    } catch (e) {
        // Silent fail or minimal log
    }

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
                 logs.value.push({
                     time: new Date().toLocaleTimeString(),
                     message: data.log,
                     error: data.error
                 })
             }
        }
    })

    socket.on('htbench_task_complete', (data) => {
        if (data.task_id === id) {
            isComplete.value = true
            isProcessing.value = false
            loading.value = false
            hasError.value = data.status !== 'success'
            statusMessage.value = data.status === 'success' ? 'Completed' : 'Failed'
            if (data.status === 'success') progress.value = 100
            isPolling.value = false
        }
    })
}

function handleClose() {
    if (isProcessing.value) {
        // Warn user?
        if(!confirm("Task is running. Are you sure you want to close? Logs will be lost.")) return
    }
    emit("update:modelValue", false)
    // Clean up
    reset()
}

function finish() {
    emit("created")
    emit("update:modelValue", false)
    reset()
}

function reset() {
    // Reset form and state
    form.bench_name = ""
    // keep server/python maybe? easier for user
    taskId.value = null
    isProcessing.value = false
    isComplete.value = false
    logs.value = []
    
    // Remove listeners
    if (socket) {
        socket.off('htbench_task_progress')
        socket.off('htbench_task_log')
        socket.off('htbench_task_complete')
    }
}

onUnmounted(() => {
    if (socket) {
        socket.off('htbench_task_progress')
        socket.off('htbench_task_log')
        socket.off('htbench_task_complete')
    }
})
</script>
