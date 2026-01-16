<template>
  <div class="register-container">
    <div class="register-form">
      <div class="form-header">
        <h2>{{ $t('auth.registerTitle') }}</h2>
        <p>{{ $t('auth.registerSubtitle') }}</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        @submit.prevent="handleRegister"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            :placeholder="$t('auth.username')"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            type="email"
            :placeholder="$t('auth.email')"
            size="large"
            :prefix-icon="Message"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item prop="first_name">
              <el-input
                v-model="form.first_name"
                :placeholder="$t('auth.firstName')"
                size="large"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="last_name">
              <el-input
                v-model="form.last_name"
                :placeholder="$t('auth.lastName')"
                size="large"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            :placeholder="$t('auth.password')"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item prop="password_confirm">
          <el-input
            v-model="form.password_confirm"
            type="password"
            :placeholder="$t('auth.confirmPassword')"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item prop="department">
              <el-input
                v-model="form.department"
                :placeholder="$t('auth.department')"
                size="large"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="position">
              <el-input
                v-model="form.position"
                :placeholder="$t('auth.position')"
                size="large"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleRegister"
            style="width: 100%"
          >
            {{ $t('auth.register') }}
          </el-button>
        </el-form-item>

        <div class="form-footer">
          <router-link to="/login">{{ $t('auth.hasAccount') }}</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  password_confirm: '',
  department: '',
  position: ''
})

const rules = {
  username: [
    { required: true, message: computed(() => t('auth.usernameRequired')), trigger: 'blur' },
    { min: 3, max: 20, message: computed(() => t('auth.usernameLength')), trigger: 'blur' }
  ],
  email: [
    { required: true, message: computed(() => t('auth.emailRequired')), trigger: 'blur' },
    { type: 'email', message: computed(() => t('auth.emailFormat')), trigger: 'blur' }
  ],
  password: [
    { required: true, message: computed(() => t('auth.passwordRequired')), trigger: 'blur' },
    { min: 6, message: computed(() => t('auth.passwordLength')), trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: computed(() => t('auth.confirmPasswordRequired')), trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error(t('auth.passwordMismatch')))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const handleRegister = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.register(form)
        ElMessage.success(t('auth.registerSuccess'))
        router.push('/login')
      } catch (error) {
        ElMessage.error(error.response?.data?.error || t('auth.registerFailed'))
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.register-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-form {
  width: 500px;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  
  .form-header {
    text-align: center;
    margin-bottom: 30px;
    
    h2 {
      color: #303133;
      font-size: 28px;
      font-weight: 600;
      margin: 0 0 10px 0;
    }
    
    p {
      color: #909399;
      margin: 0;
    }
  }
  
  .form-footer {
    text-align: center;
    margin-top: 20px;
    
    a {
      color: #409eff;
      text-decoration: none;
      
      &:hover {
        text-decoration: underline;
      }
    }
  }
}
</style>