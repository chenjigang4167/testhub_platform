<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">{{ $t('testSuite.title') }}</h1>
      <el-button type="primary">
        <el-icon><Plus /></el-icon>
        {{ $t('testSuite.newSuite') }}
      </el-button>
    </div>

    <div class="card-container">
      <div class="empty-state">
        <el-empty :description="$t('testSuite.inDevelopment')" />
      </div>
    </div>
  </div>
</template>

<script setup>
// 测试套件列表组件
</script>