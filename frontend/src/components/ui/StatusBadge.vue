<template>
  <Badge
    :variant="badgeVariant"
    v-bind="$attrs"
  >
    {{ label }}
  </Badge>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
	label: String,
	status: {
		type: String,
		default: "neutral",
	},
})

const badgeVariant = computed(() => {
	const map = {
		active: "green",
		running: "blue",
		success: "green",
		failed: "red",
		warning: "orange",
		error: "red",
		neutral: "gray",
		stopped: "gray",
		pending: "orange",
	}
	return map[props.status.toLowerCase()] || "gray"
})
</script>
