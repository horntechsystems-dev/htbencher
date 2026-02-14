<template>
  <div class="space-y-2">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Select Branch</label>
    <div v-if="loading" class="flex justify-center py-4">
      <LoadingIndicator />
    </div>
    <GlassSelect
      v-else
      :model-value="modelValue"
      :options="branchOptions"
      placeholder="Select branch..."
      @update:model-value="$emit('update:modelValue', $event)"
    />
  </div>
</template>

<script setup>
import { computed } from "vue"
import GlassSelect from "@/components/ui/GlassSelect.vue"

const props = defineProps({
  modelValue: String,
  branches: {
    type: Array,
    default: () => []
  },
  loading: Boolean
})

defineEmits(['update:modelValue'])

const branchOptions = computed(() => 
    props.branches?.map(b => ({ label: b, value: b })) || []
)
</script>
