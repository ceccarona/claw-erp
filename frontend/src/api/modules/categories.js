import axios from '../index'

export const getCategories = (params) => axios.get('/categories', { params })
export const getAllCategories = () => axios.get('/categories/all')
export const getCategory = (id) => axios.get(`/categories/${id}`)
export const createCategory = (data) => axios.post('/categories', data)
export const updateCategory = (id, data) => axios.put(`/categories/${id}`, data)
export const deleteCategory = (id) => axios.delete(`/categories/${id}`)
