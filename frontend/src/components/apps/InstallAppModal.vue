<template>
  <GlassModal
    :model-value="modelValue"
    title="Install App"
    @update:model-value="handleClose"
  >
    <div v-if="!isProcessing && !isComplete">
      <form id="install-app-form" @submit.prevent="handleInstall">
        <div class="space-y-4">
          <GlassSelect
            v-model="form.app_doc_name"
            label="Select App"
            :options="appOptions"
            placeholder="Select an app to install..."
            required
            hint="Choose an app from your HT App definitions."
          />
          
          <GlassSelect
            v-model="form.bench_name"
            label="Target Bench"
            :options="benchOptions"
            placeholder="Select a bench..."
            required
            hint="The bench where this app will be installed."
          />
        </div>
      </form>
    </div>

    <!-- Process Logs -->
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
        type="submit"
        form="install-app-form"
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
import GlassInput from "@/components/ui/GlassInput.vue"
import GlassModal from "@/components/ui/GlassModal.vue"
import GlassSelect from "@/components/ui/GlassSelect.vue"
import GradientButton from "@/components/ui/GradientButton.vue"
import ProcessLog from "@/components/ui/ProcessLog.vue"
import StatusIndicator from "@/components/ui/StatusIndicator.vue"
import { useBench } from "@/composables/useBench"
import { benches } from "@/services/htbencherApi"
import { useSocket } from "@/socket"
import { createResource } from "frappe-ui"
import { computed, reactive, ref, onBeforeUnmount } from "vue"

const props = defineProps({
  modelValue: Boolean,
})

const emit = defineEmits(["update:modelValue", "installed"])

const { benchList } = useBench()
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
	app_doc_name: "",
	bench_name: "",
})

// HT Apps Resource
const appsResource = createResource({
    url: 'frappe.client.get_list',
    params: { doctype: "HT App", fields: ["name", "app_name"] },
    auto: true
})

const appOptions = computed(() => 
    appsResource.data?.map(a => ({ label: a.app_name || a.name, value: a.name })) || []
)

const benchOptions = computed(() => 
    benchList.data?.map(b => ({ label: b.name, value: b.name })) || []
)

async function handleInstall() {
    if(!form.app_doc_name || !form.bench_name) return

	loading.value = true
    logs.value = []
    progress.value = 0
    isComplete.value = false
    hasError.value = false
    statusMessage.value = "Starting..."

	try {
        const res = await benches.installApp(form.bench_name, form.app_doc_name)
        if (res.task_id) {
            taskId.value = res.task_id
            isProcessing.value = true
            statusMessage.value = "Task queued..."
            
            setupSocketListeners(res.task_id)
        }
	} catch (e) {
        console.error(e)
        loading.value = false
        isProcessing.value = false
        hasError.value = true
        statusMessage.value = "Failed: " + (e.message || "Unknown error")
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
    if (isProcessing.value && !isComplete.value) {
        if(!confirm("Task is running. Are you sure you want to close?")) return
    }
    emit("update:modelValue", false)
    form.app_doc_name = ""
    isProcessing.value = false
}

function finish() {
    emit("installed")
    emit("update:modelValue", false)
}
</script>
