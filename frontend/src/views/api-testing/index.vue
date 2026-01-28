<template>
  <div class="api-testing-layout">
    <!-- 顶部导航 -->
    <div class="top-nav">
      <h2>{{ $t('apiTesting.nav.title') }}</h2>
      <el-menu
        :default-active="currentRoute"
        mode="horizontal"
        @select="handleMenuSelect"
        class="nav-menu"
      >
        <el-menu-item index="projects">{{ $t('apiTesting.nav.projects') }}</el-menu-item>
        <el-menu-item index="interfaces">{{ $t('apiTesting.nav.interfaces') }}</el-menu-item>
        <el-menu-item index="automation">{{ $t('apiTesting.nav.automation') }}</el-menu-item>
        <el-menu-item index="history">{{ $t('apiTesting.nav.history') }}</el-menu-item>
        <el-menu-item index="environments">{{ $t('apiTesting.nav.environments') }}</el-menu-item>
        <el-menu-item index="scheduled-tasks">{{ $t('apiTesting.nav.scheduledTasks') }}</el-menu-item>
        <el-menu-item index="reports">{{ $t('apiTesting.nav.reports') }}</el-menu-item>
        <el-menu-item index="notification-logs">{{ $t('apiTesting.nav.notificationLogs') }}</el-menu-item>
        <el-menu-item index="notification-configs">{{ $t('apiTesting.nav.notificationConfigs') }}</el-menu-item>
      </el-menu>
    </div>

    <!-- 内容区域 -->
    <div class="content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const currentRoute = computed(() => {
  const path = route.path
  if (path.includes('/projects')) return 'projects'
  if (path.includes('/interfaces')) return 'interfaces' 
  if (path.includes('/automation')) return 'automation'
  if (path.includes('/history')) return 'history'
  if (path.includes('/environments')) return 'environments'
  if (path.includes('/scheduled-tasks')) return 'scheduled-tasks'
  if (path.includes('/reports')) return 'reports'
  if (path.includes('/notification-logs')) return 'notification-logs'
  if (path.includes('/notification-configs')) return 'notification-configs'
  return 'projects'
})

const handleMenuSelect = (index) => {
  router.push(`/api-testing/${index}`)
}
</script>

<style scoped>
.api-testing-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.top-nav {
  border-bottom: 1px solid #e4e7ed;
  background: white;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 30px;
}

.top-nav h2 {
  margin: 0;
  color: #303133;
  white-space: nowrap;
}

.nav-menu {
  flex: 1;
  border: none;
}

.content {
  flex: 1;
  overflow: hidden;
}
</style>