import axios from "axios"
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "./auth"

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL + "/v1",
})

api.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config
    if (err.response?.status === 401 && original.url?.includes("/auth/"))
      return Promise.reject(err)
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const refresh = getRefreshToken()
        if (!refresh) throw new Error("No refresh token")
        const res = await axios.post(
          process.env.NEXT_PUBLIC_API_URL + "/v1/auth/refresh",
          { refresh_token: refresh }
        )
        setTokens(res.data.access_token, res.data.refresh_token)
        original.headers.Authorization = `Bearer ${res.data.access_token}`
        return api(original)
      } catch {
        clearTokens()
        window.location.href = "/login"
      }
    }
    return Promise.reject(err)
  }
)