<template>
  <GlassModal
    :model-value="modelValue"
    title="Create New Site"
    @update:model-value="handleClose"
  >
    <!-- Step 1: Input Form -->
    <div v-if="!isProcessing && !isComplete">
        <form @submit.prevent="handleCreate">
        <div class="space-y-4">
            <GlassSelect
              v-model="form.bench_name"
              label="Select Bench"
              :options="benchOptions"
              placeholder="Select a bench..."
              required
              hint="The bench where this site will be installed."
            />
            
            <GlassInput
              v-model="form.site_name"
              label="Site Name"
              placeholder="e.g. mysite.localhost"
              required
              hint="A unique name for your site (usually the domain)."
            />
            
            <GlassInput
              v-model="form.admin_password"
              label="Admin Password"
              type="password"
              required
              hint="The Administrator password for the new site."
            />
            
            <GlassInput
              v-model="form.db_password"
              label="Database Password"
              type="password"
              required
              hint="The MariaDB root password for creating the database."
            />
            
            <GlassInput
              v-model="form.root_domain"
              label="Root Domain (Optional)"
              placeholder="e.g. example.com"
            />
        </div>
        </form>
    </div>

    <!-- Step 2: Processing / Terminal -->
    <div v-else class="space-y-4">
        <div class="flex items-center justify-between">
            <h4 class="text-sm font-semibold text-gray-900 dark:text-white">
                {{ isComplete ? (hasError ? 'Task Failed' : 'Task Completed') : 'Creating Site...' }}
            </h4>
            <StatusIndicator :status="isComplete ? (hasError ? 'Failed' : 'Active') : 'Active'" />
        </div>
        
        <ProcessLog 
            :logs="logs" 
            :progress="progress" 
            :status="statusMessage"
        />
        
        <div v-if="isComplete" class="rounded-lg bg-green-50 p-4 text-sm text-green-700 dark:bg-green-900/30 dark:text-green-400" :class="{'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400': hasError}">
            {{ hasError ? 'Site creation failed. Please check the logs above.' : 'Site created successfully! You can now access it from the dashboard.' }}
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
import { sites } from "@/services/htbencherApi"
import { useSocket } from "@/socket"
import { createResource } from "frappe-ui"
import { computed, onUnmounted, reactive, ref } from "vue"

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
    site_name: "",
    admin_password: "",
    db_password: "",
    root_domain: ""
})

// Resources
const benchesResource = createResource({
    url: 'frappe.client.get_list',
    params: { doctype: "HT Bench", fields: ["name"] },
    auto: true
})

// Computeds
const benchOptions = computed(() => 
    benchesResource.data?.map(b => ({ label: b.name, value: b.name })) || []
)

// Logic
async function handleCreate() {
    if(!form.bench_name || !form.site_name || !form.admin_password || !form.db_password) return

    loading.value = true
    // Reset state
    logs.value = []
    progress.value = 0
    isProcessing.value = false 
    isComplete.value = false
    hasError.value = false
    statusMessage.value = "Starting..."

    try {
        const payload = {
            bench_name: form.bench_name,
            site_name: form.site_name,
            admin_password: form.admin_password,
            db_password: form.db_password,
            root_domain: form.root_domain || null
        }
        const res = await sites.create(payload)
        if (res.task_id) {
            taskId.value = res.task_id
            isProcessing.value = true
            statusMessage.value = "Task queued..."
            
            // Use Sockets
            setupSocketListeners(res.task_id)
        }
    } catch (e) {
        console.error(e)
        loading.value = false
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
        }
    })
}

function handleClose() {
    if (isProcessing.value) {
        if(!confirm("Task is running. Are you sure you want to close? Logs will be lost.")) return
    }
    emit("update:modelValue", false)
    reset()
}

function finish() {
    emit("created")
    emit("update:modelValue", false)
    reset()
}

function reset() {
    form.site_name = ""
    form.admin_password = ""
    form.db_password = ""
    form.root_domain = ""
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

onUnmounted(() => {
    if (socket) {
        socket.off('htbench_task_progress')
        socket.off('htbench_task_log')
        socket.off('htbench_task_complete')
    }
})
</script>
