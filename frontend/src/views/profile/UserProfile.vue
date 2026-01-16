<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">{{ $t('profile.title') }}</h1>
    </div>

    <div class="card-container">
      <el-tabs v-model="activeTab">
        <el-tab-pane :label="$t('profile.basicInfo')" name="basic">
          <el-form v-if="userStore.user" :model="userStore.user" label-width="100px">
            <el-form-item :label="$t('profile.username')">
              <el-input v-model="userStore.user.username" disabled />
            </el-form-item>
            <el-form-item :label="$t('profile.email')">
              <el-input v-model="userStore.user.email" />
            </el-form-item>
            <el-form-item :label="$t('profile.name')">
              <el-input v-model="userStore.user.first_name" />
            </el-form-item>
            <el-form-item :label="$t('profile.department')">
              <el-input v-model="userStore.user.department" />
            </el-form-item>
            <el-form-item :label="$t('profile.position')">
              <el-input v-model="userStore.user.position" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary">{{ $t('common.save') }}</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane :label="$t('profile.changePassword')" name="password">
          <el-form label-width="120px">
            <el-form-item :label="$t('profile.currentPassword')">
              <el-input type="password" />
            </el-form-item>
            <el-form-item :label="$t('profile.newPassword')">
              <el-input type="password" />
            </el-form-item>
            <el-form-item :label="$t('profile.confirmPassword')">
              <el-input type="password" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary">{{ $t('profile.changePasswordButton') }}</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const activeTab = ref('basic')
</script>