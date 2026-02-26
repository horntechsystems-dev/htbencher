<template>
  <div class="min-h-screen bg-gray-50 font-sans text-gray-900 transition-colors duration-300 dark:bg-gray-900 dark:text-gray-100">
    <!-- Mobile Sidebar Overlay -->
    <div 
      v-if="!sidebarCollapsed" 
      class="fixed inset-0 z-40 bg-gray-900/50 backdrop-blur-sm lg:hidden transition-opacity" 
      @click="sidebarCollapsed = true"
    ></div>

    <SidebarPremium
      :collapsed="sidebarCollapsed"
    />
    
    <div
      class="flex min-h-screen flex-col transition-all duration-300"
      :class="[sidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64']"
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
import { ref, onMounted, onUnmounted } from "vue"

const sidebarCollapsed = ref(true)

function handleResize() {
  sidebarCollapsed.value = window.innerWidth < 1024
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>
