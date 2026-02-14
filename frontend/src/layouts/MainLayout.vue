<template>
  <div class="min-h-screen bg-gray-50 font-sans text-gray-900 transition-colors duration-300 dark:bg-gray-900 dark:text-gray-100">
    <SidebarPremium
      :collapsed="sidebarCollapsed"
    />
    
    <div
      class="flex min-h-screen flex-col transition-all duration-300"
      :class="[sidebarCollapsed ? 'pl-20' : 'pl-64']"
    >
      <NavbarPremium
        :collapsed="sidebarCollapsed"
        @toggle-sidebar="toggleSidebar"
      />
      
      <main class="flex-1 p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import NavbarPremium from "@/components/layout/NavbarPremium.vue"
import SidebarPremium from "@/components/layout/SidebarPremium.vue"
import { ref } from "vue"

const sidebarCollapsed = ref(false)
function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>
