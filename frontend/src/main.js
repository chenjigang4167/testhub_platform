import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import i18n from './locales'

import App from './App.vue'
import router from './router'
import './assets/css/global.scss'

// Axios aÃ¥ÂÂºÃ§Â½Â®
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.withCredentials = true; // Ã¥ÂÂÃ¨Â®Â¸Ã¨Â·Â¨Ã¨Â¯Â·Ã¥Â¸Â¦ Cookie

const app = createApp(App)

app.use(createPinia())

const userStore = useUserStore()

async function init() {
  try {
    await userStore.initAuth()
  } catch (error) {
    // 获取用户信息失败，说明未登录，无需处理
  }

  // 注册所有图标
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }

  app.use(router)
  app.use(i18n)

  // Element Plus 语言由 App.vue 的 el-config-provider 动态配置
  app.use(ElementPlus)

  app.mount('#app')
}

init()

