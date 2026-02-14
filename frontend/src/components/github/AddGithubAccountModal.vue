<template>
  <GlassModal
    :model-value="modelValue"
    title="Add GitHub Account"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Account Name</label>
        <GlassInput
          v-model="form.account_name"
          placeholder="e.g. My GitHub"
          class="mt-1"
        />
      </div>

      <SSHKeyGenerator 
        v-model:privateKey="form.ssh_private_key"
        v-model:publicKey="form.ssh_public_key"
      />

      <div class="rounded-xl bg-blue-50 p-4 dark:bg-blue-900/20">
        <div class="flex gap-3">
          <Info class="h-5 w-5 text-blue-600" />
          <div class="text-xs text-blue-700 dark:text-blue-300">
            <p class="font-semibold">Security Note</p>
            <p class="mt-1">Private keys are encrypted and stored securely on your server. They are only used for SSH-based app installations.</p>
          </div>
        </div>
      </div>
    </div>

    <template #actions>
      <div class="flex justify-end gap-2 px-2">
        <Button variant="subtle" @click="modelValue = false" :disabled="loading">Cancel</Button>
        <GradientButton @click="onSubmit" :loading="loading" :disabled="!form.account_name || !form.ssh_private_key">
          Add Account
        </GradientButton>
      </div>
    </template>
  </GlassModal>
</template>

<script setup>
import { reactive, watch } from "vue"
import { Info } from "lucide-vue-next"
import GlassModal from "@/components/ui/GlassModal.vue"
import GlassInput from "@/components/ui/GlassInput.vue"
import GradientButton from "@/components/ui/GradientButton.vue"
import SSHKeyGenerator from "./SSHKeyGenerator.vue"

const props = defineProps({
  modelValue: Boolean,
  loading: Boolean
})

const emit = defineEmits(["update:modelValue", "submit"])

const form = reactive({
  account_name: "",
  ssh_private_key: "",
  ssh_public_key: ""
})

watch(() => props.modelValue, (val) => {
  if (val) {
    form.account_name = ""
    form.ssh_private_key = ""
    form.ssh_public_key = ""
  }
})

function onSubmit() {
  emit("submit", { ...form })
}
</script>
