<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref<'table' | 'form'>('table')
</script>

<template>
  <!-- Negative fixture: table sizing leaked into the shared shell. -->
  <main class="flex h-dvh flex-col overflow-hidden">
    <nav aria-label="Order views">
      <button type="button" @click="activeTab = 'table'">Orders</button>
      <button type="button" @click="activeTab = 'form'">Order details</button>
    </nav>

    <section class="min-h-0 flex-1 overflow-hidden">
      <div v-if="activeTab === 'table'" class="flex h-full min-h-0 flex-col">
        <div class="min-h-0 flex-1 overflow-auto">
          <table><tbody><tr><td>Large table</td></tr></tbody></table>
        </div>
      </div>

      <!-- The 20-field form is now clipped inside the table-owned viewport. -->
      <form v-else class="h-full overflow-hidden">Long order form</form>
    </section>
  </main>
</template>
