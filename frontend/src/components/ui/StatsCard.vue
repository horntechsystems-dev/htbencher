<template>
  <div class="rounded-lg border bg-surface-white p-6 shadow-sm ring-1 ring-outline-gray-2">
    <div class="flex items-center justify-between">
      <p class="text-sm font-medium text-ink-gray-5">{{ label }}</p>
      <component :is="icon" v-if="icon" class="h-4 w-4 text-ink-gray-4" />
    </div>
    <div class="mt-2 flex items-baseline gap-2">
      <h3 class="text-2xl font-bold tracking-tight text-ink-gray-9">{{ value }}</h3>
      <span
        v-if="trend !== undefined"
        class="text-xs font-medium"
        :class="[trend >= 0 ? 'text-ink-green-3' : 'text-ink-red-3']"
      >
        {{ trend >= 0 ? '+' : '' }}{{ trend }}%
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps({
	label: String,
	value: [String, Number],
	icon: Object,
	trend: Number,
})
</script>
