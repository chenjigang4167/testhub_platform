import { createI18n } from 'vue-i18n'
import zhCn from './lang/zh-cn/index.js'
import en from './lang/en/index.js'
import { datetimeFormats } from './datetimeFormats.js'
import { numberFormats } from './numberFormats.js'
import { pluralRules } from './pluralRules.js'

// 从 localStorage 获取语言设置，默认中文
const defaultLang = localStorage.getItem('app-lang') || 'zh-cn'

// 开发环境下的缺失翻译警告处理器
const missingHandler = (locale, key, vm, values) => {
  if (import.meta.env.DEV) {
    console.warn(`[i18n] Missing translation: "${key}" for locale "${locale}"`)
  }
  // 返回 key 本身作为兜底显示
  return key
}

const i18n = createI18n({
  legacy: false, // 必须设置 false 才能使用 Composition API
  locale: defaultLang,
  fallbackLocale: 'zh-cn', // 缺省语言
  globalInjection: true, // 全局注入 $t 函数

  // 语言消息
  messages: {
    'zh-cn': zhCn,
    'en': en
  },

  // 日期时间格式化
  datetimeFormats,

  // 数字格式化
  numberFormats,

  // 复数规则
  pluralRules,

  // 缺失翻译处理
  missing: missingHandler,

  // 缺失翻译警告 - 开发环境开启
  missingWarn: import.meta.env.DEV,

  // 回退警告 - 开发环境开启
  fallbackWarn: import.meta.env.DEV
})

export default i18n
