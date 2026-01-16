<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">{{ $t('report.title') }}</h1>
    </div>

    <div class="card-container">
      <div class="empty-state">
        <el-empty :description="$t('report.inDevelopment')" />
      </div>
    </div>
  </div>
</template>

<script setup>
// Test report list component
</script>