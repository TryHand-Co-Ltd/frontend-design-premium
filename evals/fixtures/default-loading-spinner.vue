<template>
  <section class="orders-table min-h-80">
    <AppSpinner v-if="loading" aria-label="読み込み中" />
    <OrderTable v-else :rows="rows" />
  </section>
</template>
