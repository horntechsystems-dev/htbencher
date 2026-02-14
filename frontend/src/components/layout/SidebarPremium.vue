<template>
  <aside
    class="fixed inset-y-0 left-0 z-50 flex flex-col border-r border-gray-200 bg-white/80 backdrop-blur-xl transition-all duration-300 dark:border-gray-800 dark:bg-gray-900/80"
    :class="[collapsed ? 'w-20' : 'w-64']"
  >
    <div class="flex h-16 items-center justify-center border-b border-gray-100 dark:border-gray-800">
      <div class="flex items-center gap-3 overflow-hidden px-4">
        <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gray-900 text-white dark:bg-white dark:text-gray-900">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <span
          class="font-bold text-gray-900 transition-opacity dark:text-white"
          :class="[collapsed ? 'opacity-0 w-0' : 'opacity-100']"
        >
          HTBencher
        </span>
      </div>
    </div>

    <nav class="flex-1 space-y-1 px-3 py-4">
      <router-link
        v-for="item in navigation"
        :key="item.name"
        :to="item.to"
        class="group flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition-colors"
        :class="[
          isActive(item.to)
            ? 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-white'
            : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800/50 dark:hover:text-white'
        ]"
      >
        <component
          :is="item.icon"
          class="h-5 w-5 shrink-0 transition-colors"
          :class="[
            isActive(item.to)
              ? 'text-gray-900 dark:text-white'
              : 'text-gray-400 group-hover:text-gray-500 dark:text-gray-500 dark:group-hover:text-gray-300'
          ]"
        />
        <span
          class="ml-3 overflow-hidden text-nowrap transition-all duration-300"
          :class="[collapsed ? 'w-0 opacity-0' : 'w-auto opacity-100']"
        >
          {{ item.name }}
        </span>
      </router-link>
    </nav>

    <div class="border-t border-gray-100 p-4 dark:border-gray-800">
      <button
        @click="logout"
        class="group flex w-full items-center rounded-lg px-3 py-2.5 text-sm font-medium text-red-600 transition-colors hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
      >
        <LogOut class="h-5 w-5 shrink-0" />
        <span
          class="ml-3 overflow-hidden text-nowrap transition-all duration-300"
          :class="[collapsed ? 'w-0 opacity-0' : 'w-auto opacity-100']"
        >
          Sign out
        </span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { useAuth } from "@/composables/useAuth"
import {
  LayoutDashboard,
  Terminal,
  Globe,
  Package,
  Layers,
  LogOut,
  Settings,
  Github
} from "lucide-vue-next"
import { useRoute } from "vue-router"

defineProps({
  collapsed: Boolean,
})

const route = useRoute()
const { logout } = useAuth()

const navigation = [
  { name: "Dashboard", to: { name: "Dashboard" }, icon: LayoutDashboard },
  { name: "Benches", to: { name: "Benches" }, icon: Terminal },
  { name: "Sites", to: { name: "Sites" }, icon: Globe },
  { name: "Apps", to: { name: "Apps" }, icon: Package },
  { name: "Jobs", to: { name: "Jobs" }, icon: Layers },
  { name: "GitHub Accounts", to: { name: "GithubAccounts" }, icon: Github },
]

function isActive(to) {
  return route.name === to.name
}
</script>
