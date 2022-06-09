import Axios from 'axios';
import { SERVER_URL } from 'src/constants';

const API = Axios.create({
  baseURL: `${SERVER_URL}/`,
  timeout: 10000
});

API.interceptors.request.use(config => {
  const accessToken = window.localStorage.getItem('accessToken');
  if (accessToken) config.headers.Authorization = `token ${accessToken}`;
  config.headers['Content-Type'] = 'application/json';
  return config;
});

export default API;
