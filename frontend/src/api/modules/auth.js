import axios from '../index'

export const login = (username, password) => {
  return axios.post('/auth/login', { username, password })
}

export const logout = () => {
  return axios.post('/auth/logout')
}

export const getCurrentUser = () => {
  return axios.get('/auth/me')
}
