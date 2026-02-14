<template>
  <div class="space-y-2">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">GitHub Account</label>
    <GlassSelect
      :model-value="modelValue"
      :options="accountOptions"
      placeholder="Select GitHub account..."
      hint="Used for authentication during repo listing and installation."
      @update:model-value="$emit('update:modelValue', $event)"
    />
  </div>
</template>

<script setup>
import { computed, onMounted } from "vue"
import GlassSelect from "@/components/ui/GlassSelect.vue"
import { useGithub } from "@/composables/useGithub"

const props = defineProps({
  modelValue: String
})

defineEmits(['update:modelValue'])

const { accounts, fetchAccounts } = useGithub()

onMounted(() => {
  fetchAccounts()
})

const accountOptions = computed(() => 
    accounts.value?.map(a => ({ label: a.account_name, value: a.name })) || []
)
</script>
