<template>
  <div class="space-y-4 rounded-xl bg-gray-50 p-4 dark:bg-gray-800/50">
    <div class="flex items-center justify-between">
      <h4 class="text-sm font-semibold text-gray-900 dark:text-white">SSH Key Pair</h4>
      <Button
        variant="subtle"
        size="sm"
        :loading="loading"
        @click="generateKeys"
      >
        <RefreshCw class="mr-2 h-3 w-3" />
        Generate
      </Button>
    </div>
    
    <div class="space-y-3">
      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400">Private Key</label>
        <textarea
          :value="privateKey"
          rows="4"
          readonly
          class="mt-1 block w-full rounded-lg border-gray-200 bg-white p-2 text-xs font-mono dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
          placeholder="Private key will appear here..."
        ></textarea>
      </div>
      <div>
        <div class="flex items-center justify-between">
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400">Public Key</label>
          <button
            v-if="publicKey"
            class="text-xs text-blue-600 hover:underline dark:text-blue-400"
            @click="copyPublic"
          >
            Copy
          </button>
        </div>
        <textarea
          :value="publicKey"
          rows="3"
          readonly
          class="mt-1 block w-full rounded-lg border-gray-200 bg-white p-2 text-xs font-mono dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
          placeholder="Public key will appear here..."
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { RefreshCw } from "lucide-vue-next"

const props = defineProps({
  privateKey: String,
  publicKey: String
})

const emit = defineEmits(['update:privateKey', 'update:publicKey'])

const loading = ref(false)

async function generateKeys() {
  loading.value = true
  try {
    // We'll call a backend endpoint or use a library. 
    // Usually, backend is safer for keygen.
    // Let's assume we have a backend utility for this.
    const response = await fetch('/api/method/htbencher.api.v1.common.generate_ssh_keypair')
    const result = await response.json()
    if (result.message) {
      emit('update:privateKey', result.message.private)
      emit('update:publicKey', result.message.public)
    }
  } catch (err) {
    console.error("Failed to generate keys", err)
  } finally {
    loading.value = false
  }
}

function copyPublic() {
  navigator.clipboard.writeText(props.publicKey)
  // toast notification would be nice here
}
</script>
