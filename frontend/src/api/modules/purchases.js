import axios from '../index'

export const getPurchases = (params) => axios.get('/purchases', { params })
export const getPurchase = (id) => axios.get(`/purchases/${id}`)
export const createPurchase = (data) => axios.post('/purchases', data)
export const updatePurchase = (id, data) => axios.put(`/purchases/${id}`, data)
export const deletePurchase = (id) => axios.delete(`/purchases/${id}`)
export const receivePurchase = (id, data) => axios.post(`/purchases/${id}/receive`, data)
