import { defineStore } from 'pinia'
import { ref } from 'vue'
import i18n from '@/locales'

export const useAppStore = defineStore('app', () => {
  // 状态：当前语言
  const language = ref(localStorage.getItem('app-lang') || 'zh-cn')

  // 动作：切换语言
  const setLanguage = (lang) => {
    language.value = lang
    // 1. 修改 i18n 实例语言
    i18n.global.locale.value = lang
    // 2. 持久化
    localStorage.setItem('app-lang', lang)
    // 3. 设置 HTML 标签 lang 属性，利于 SEO 和浏览器识别
    document.querySelector('html')?.setAttribute('lang', lang)
  }

  return { language, setLanguage }
})
