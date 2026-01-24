import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const tokenExpiresAt = ref(parseInt(localStorage.getItem('token_expires_at') || '0'))

  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)

  // 检查token是否即将过期（5分钟内）
  const isTokenExpiringSoon = computed(() => {
    if (!tokenExpiresAt.value) return false
    const now = Date.now()
    const timeLeft = tokenExpiresAt.value - now
    return timeLeft < 5 * 60 * 1000 // 5分钟
  })

  // 检查token是否已过期
  const isTokenExpired = computed(() => {
    if (!tokenExpiresAt.value) return false
    return Date.now() > tokenExpiresAt.value
  })

  const login = async (credentials) => {
    try {
      const response = await api.post('/auth/login/', credentials)

      // 保存双token
      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh
      user.value = response.data.user

      // 计算过期时间（当前时间 + 30分钟）
      const expiresAt = Date.now() + 30 * 60 * 1000
      tokenExpiresAt.value = expiresAt

      // 持久化存储
      localStorage.setItem('access_token', accessToken.value)
      localStorage.setItem('refresh_token', refreshToken.value)
      localStorage.setItem('token_expires_at', expiresAt.toString())
      localStorage.setItem('user', JSON.stringify(user.value))

      return response.data
    } catch (error) {
      throw error
    }
  }

  const register = async (userData) => {
    try {
      // 临时使用测试接口
      const response = await api.post('/auth/test-register/', userData)

      // 注册成功后不自动登录，不保存token和用户信息
      // 让用户手动登录
      return response.data
    } catch (error) {
      throw error
    }
  }

  // 添加一个标记防止logout过程中的循环调用
  let isLoggingOut = false

  const logout = async () => {
    // 防止重复调用logout
    if (isLoggingOut) {
      return
    }
    isLoggingOut = true

    try {
      // 只有当access token未过期时，才尝试调用logout API将refresh token加入黑名单
      // 如果token已过期，直接清除本地状态即可，避免401死循环
      if (refreshToken.value && !isTokenExpired.value) {
        try {
          await api.post('/auth/logout/', { refresh: refreshToken.value })
        } catch (apiError) {
          // logout API调用失败不影响本地清除操作
          console.error('Logout API调用失败:', apiError)
        }
      }
    } finally {
      // 清除所有认证信息
      accessToken.value = ''
      refreshToken.value = ''
      user.value = null
      tokenExpiresAt.value = 0

      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('token_expires_at')
      localStorage.removeItem('user')

      // 重置标记
      isLoggingOut = false

      window.location.href = '/login'
    }
  }

  // 刷新access token
  const refreshAccessToken = async () => {
    try {
      const response = await api.post('/auth/token/refresh/', {
        refresh: refreshToken.value
      })

      // 更新access token和过期时间
      accessToken.value = response.data.access
      const expiresAt = Date.now() + 30 * 60 * 1000
      tokenExpiresAt.value = expiresAt

      // 如果返回了新的refresh token（启用了ROTATE_REFRESH_TOKENS）
      if (response.data.refresh) {
        refreshToken.value = response.data.refresh
        localStorage.setItem('refresh_token', refreshToken.value)
      }

      // 持久化存储
      localStorage.setItem('access_token', accessToken.value)
      localStorage.setItem('token_expires_at', expiresAt.toString())

      return response.data.access
    } catch (error) {
      // 刷新失败，清除所有认证信息
      console.error('Token refresh failed:', error)
      await logout()
      throw error
    }
  }

  const fetchUser = async () => {
    try {
      const response = await api.get('/users/me/')
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(user.value))
    } catch (error) {
      await logout()
      throw error
    }
  }

  const fetchProfile = async () => {
    try {
      const response = await api.get('/auth/profile/')
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(user.value))
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        await logout()
      }
      throw error
    }
  }

  const initAuth = async () => {
    console.log('initAuth 开始:', {
      hasAccessToken: !!accessToken.value,
      hasRefreshToken: !!refreshToken.value,
      hasUser: !!user.value,
      isExpired: isTokenExpired.value
    })

    // 从localStorage恢复用户信息
    if (!user.value) {
      const savedUser = localStorage.getItem('user')
      if (savedUser) {
        try {
          user.value = JSON.parse(savedUser)
        } catch (e) {
          console.error('解析用户信息失败:', e)
        }
      }
    }

    if (accessToken.value) {
      // 检查token是否过期
      if (isTokenExpired.value && refreshToken.value) {
        console.log('Token已过期，尝试刷新...')
        try {
          await refreshAccessToken()
          console.log('Token刷新成功')
        } catch (error) {
          console.error('Token刷新失败:', error)
          return
        }
      }

      // 获取用户信息
      if (!user.value) {
        try {
          console.log('获取用户信息...')
          await fetchProfile()
          console.log('用户信息获取成功:', user.value?.username)
        } catch (error) {
          console.error('获取用户信息失败:', error)
          await logout()
        }
      } else {
        console.log('用户信息已存在，跳过获取')
      }
    } else {
      console.log('没有access token，跳过认证初始化')
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    tokenExpiresAt,
    isAuthenticated,
    isTokenExpiringSoon,
    isTokenExpired,
    login,
    register,
    logout,
    refreshAccessToken,
    fetchProfile,
    initAuth
  }
})
