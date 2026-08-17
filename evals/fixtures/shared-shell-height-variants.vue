<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref<'table' | 'form'>('table')
</script>

<template>
  <!-- Negative fixture: equivalent height utilities leak table sizing into the shared shell. -->
  <main class="flex min-h-screen flex-col" style="height: 100%">
    <button type="button" @click="activeTab = 'table'">一覧</button>
    <button type="button" @click="activeTab = 'form'">詳細</button>

    <section class="h-full overflow-hidden">
      <div v-if="activeTab === 'table'" class="min-h-0 overflow-auto">
        <table><tbody><tr><td>大量データ</td></tr></tbody></table>
      </div>
      <form v-else class="h-full overflow-hidden">20項目の注文フォーム</form>
    </section>
  </main>
</template>
