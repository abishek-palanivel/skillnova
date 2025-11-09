import { createContext, useContext, useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import api from '../utils/api';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for existing token on app load
  useEffect(() => {
    const token = Cookies.get('skillnova_token');
    if (token) {
      // Set token in API headers
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Verify token and get user profile
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await api.get('/auth/profile');
      if (response.data.success) {
        setUser(response.data.user);
      } else {
        // Token is invalid, remove it
        logout();
      }
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      
      if (response.data.success) {
        const { user: userData, access_token } = response.data;
        
        // Store token in cookie (expires in 24 hours)
        Cookies.set('skillnova_token', access_token, { expires: 1 });
        
        // Set token in API headers
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        
        // Set user state
        setUser(userData);
        
        toast.success(response.data.message);
        return { success: true, user: userData };
      } else {
        toast.error(response.data.message);
        return { success: false, message: response.data.message };
      }
    } catch (error) {
      const message = error.response?.data?.message || 'Login failed. Please try again.';
      toast.error(message);
      return { success: false, message };
    }
  };

  const signup = async (name, email, password) => {
    try {
      const response = await api.post('/auth/signup', { name, email, password });
      
      if (response.data.success) {
        const { user: userData, access_token } = response.data;
        
        // Store token in cookie
        Cookies.set('skillnova_token', access_token, { expires: 1 });
        
        // Set token in API headers
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        
        // Set user state
        setUser(userData);
        
        toast.success(response.data.message);
        return { success: true, user: userData };
      } else {
        toast.error(response.data.message);
        return { success: false, message: response.data.message };
      }
    } catch (error) {
      const message = error.response?.data?.message || 'Signup failed. Please try again.';
      toast.error(message);
      return { success: false, message };
    }
  };

  const logout = () => {
    // Remove token from cookie
    Cookies.remove('skillnova_token');
    
    // Remove token from API headers
    delete api.defaults.headers.common['Authorization'];
    
    // Clear user state
    setUser(null);
    
    toast.success('Logged out successfully');
  };

  const forgotPassword = async (email) => {
    try {
      const response = await api.post('/auth/forgot-password', { email });
      
      if (response.data.success) {
        toast.success(response.data.message);
        return { success: true };
      } else {
        toast.error(response.data.message);
        return { success: false, message: response.data.message };
      }
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to send reset email.';
      toast.error(message);
      return { success: false, message };
    }
  };

  const resetPassword = async (token, newPassword) => {
    try {
      const response = await api.post('/auth/reset-password', {
        token,
        new_password: newPassword
      });
      
      if (response.data.success) {
        toast.success(response.data.message);
        return { success: true };
      } else {
        toast.error(response.data.message);
        return { success: false, message: response.data.message };
      }
    } catch (error) {
      const message = error.response?.data?.message || 'Password reset failed.';
      toast.error(message);
      return { success: false, message };
    }
  };

  const updateUser = (userData) => {
    setUser(prevUser => ({ ...prevUser, ...userData }));
  };

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
    forgotPassword,
    resetPassword,
    updateUser,
    isAuthenticated: !!user,
    isAdmin: user?.is_admin || false,
    isMentor: user?.is_mentor || false
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};