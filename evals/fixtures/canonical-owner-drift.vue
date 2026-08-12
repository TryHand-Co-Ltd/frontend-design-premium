<script setup lang="ts">
// UX-CONTRACT.md names AppSelect as the canonical owner, but this screen copied it locally.
const save = () => undefined
</script>

<template>
  <form @submit.prevent="save">
    <select aria-label="注文ステータス">
      <option>未処理</option>
    </select>
    <a href="#">保存</a>
  </form>
</template>
