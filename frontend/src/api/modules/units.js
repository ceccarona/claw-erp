import axios from '../index'

export const getUnits = (params) => axios.get('/units', { params })
export const getAllUnits = () => axios.get('/units/all')
export const getUnit = (id) => axios.get(`/units/${id}`)
export const createUnit = (data) => axios.post('/units', data)
export const updateUnit = (id, data) => axios.put(`/units/${id}`, data)
export const deleteUnit = (id) => axios.delete(`/units/${id}`)
