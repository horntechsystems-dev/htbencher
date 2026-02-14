<template>
  <div
    class="flex h-full flex-col border-r bg-surface-gray-1 transition-all duration-300"
    :class="[isCollapsed ? 'w-16' : 'w-64']"
  >
    <div class="flex h-16 items-center px-4 border-b">
      <div class="flex items-center gap-2 overflow-hidden">
        <div class="h-8 w-8 flex-shrink-0 rounded bg-ink-gray-9 flex items-center justify-center text-surface-white font-bold">
          HT
        </div>
        <span v-if="!isCollapsed" class="text-xl font-bold tracking-tight text-ink-gray-9 truncate">
          HTBencher
        </span>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto px-3 py-4 space-y-1">
      <router-link
        v-for="item in menuItems"
        :key="item.name"
        :to="item.to"
        class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors"
        :class="[
          router.currentRoute.value.name === item.name
            ? 'bg-surface-white text-ink-gray-9 shadow-sm ring-1 ring-outline-gray-2'
            : 'text-ink-gray-5 hover:bg-surface-gray-2 hover:text-ink-gray-9'
        ]"
      >
        <component :is="item.icon" class="h-5 w-5 flex-shrink-0" />
        <span v-if="!isCollapsed" class="truncate">{{ item.label }}</span>
      </router-link>
    </div>

    <div class="border-t p-3">
      <button
        @click="isCollapsed = !isCollapsed"
        class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-ink-gray-5 hover:bg-surface-gray-2 hover:text-ink-gray-9 transition-colors"
      >
        <component :is="isCollapsed ? 'Maximize' : 'Minimize'" class="h-5 w-5 flex-shrink-0" />
        <span v-if="!isCollapsed">Collapse</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import {
	Package as Apps,
	Terminal as Benches,
	BarChart3 as Dashboard,
	Activity as Jobs,
	ChevronRight as Maximize,
	ChevronLeft as Minimize,
	Globe as Sites,
} from "lucide-vue-next"
import { ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const isCollapsed = ref(false)

const menuItems = [
	{ name: "Dashboard", label: "Dashboard", to: "/dashboard", icon: Dashboard },
	{ name: "Benches", label: "Benches", to: "/benches", icon: Benches },
	{ name: "Apps", label: "Apps", to: "/apps", icon: Apps },
	{ name: "Sites", label: "Sites", to: "/sites", icon: Sites },
	{ name: "Jobs", label: "Jobs", to: "/jobs", icon: Jobs },
]
</script>
