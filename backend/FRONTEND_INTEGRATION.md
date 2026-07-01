# Frontend Integration Guide

This guide shows how to integrate the Agrotrace-DNA frontend with the Python backend API.

## API Base URL

Update your frontend configuration to point to the backend:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
```

## Authentication Flow

### 1. User Registration

```javascript
async function registerUser(userData) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: userData.username,
      email: userData.email,
      password: userData.password,
      full_name: userData.fullName,
      role: userData.role || 'farmer',
      farm_name: userData.farmName
    })
  });
  
  return await response.json();
}
```

### 2. User Login

```javascript
async function loginUser(username, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  const data = await response.json();
  
  // Store tokens
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  
  return data;
}
```

### 3. Authenticated Requests

```javascript
function getAuthHeaders() {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}

async function makeAuthenticatedRequest(url, options = {}) {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: getAuthHeaders()
  });
  
  if (response.status === 401) {
    // Token expired, try to refresh
    await refreshAccessToken();
    return makeAuthenticatedRequest(url, options);
  }
  
  return await response.json();
}
```

### 4. Refresh Token

```javascript
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  });
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  
  return data;
}
```

## Integration Examples

### Farmer Registration Page

Connect your farmer registration form to the backend:

```javascript
// farmer-registration.html
document.getElementById('registerForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = {
    username: document.getElementById('username').value,
    email: document.getElementById('email').value,
    password: document.getElementById('password').value,
    fullName: document.getElementById('fullName').value,
    farmName: document.getElementById('farmName').value,
    role: 'farmer'
  };
  
  try {
    const result = await registerUser(formData);
    if (result.message) {
      alert('Registration successful! Please login.');
      window.location.href = 'login.html';
    }
  } catch (error) {
    console.error('Registration error:', error);
    alert('Registration failed');
  }
});
```

### Login Page

```javascript
// login.html
document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  
  try {
    const result = await loginUser(username, password);
    window.location.href = `admin-dashboard.html?user=${result.user.role}`;
  } catch (error) {
    console.error('Login error:', error);
    alert('Login failed');
  }
});
```

### Crop Management Page

```javascript
// admin-dashboard.html
async function loadCrops() {
  try {
    const crops = await makeAuthenticatedRequest('/crops?page=1&per_page=20');
    displayCrops(crops.crops);
  } catch (error) {
    console.error('Error loading crops:', error);
  }
}

async function createCrop(cropData) {
  try {
    const result = await makeAuthenticatedRequest('/crops', {
      method: 'POST',
      body: JSON.stringify({
        crop_type: cropData.cropType,
        variety: cropData.variety,
        planting_date: cropData.plantingDate,
        soil_type: cropData.soilType,
        area_planted: cropData.areaPlanted,
        is_organic: cropData.isOrganic
      })
    });
    
    alert('Crop created successfully');
    loadCrops();
  } catch (error) {
    console.error('Error creating crop:', error);
  }
}
```

### Consumer Verification Page

```javascript
// consumer-verification.html
async function verifyCrop(cropIdCode) {
  try {
    const response = await fetch(`${API_BASE_URL}/crops/${cropIdCode}/track`);
    const crop = await response.json();
    
    // Display crop information
    displayCropInfo(crop);
    
    // Get supply chain history
    const supplyChain = await fetch(
      `${API_BASE_URL}/supply-chain/${cropIdCode}/public`
    );
    const history = await supplyChain.json();
    
    displaySupplyChainHistory(history.records);
  } catch (error) {
    console.error('Error verifying crop:', error);
  }
}
```

### Supply Chain Tracking Page

```javascript
// supply-chain.html
async function trackSupplyChain(cropId) {
  try {
    const records = await makeAuthenticatedRequest(
      `/supply-chain/crop/${cropId}`
    );
    
    displaySupplyChainTimeline(records.records);
  } catch (error) {
    console.error('Error tracking supply chain:', error);
  }
}

async function addSupplyChainRecord(cropId, recordData) {
  try {
    const result = await makeAuthenticatedRequest('/supply-chain', {
      method: 'POST',
      body: JSON.stringify({
        crop_id: cropId,
        stage: recordData.stage,
        location: recordData.location,
        temperature: recordData.temperature,
        humidity: recordData.humidity,
        handler_name: recordData.handlerName,
        notes: recordData.notes
      })
    });
    
    alert('Record added successfully');
    trackSupplyChain(cropId);
  } catch (error) {
    console.error('Error adding record:', error);
  }
}
```

### QR Code Generation

```javascript
// QR-Generator.html
async function generateQRCode(cropId) {
  try {
    const result = await makeAuthenticatedRequest('/qr/generate', {
      method: 'POST',
      body: JSON.stringify({ crop_id: cropId })
    });
    
    // Display QR code
    displayQRCode(result.qr_code_url);
  } catch (error) {
    console.error('Error generating QR code:', error);
  }
}

// Display QR code from download endpoint
function displayQRCode(qrUrl) {
  const img = document.createElement('img');
  img.src = `${API_BASE_URL}${qrUrl}`;
  document.getElementById('qrContainer').appendChild(img);
}
```

### User Profile Page

```javascript
// User profile management
async function loadUserProfile() {
  try {
    const user = await makeAuthenticatedRequest('/users/profile');
    populateProfileForm(user.user);
  } catch (error) {
    console.error('Error loading profile:', error);
  }
}

async function updateUserProfile(profileData) {
  try {
    const result = await makeAuthenticatedRequest('/users/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    });
    
    alert('Profile updated successfully');
    localStorage.setItem('user', JSON.stringify(result.user));
  } catch (error) {
    console.error('Error updating profile:', error);
  }
}
```

## CORS Configuration

Ensure your frontend URL is added to backend CORS settings:

```bash
# In .env file
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://yourdomain.com
```

## Environment Variables for Frontend

Create `.env` file in your frontend root:

```bash
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_JWT_EXPIRATION=24
```

## Error Handling

```javascript
async function handleApiError(error) {
  if (error.status === 401) {
    // Unauthorized - clear stored tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = 'login.html';
  } else if (error.status === 403) {
    alert('You do not have permission to access this resource');
  } else if (error.status === 404) {
    alert('Resource not found');
  } else if (error.status === 500) {
    alert('Server error - please try again later');
  }
}
```

## Testing the Integration

1. Start the backend:
```bash
python run.py
```

2. Open your frontend pages in browser

3. Register a new user

4. Login with credentials

5. Create and manage crops

6. View supply chain tracking

7. Verify crops as consumer

## Deployment Notes

For production:

1. Update `REACT_APP_API_URL` to production backend URL
2. Ensure HTTPS is enabled
3. Add production domain to backend CORS
4. Implement proper error logging
5. Add loading states and error handling UI
6. Cache API responses where appropriate
