import axios from '../index'

export const getSales = (params) => axios.get('/sales', { params })
export const getSale = (id) => axios.get(`/sales/${id}`)
export const createSale = (data) => axios.post('/sales', data)
export const updateSale = (id, data) => axios.put(`/sales/${id}`, data)
export const deleteSale = (id) => axios.delete(`/sales/${id}`)
export const deliverSale = (id, data) => axios.post(`/sales/${id}/deliver`, data)
