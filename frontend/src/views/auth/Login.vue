<template>
  <div class="login-container">
    <!-- 左侧展示区域 -->
    <div class="showcase-section">
      <div class="showcase-content">
        <!-- Logo和标题 -->
        <div class="brand-header">
          <div class="logo-wrapper">
            <div class="logo-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h1 class="brand-title">TestHub</h1>
          </div>
          <p class="brand-subtitle">AI-Powered Testing Platform</p>
        </div>

        <!-- 特性展示 -->
        <div class="features-grid">
          <div class="feature-card" v-for="(feature, index) in features" :key="index">
            <div class="feature-icon" :style="{ backgroundColor: feature.color }">
              <component :is="feature.icon" />
            </div>
            <div class="feature-content">
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.description }}</p>
            </div>
          </div>
        </div>

        <!-- AI能力展示 -->
        <div class="ai-capabilities">
          <div class="capability-badge">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>{{ $t('auth.aiCaseGeneration') }}</span>
          </div>
          <div class="capability-badge">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span>{{ $t('auth.aiIntelligentTesting') }}</span>
          </div>
          <div class="capability-badge">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
              <path d="M3 9H21" stroke="currentColor" stroke-width="2"/>
              <path d="M9 21V9" stroke="currentColor" stroke-width="2"/>
            </svg>
            <span>{{ $t('auth.automatedExecution') }}</span>
          </div>
          <div class="capability-badge">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path d="M12 6V12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M12 12L16 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M12 12L8 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M12 12L16 16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M12 12L8 16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span>{{ $t('auth.scheduledTasks') }}</span>
          </div>
        </div>
      </div>

      <!-- 装饰元素 -->
      <div class="floating-shapes">
        <!-- 语言切换 -->
        <div class="language-switcher">
          <el-dropdown @command="handleLanguageChange" class="language-dropdown">
            <span class="el-dropdown-link">
              <span class="language-icon">{{ currentLanguage === 'zh-cn' ? '🇨🇳' : '🇺🇸' }}</span>
              <span class="language-text">{{ currentLanguage === 'zh-cn' ? '中文' : 'English' }}</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="zh-cn" :disabled="currentLanguage === 'zh-cn'">
                  <span class="dropdown-flag">🇨🇳</span> 简体中文
                </el-dropdown-item>
                <el-dropdown-item command="en" :disabled="currentLanguage === 'en'">
                  <span class="dropdown-flag">🇺🇸</span> English
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="login-section">
      <div class="login-form-wrapper">
        <div class="form-header">
          <h2>{{ $t('auth.welcomeBack') }}</h2>
          <p>{{ $t('auth.loginSubtitle') }}</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          @submit.prevent="handleLogin"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              :placeholder="$t('auth.usernamePlaceholder')"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              :placeholder="$t('auth.passwordPlaceholder')"
              size="large"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="handleLogin"
              class="login-button"
            >
              <span v-if="!loading">{{ $t('auth.login') }}</span>
              <span v-else>{{ $t('auth.loggingIn') }}</span>
            </el-button>
          </el-form-item>

          <div class="form-footer">
            <router-link to="/register" class="register-link">
              {{ $t('auth.noAccount') }}<span>{{ $t('auth.signUpNow') }}</span>
            </router-link>
          </div>
        </el-form>

        <!-- 底部信息 -->
        <div class="bottom-info">
          <p>{{ $t('auth.copyright') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { User, Lock, Document, MagicStick, Connection, TrendCharts, ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()
const { t } = useI18n()

// 当前语言
const currentLanguage = computed(() => appStore.language)

// 语言切换（无刷新）
const handleLanguageChange = (lang) => {
  appStore.setLanguage(lang)
}
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: computed(() => t('auth.usernameRequired')), trigger: 'blur' }
  ],
  password: [
    { required: true, message: computed(() => t('auth.passwordRequired')), trigger: 'blur' },
    { min: 6, message: computed(() => t('auth.passwordLength')), trigger: 'blur' }
  ]
}

// 特性数据
const features = computed(() => [
  {
    icon: Document,
    title: t('auth.aiCaseGeneration'),
    description: t('auth.aiCaseGenerationDesc'),
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    icon: MagicStick,
    title: t('auth.aiIntelligentTesting'),
    description: t('auth.aiIntelligentTestingDesc'),
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    icon: Connection,
    title: t('auth.multiTypeTesting'),
    description: t('auth.multiTypeTestingDesc'),
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  },
  {
    icon: TrendCharts,
    title: t('auth.dataAnalysis'),
    description: t('auth.dataAnalysisDesc'),
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
  }
])

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        console.log('开始登录...')
        const result = await userStore.login(form)
        console.log('登录结果:', result)
        console.log('用户store状态:', {
          token: userStore.token,
          user: userStore.user,
          isAuthenticated: userStore.isAuthenticated
        })

        ElMessage.success(t('auth.loginSuccess'))
        console.log('准备跳转到 /home')

        // 使用replace而不是push，避免返回登录页
        await router.replace('/home')
        console.log('跳转完成')

      } catch (error) {
        console.error('登录失败:', error)
        ElMessage.error(error.response?.data?.error || t('auth.loginFailed'))
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.login-container {
  height: 100vh;
  display: flex;
  background: #f5f7fa;
  overflow: hidden;
}

.dropdown-flag {
  font-size: 16px;
  margin-right: 6px;
}

/* 左侧展示区域 */
.showcase-section {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 60px;

  .showcase-content {
    position: relative;
    z-index: 2;
    width: 100%;
    max-width: 600px;
    color: white;
  }

  .brand-header {
    margin-bottom: 60px;
    animation: fadeInDown 0.8s ease-out;

    .logo-wrapper {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 16px;

      .logo-icon {
        width: 60px;
        height: 60px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(10px);

        svg {
          width: 32px;
          height: 32px;
          color: white;
        }
      }

      .brand-title {
        font-size: 42px;
        font-weight: 700;
        margin: 0;
        color: white;
        letter-spacing: -1px;
      }
    }

    .brand-subtitle {
      font-size: 18px;
      opacity: 0.9;
      margin: 0;
      font-weight: 300;
      letter-spacing: 1px;
    }
  }

  .features-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-bottom: 60px;

    .feature-card {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      border-radius: 16px;
      padding: 24px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      transition: all 0.3s ease;
      animation: fadeInUp 0.8s ease-out;
      animation-delay: calc(var(--index) * 0.1s);

      &:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.15);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
      }

      .feature-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 16px;

        :deep(svg) {
          width: 24px;
          height: 24px;
          color: white;
        }
      }

      .feature-content {
        h3 {
          font-size: 16px;
          font-weight: 600;
          margin: 0 0 8px 0;
          color: white;
        }

        p {
          font-size: 13px;
          margin: 0;
          opacity: 0.8;
          line-height: 1.5;
        }
      }
    }
  }

  .ai-capabilities {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    animation: fadeInUp 1s ease-out;

    .capability-badge {
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(255, 255, 255, 0.15);
      backdrop-filter: blur(10px);
      padding: 10px 20px;
      border-radius: 50px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      font-size: 14px;
      font-weight: 500;

      svg {
        width: 18px;
        height: 18px;
      }
    }
  }

  .floating-shapes {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: 1;

    .language-switcher {
      position: absolute;
      top: 20px;
      right: 20px;
      z-index: 10;

      .language-dropdown {
        .el-dropdown-link {
          display: flex;
          align-items: center;
          cursor: pointer;
          color: white;
          background: rgba(255, 255, 255, 0.15);
          backdrop-filter: blur(10px);
          padding: 8px 16px;
          border-radius: 20px;
          border: 1px solid rgba(255, 255, 255, 0.2);
          transition: all 0.3s ease;
          outline: none;

          &:focus {
            outline: none;
          }

          .language-icon {
            font-size: 16px;
            margin-right: 6px;
            line-height: 1;
          }

          .language-text {
            font-size: 14px;
            margin-right: 4px;
          }

          &:hover {
            background: rgba(255, 255, 255, 0.25);
          }
        }
      }
    }

    .shape {
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.1);
      animation: float 20s infinite;

      &.shape-1 {
        width: 300px;
        height: 300px;
        top: -100px;
        left: -100px;
        animation-delay: 0s;
      }

      &.shape-2 {
        width: 200px;
        height: 200px;
        bottom: -50px;
        right: -50px;
        animation-delay: 5s;
      }

      &.shape-3 {
        width: 150px;
        height: 150px;
        top: 50%;
        right: 20%;
        animation-delay: 10s;
      }

      &.shape-4 {
        width: 100px;
        height: 100px;
        bottom: 30%;
        left: 30%;
        animation-delay: 15s;
      }
    }
  }
}

/* 右侧登录表单 */
.login-section {
  width: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  padding: 60px;
  position: relative;

  .login-form-wrapper {
    width: 100%;
    max-width: 400px;
  }

  .form-header {
    text-align: center;
    margin-bottom: 40px;
    animation: fadeIn 0.8s ease-out;

    h2 {
      font-size: 28px;
      font-weight: 700;
      color: #303133;
      margin: 0 0 12px 0;
    }

    p {
      font-size: 14px;
      color: #909399;
      margin: 0;
      line-height: 1.6;
    }
  }

  .login-form {
    :deep(.el-input__wrapper) {
      padding: 8px 16px;
      box-shadow: 0 0 0 1px #dcdfe6 inset;
      transition: all 0.3s ease;

      &:hover {
        box-shadow: 0 0 0 1px #c0c4cc inset;
      }

      &.is-focus {
        box-shadow: 0 0 0 1px #667eea inset;
      }
    }

    :deep(.el-form-item) {
      margin-bottom: 24px;
    }

    .login-button {
      width: 100%;
      height: 48px;
      font-size: 16px;
      font-weight: 600;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border: none;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
      }

      &:active {
        transform: translateY(0);
      }
    }
  }

  .form-footer {
    text-align: center;
    margin-top: 24px;

    .register-link {
      color: #909399;
      text-decoration: none;
      font-size: 14px;
      transition: all 0.3s ease;

      span {
        color: #667eea;
        font-weight: 600;
      }

      &:hover {
        color: #667eea;
      }
    }
  }

  .bottom-info {
    margin-top: 60px;
    text-align: center;

    p {
      font-size: 12px;
      color: #c0c4cc;
      margin: 0;
    }
  }
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  25% {
    transform: translate(30px, -30px) rotate(90deg);
  }
  50% {
    transform: translate(-20px, 20px) rotate(180deg);
  }
  75% {
    transform: translate(20px, 10px) rotate(270deg);
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .showcase-section {
    padding: 40px;

    .features-grid {
      grid-template-columns: 1fr;
    }
  }
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }

  .showcase-section {
    min-height: 50vh;
    padding: 30px;

    .brand-header {
      margin-bottom: 30px;

      .logo-wrapper .brand-title {
        font-size: 32px;
      }
    }

    .features-grid {
      display: none;
    }
  }

  .login-section {
    width: 100%;
    padding: 30px;
  }
}
</style>
