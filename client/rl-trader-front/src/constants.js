export const APP_VERSION = '3.1.0';

export const ENABLE_REDUX_DEV_TOOLS = true;

export const THEMES = {
  LIGHT: 'LIGHT',
  ONE_DARK: 'ONE_DARK',
  UNICORN: 'UNICORN'
};


const LOCATION = process.env.NODE_ENV === "development" ? 'localhost:8000' : window.location.hostname;

export const SERVER_URL = `http://${LOCATION}`;
export const SOCKET_URL = `ws://${LOCATION}`;
