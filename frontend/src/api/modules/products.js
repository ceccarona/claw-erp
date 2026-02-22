import axios from '../index'

export const getProducts = (params) => axios.get('/products', { params })
export const getProduct = (id) => axios.get(`/products/${id}`)
export const createProduct = (data) => axios.post('/products', data)
export const updateProduct = (id, data) => axios.put(`/products/${id}`, data)
export const deleteProduct = (id) => axios.delete(`/products/${id}`)

export const getCategories = () => axios.get('/categories')
export const getUnits = () => axios.get('/units')
