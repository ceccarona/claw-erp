import axios from '../index'

export const getInventory = (params) => axios.get('/inventory', { params })
export const getInventoryLogs = (params) => axios.get('/inventory/logs', { params })
export const checkInventory = (data) => axios.post('/inventory/check', data)
