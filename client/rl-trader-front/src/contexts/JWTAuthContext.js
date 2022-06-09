import React, { createContext, useEffect, useReducer } from 'react';
import API from 'src/Api';
// import jwtDecode from 'jwt-decode';
import SplashScreen from 'src/components/SplashScreen';
import axios from 'src/utils/axios';

const initialAuthState = {
  isAuthenticated: false,
  isInitialised: false
};

const setSession = accessToken => {
  if (accessToken) {
    localStorage.setItem('accessToken', accessToken);
    axios.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
  } else {
    localStorage.removeItem('accessToken');
    delete axios.defaults.headers.common.Authorization;
  }
};

const reducer = (state, action) => {
  switch (action.type) {
    case 'INITIALISE': {
      const { isAuthenticated } = action.payload;

      return {
        ...state,
        isAuthenticated,
        isInitialised: true
      };
    }
    case 'LOGIN': {
      return {
        ...state,
        isAuthenticated: true
      };
    }
    case 'LOGOUT': {
      return {
        ...state,
        isAuthenticated: false
      };
    }
    case 'REGISTER': {
      return {
        ...state,
        isAuthenticated: true
      };
    }
    default: {
      return { ...state };
    }
  }
};

const AuthContext = createContext({
  ...initialAuthState,
  method: 'JWT',
  login: () => Promise.resolve(),
  logout: () => {},
  register: () => Promise.resolve()
});

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialAuthState);

  const login = async key => {
    const response = await API.post('/api/auth', { key: key });
    const { accessToken } = response.data;

    setSession(accessToken);
    dispatch({
      type: 'LOGIN',
      payload: {}
    });
  };

  const logout = () => {
    setSession(null);
    dispatch({ type: 'LOGOUT' });
  };

  const register = async (email, name, password) => {
    const response = await axios.post('/api/account/register', {
      email,
      name,
      password
    });
    const { accessToken, user } = response.data;

    window.localStorage.setItem('accessToken', accessToken);

    dispatch({
      type: 'REGISTER',
      payload: {
        user
      }
    });
  };

  useEffect(() => {
    const initialise = async () => {
      try {
        const accessToken = window.localStorage.getItem('accessToken');

        if (accessToken) {
          setSession(accessToken);
          dispatch({
            type: 'INITIALISE',
            payload: {
              isAuthenticated: true
            }
          });
        } else {
          dispatch({
            type: 'INITIALISE',
            payload: {
              isAuthenticated: false
            }
          });
        }
      } catch (err) {
        console.error(err);
        dispatch({
          type: 'INITIALISE',
          payload: {
            isAuthenticated: false
          }
        });
      }
    };

    initialise();
  }, []);

  if (!state.isInitialised) {
    return <SplashScreen />;
  }

  return (
    <AuthContext.Provider
      value={{
        ...state,
        method: 'JWT',
        login,
        logout,
        register
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
