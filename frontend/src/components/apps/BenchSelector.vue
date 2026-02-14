<template>
  <div class="space-y-2">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Target Bench</label>
    <GlassSelect
      :model-value="modelValue"
      :options="benchOptions"
      placeholder="Select a bench..."
      hint="The bench where the app will be installed."
      @update:model-value="$emit('update:modelValue', $event)"
    />
  </div>
</template>

<script setup>
import { computed, onMounted } from "vue"
import GlassSelect from "@/components/ui/GlassSelect.vue"
import { useBench } from "@/composables/useBench"

const props = defineProps({
  modelValue: String
})

defineEmits(['update:modelValue'])

const { benchList } = useBench()

onMounted(() => {
    if (!benchList.data?.length) {
        benchList.reload()
    }
})

const benchOptions = computed(() => 
    benchList.data?.map(b => ({ label: b.name, value: b.name })) || []
)
</script>
