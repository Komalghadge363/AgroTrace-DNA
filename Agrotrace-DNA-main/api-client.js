(function () {
  const API_BASE_STORAGE_KEY = 'cropid_api_base';
  const ACCESS_TOKEN_KEY = 'access_token';
  const REFRESH_TOKEN_KEY = 'refresh_token';
  const USER_KEY = 'user';

  function resolveApiBaseUrl() {
    const saved = localStorage.getItem(API_BASE_STORAGE_KEY);
    if (saved) {
      return saved.replace(/\/$/, '');
    }

    const host = window.location.hostname || '127.0.0.1';
    return `http://${host}:5000/api`;
  }

  async function request(path, options) {
    const config = options || {};
    const headers = new Headers(config.headers || {});

    if (config.body && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(`${resolveApiBaseUrl()}${path}`, {
      ...config,
      headers
    });

    const raw = await response.text();
    let data = {};

    if (raw) {
      try {
        data = JSON.parse(raw);
      } catch (error) {
        data = { message: raw };
      }
    }

    if (!response.ok) {
      const apiError = new Error(data.message || `Request failed with status ${response.status}`);
      apiError.status = response.status;
      apiError.data = data;
      throw apiError;
    }

    return data;
  }

  function saveSession(authData) {
    if (authData.access_token) {
      localStorage.setItem(ACCESS_TOKEN_KEY, authData.access_token);
    }
    if (authData.refresh_token) {
      localStorage.setItem(REFRESH_TOKEN_KEY, authData.refresh_token);
    }
    if (authData.user) {
      localStorage.setItem(USER_KEY, JSON.stringify(authData.user));
    }
  }

  function clearSession() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  function getStoredUser() {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) {
      return null;
    }

    try {
      return JSON.parse(raw);
    } catch (error) {
      return null;
    }
  }

  function getRoleRedirect(role, fallbackRole) {
    const redirectMap = {
      farmer: 'crop-soil-input.html',
      admin: 'admin-dashboard.html',
      distributor: 'supply-chain.html',
      supplier: 'supply-chain.html',
      consumer: 'consumer-verification.html',
      inspector: 'supply-chain.html'
    };

    return redirectMap[role] || redirectMap[fallbackRole] || 'index.html';
  }

  function getAccessToken() {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }

  function getAuthHeaders(extraHeaders) {
    const headers = new Headers(extraHeaders || {});
    const token = getAccessToken();

    if (!headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    if (token && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    return headers;
  }

  // ======= AUTH ENDPOINTS =======
  async function register(userData) {
    const response = await request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
    saveSession(response);
    
    // Auto-login after registration
    if (response.user && response.user.role) {
      const redirectUrl = getRoleRedirect(response.user.role);
      setTimeout(() => {
        window.location.href = redirectUrl;
      }, 500); // Brief delay to let registration complete
    }
    
    return response;
  }

  async function login(username, password) {
    const response = await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    saveSession(response);
    
    // Auto-redirect based on role
    if (response.user && response.user.role) {
      const redirectUrl = getRoleRedirect(response.user.role);
      setTimeout(() => {
        window.location.href = redirectUrl;
      }, 500); // Brief delay to let login complete
    }
    
    return response;
  }

  async function logout() {
    try {
      await request('/auth/logout', {
        method: 'POST',
        headers: getAuthHeaders()
      });
    } finally {
      clearSession();
    }
  }

  async function refreshToken() {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken) throw new Error('No refresh token available');
    
    const response = await request('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    saveSession(response);
    return response;
  }

  async function verifyToken() {
    return await request('/auth/verify', {
      method: 'GET',
      headers: getAuthHeaders()
    });
  }

  // ======= USER ENDPOINTS =======
  async function getUserProfile() {
    return await request('/users/profile', {
      method: 'GET',
      headers: getAuthHeaders()
    });
  }

  async function updateUserProfile(userData) {
    return await request('/users/profile', {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(userData)
    });
  }

  async function changePassword(currentPassword, newPassword) {
    return await request('/users/change-password', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
    });
  }

  async function getUserById(userId) {
    return await request(`/users/${userId}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
  }

  // ======= CROP ENDPOINTS =======
  async function createCrop(cropData) {
    return await request('/crops', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(cropData)
    });
  }

  async function getCrops(page = 1, perPage = 20) {
    return await request(`/crops?page=${page}&per_page=${perPage}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
  }

  async function getCropById(cropId) {
    return await request(`/crops/${cropId}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
  }

  async function updateCrop(cropId, cropData) {
    return await request(`/crops/${cropId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(cropData)
    });
  }

  async function deleteCrop(cropId) {
    return await request(`/crops/${cropId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
  }

  async function trackCrop(cropCode) {
    return await request(`/crops/${cropCode}/track`, {
      method: 'GET'
    });
  }

  // ======= SUPPLY CHAIN ENDPOINTS =======
  async function addSupplyChainRecord(recordData) {
    return await request('/supply-chain', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(recordData)
    });
  }

  async function getSupplyChainHistory(cropId) {
    return await request(`/supply-chain/crop/${cropId}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
  }

  async function updateSupplyChainRecord(recordId, recordData) {
    return await request(`/supply-chain/${recordId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(recordData)
    });
  }

  async function getPublicSupplyChain(cropCode) {
    return await request(`/supply-chain/${cropCode}/public`, {
      method: 'GET'
    });
  }

  // ======= QR CODE ENDPOINTS =======
  async function generateQRCode(cropId) {
    return await request('/qr/generate', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ crop_id: cropId })
    });
  }

  async function viewQRCode(qrCode) {
    return await request(`/qr/${qrCode}/view`, {
      method: 'GET'
    });
  }

  async function downloadQRImage(filename) {
    return `${resolveApiBaseUrl()}/qr/download/${filename}`;
  }

  async function generateQRImage(cropId) {
    return await request('/qr/generate-image', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ crop_id: cropId })
    });
  }

  // ======= ADMIN ENDPOINTS =======
  async function getSystemStatistics() {
    return await request('/admin/statistics', {
      method: 'GET',
      headers: getAuthHeaders()
    });
  }

  async function getAuditLogs(page = 1, perPage = 20) {
    return await request(`/admin/audit-logs?page=${page}&per_page=${perPage}`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
  }

  async function verifyUser(userId) {
    return await request(`/admin/users/${userId}/verify`, {
      method: 'PATCH',
      headers: getAuthHeaders()
    });
  }

  async function getSystemHealth() {
    return await request('/admin/health', {
      method: 'GET',
      headers: getAuthHeaders()
    });
  }

  // ======= UTILITY =======
  async function getHealth() {
    return await request('/health', {
      method: 'GET'
    });
  }

  async function forgotPassword(email) {
    return await request('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email })
    });
  }

  async function getGoogleConfig() {
    return await request('/auth/google-config', {
      method: 'GET'
    });
  }

  async function verifyOTP(email, otp, newPassword) {
    return await request('/auth/verify-otp', {
      method: 'POST',
      body: JSON.stringify({ email, otp, new_password: newPassword })
    });
  }

  async function googleLogin(credential, requestedRole) {
    const response = await request('/auth/google-login', {
      method: 'POST',
      body: JSON.stringify({ credential, requested_role: requestedRole })
    });
    saveSession(response);
    
    // Auto-redirect based on role
    if (response.user && response.user.role) {
      const redirectUrl = getRoleRedirect(response.user.role);
      setTimeout(() => {
        window.location.href = redirectUrl;
      }, 500); // Brief delay to let login complete
    }
    
    return response;
  }

  // ======= ROLE-BASED ACCESS CONTROL =======
  function checkPageAccess(requiredRoles = []) {
    const user = getStoredUser();
    
    if (!user) {
      // Not logged in, redirect to login
      window.location.href = 'login.html';
      return false;
    }

    if (requiredRoles.length === 0) {
      // No role restriction
      return true;
    }

    if (!requiredRoles.includes(user.role)) {
      // User doesn't have required role, redirect to appropriate page
      const redirectUrl = getRoleRedirect(user.role);
      window.location.href = redirectUrl;
      return false;
    }

    return true;
  }

  window.CropIdApi = {
    resolveApiBaseUrl,
    request,
    saveSession,
    clearSession,
    getStoredUser,
    getRoleRedirect,
    getAccessToken,
    getAuthHeaders,
    checkPageAccess,
    // Auth methods
    register,
    login,
    logout,
    refreshToken,
    verifyToken,
    // User methods
    getUserProfile,
    updateUserProfile,
    changePassword,
    getUserById,
    // Crop methods
    createCrop,
    getCrops,
    getCropById,
    updateCrop,
    deleteCrop,
    trackCrop,
    // Supply Chain methods
    addSupplyChainRecord,
    getSupplyChainHistory,
    updateSupplyChainRecord,
    getPublicSupplyChain,
    // QR Code methods
    generateQRCode,
    viewQRCode,
    downloadQRImage,
    generateQRImage,
    // Admin methods
    getSystemStatistics,
    getAuditLogs,
    verifyUser,
    getSystemHealth,
    // Utility
    getHealth,
    forgotPassword,
    getGoogleConfig,
    verifyOTP,
    googleLogin
  };
})();
