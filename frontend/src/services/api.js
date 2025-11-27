import axios from 'axios';

// Configure base URL for backend API
const API_BASE_URL = 'http://localhost:5000/api';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Error interceptor for handling API errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle different types of errors
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
      return Promise.reject({
        message: error.response.data.error || 'An error occurred',
        status: error.response.status,
        details: error.response.data.details,
      });
    } else if (error.request) {
      // Request made but no response received
      console.error('Network Error:', error.request);
      return Promise.reject({
        message: 'Network error. Please check your connection and ensure the backend server is running.',
        status: 0,
      });
    } else {
      // Error in request setup
      console.error('Request Error:', error.message);
      return Promise.reject({
        message: error.message || 'An unexpected error occurred',
        status: -1,
      });
    }
  }
);

// ============================================
// Customer Service Functions
// ============================================

export const customerService = {
  // Get all customers
  getAll: async () => {
    const response = await apiClient.get('/customers');
    return response.data;
  },

  // Get customer by ID
  getById: async (id) => {
    const response = await apiClient.get(`/customers/${id}`);
    return response.data;
  },

  // Create new customer
  create: async (customerData) => {
    const response = await apiClient.post('/customers', customerData);
    return response.data;
  },

  // Update customer
  update: async (id, customerData) => {
    const response = await apiClient.put(`/customers/${id}`, customerData);
    return response.data;
  },

  // Delete customer
  delete: async (id) => {
    const response = await apiClient.delete(`/customers/${id}`);
    return response.data;
  },
};

// ============================================
// Driver Service Functions
// ============================================

export const driverService = {
  // Get all drivers
  getAll: async () => {
    const response = await apiClient.get('/drivers');
    return response.data;
  },

  // Get driver by ID
  getById: async (id) => {
    const response = await apiClient.get(`/drivers/${id}`);
    return response.data;
  },

  // Create new driver
  create: async (driverData) => {
    const response = await apiClient.post('/drivers', driverData);
    return response.data;
  },

  // Update driver
  update: async (id, driverData) => {
    const response = await apiClient.put(`/drivers/${id}`, driverData);
    return response.data;
  },

  // Delete driver
  delete: async (id) => {
    const response = await apiClient.delete(`/drivers/${id}`);
    return response.data;
  },
};

// ============================================
// Vehicle Service Functions
// ============================================

export const vehicleService = {
  // Get all vehicles
  getAll: async () => {
    const response = await apiClient.get('/vehicles');
    return response.data;
  },

  // Get vehicle by VIN
  getByVin: async (vin) => {
    const response = await apiClient.get(`/vehicles/${vin}`);
    return response.data;
  },

  // Create new vehicle
  create: async (vehicleData) => {
    const response = await apiClient.post('/vehicles', vehicleData);
    return response.data;
  },

  // Update vehicle
  update: async (vin, vehicleData) => {
    const response = await apiClient.put(`/vehicles/${vin}`, vehicleData);
    return response.data;
  },

  // Delete vehicle
  delete: async (vin) => {
    const response = await apiClient.delete(`/vehicles/${vin}`);
    return response.data;
  },
};

// ============================================
// Location Service Functions
// ============================================

export const locationService = {
  // Get all locations
  getAll: async () => {
    const response = await apiClient.get('/locations');
    return response.data;
  },

  // Get location by ID
  getById: async (id) => {
    const response = await apiClient.get(`/locations/${id}`);
    return response.data;
  },

  // Create new location
  create: async (locationData) => {
    const response = await apiClient.post('/locations', locationData);
    return response.data;
  },

  // Update location
  update: async (id, locationData) => {
    const response = await apiClient.put(`/locations/${id}`, locationData);
    return response.data;
  },

  // Delete location
  delete: async (id) => {
    const response = await apiClient.delete(`/locations/${id}`);
    return response.data;
  },
};

// ============================================
// Ride Service Functions
// ============================================

export const rideService = {
  // Get all rides
  getAll: async () => {
    const response = await apiClient.get('/rides');
    return response.data;
  },

  // Get ride by ID
  getById: async (id) => {
    const response = await apiClient.get(`/rides/${id}`);
    return response.data;
  },

  // Create new ride
  create: async (rideData) => {
    const response = await apiClient.post('/rides', rideData);
    return response.data;
  },

  // Update ride
  update: async (id, rideData) => {
    const response = await apiClient.put(`/rides/${id}`, rideData);
    return response.data;
  },

  // Delete ride
  delete: async (id) => {
    const response = await apiClient.delete(`/rides/${id}`);
    return response.data;
  },
};

// ============================================
// Payment Service Functions
// ============================================

export const paymentService = {
  // Get all payments
  getAll: async () => {
    const response = await apiClient.get('/payments');
    return response.data;
  },

  // Get payment by transaction ID
  getById: async (id) => {
    const response = await apiClient.get(`/payments/${id}`);
    return response.data;
  },

  // Create new payment
  create: async (paymentData) => {
    const response = await apiClient.post('/payments', paymentData);
    return response.data;
  },

  // Update payment
  update: async (id, paymentData) => {
    const response = await apiClient.put(`/payments/${id}`, paymentData);
    return response.data;
  },

  // Delete payment
  delete: async (id) => {
    const response = await apiClient.delete(`/payments/${id}`);
    return response.data;
  },
};

// ============================================
// Rating Service Functions
// ============================================

export const ratingService = {
  // Get all ratings
  getAll: async () => {
    const response = await apiClient.get('/ratings');
    return response.data;
  },

  // Get rating by ID
  getById: async (id) => {
    const response = await apiClient.get(`/ratings/${id}`);
    return response.data;
  },

  // Create new rating
  create: async (ratingData) => {
    const response = await apiClient.post('/ratings', ratingData);
    return response.data;
  },

  // Update rating
  update: async (id, ratingData) => {
    const response = await apiClient.put(`/ratings/${id}`, ratingData);
    return response.data;
  },

  // Delete rating
  delete: async (id) => {
    const response = await apiClient.delete(`/ratings/${id}`);
    return response.data;
  },
};

// ============================================
// Report Service Functions
// ============================================

export const reportService = {
  // Get top drivers by ride count
  getTopDrivers: async () => {
    const response = await apiClient.get('/reports/top-drivers');
    return response.data;
  },

  // Get revenue by payment method
  getRevenueByMethod: async () => {
    const response = await apiClient.get('/reports/revenue-by-method');
    return response.data;
  },

  // Get average ratings by driver
  getAverageRatings: async () => {
    const response = await apiClient.get('/reports/average-ratings');
    return response.data;
  },

  // Get rides by location
  getRidesByLocation: async () => {
    const response = await apiClient.get('/reports/rides-by-location');
    return response.data;
  },

  // Get customer ride history
  getCustomerHistory: async (customerId) => {
    const response = await apiClient.get(`/reports/customer-history/${customerId}`);
    return response.data;
  },
};

// Export the configured axios instance for custom requests if needed
export default apiClient;
