import axios from 'axios';
const defaultApiBase=`${window.location.protocol}//${window.location.hostname}:8000/api`;
export const api=axios.create({baseURL:import.meta.env.VITE_API_BASE_URL||defaultApiBase,timeout:15000});
api.interceptors.request.use(config=>{const token=localStorage.getItem('northstar_token');if(token)config.headers.Authorization=`Bearer ${token}`;return config});
api.interceptors.response.use(response=>response,error=>{if(error.response?.status===401&&localStorage.getItem('northstar_token')){localStorage.removeItem('northstar_token');localStorage.removeItem('northstar_user');window.location.assign('/login')}return Promise.reject(error)});
export async function get(path){return (await api.get(path)).data}
