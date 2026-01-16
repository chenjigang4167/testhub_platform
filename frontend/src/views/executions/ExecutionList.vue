<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">{{ $t('execution.title') }}</h1>
    </div>

    <div class="card-container">
      <div class="empty-state">
        <el-empty :description="$t('execution.inDevelopment')" />
      </div>
    </div>
  </div>
</template>

<script setup>
// 执行记录列表组件
</script>
