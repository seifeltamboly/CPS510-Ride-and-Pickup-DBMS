import { useState, useEffect } from 'react';
import { rideService, customerService, driverService, vehicleService, locationService } from '../services/api';
import ErrorMessage from './ErrorMessage';
import { isRequired, isAfter, getErrorMessage } from '../utils/validation';
import './RideForm.css';

function RideForm({ ride, onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    customer_id: '',
    driver_id: '',
    vehicle_vin: '',
    pickup_location: '',
    dropoff_location: '',
    start_time: '',
    arrival_time: '',
  });
  
  // State for dropdown options
  const [customers, setCustomers] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [locations, setLocations] = useState([]);
  
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState(null);
  const [loadingData, setLoadingData] = useState(true);

  const isEditMode = !!ride;

  // Load all required data on component mount
  useEffect(() => {
    loadAllData();
  }, []);

  // Populate form when editing
  useEffect(() => {
    if (ride) {
      // Format datetime for input fields (expects YYYY-MM-DDTHH:mm format)
      const formatForInput = (dateTimeStr) => {
        if (!dateTimeStr) return '';
        try {
          const date = new Date(dateTimeStr);
          // Convert to local timezone and format for datetime-local input
          const year = date.getFullYear();
          const month = String(date.getMonth() + 1).padStart(2, '0');
          const day = String(date.getDate()).padStart(2, '0');
          const hours = String(date.getHours()).padStart(2, '0');
          const minutes = String(date.getMinutes()).padStart(2, '0');
          return `${year}-${month}-${day}T${hours}:${minutes}`;
        } catch {
          return '';
        }
      };

      setFormData({
        customer_id: ride.customer_id || '',
        driver_id: ride.driver_id || '',
        vehicle_vin: ride.vehicle_vin || '',
        pickup_location: ride.pickup_location || '',
        dropoff_location: ride.dropoff_location || '',
        start_time: formatForInput(ride.start_time),
        arrival_time: formatForInput(ride.arrival_time),
      });
    }
  }, [ride]);

  // Fetch all required data for dropdowns
  const loadAllData = async () => {
    try {
      setLoadingData(true);
      const [customersRes, driversRes, vehiclesRes, locationsRes] = await Promise.all([
        customerService.getAll(),
        driverService.getAll(),
        vehicleService.getAll(),
        locationService.getAll(),
      ]);
      
      setCustomers(customersRes.data || []);
      setDrivers(driversRes.data || []);
      setVehicles(vehiclesRes.data || []);
      setLocations(locationsRes.data || []);
    } catch (err) {
      setApiError(getErrorMessage(err));
    } finally {
      setLoadingData(false);
    }
  };

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: null,
      }));
    }
    // Clear API error when user makes changes
    if (apiError) {
      setApiError(null);
    }
  };

  // Validate form data
  const validateForm = () => {
    const newErrors = {};

    // Validate customer selection
    if (!formData.customer_id) {
      newErrors.customer_id = 'Please select a customer';
    }

    // Validate driver selection
    if (!formData.driver_id) {
      newErrors.driver_id = 'Please select a driver';
    }

    // Validate vehicle selection
    if (!formData.vehicle_vin) {
      newErrors.vehicle_vin = 'Please select a vehicle';
    }

    // Validate pickup location
    if (!formData.pickup_location) {
      newErrors.pickup_location = 'Please select a pickup location';
    }

    // Validate dropoff location
    if (!formData.dropoff_location) {
      newErrors.dropoff_location = 'Please select a dropoff location';
    } else if (formData.pickup_location === formData.dropoff_location) {
      newErrors.dropoff_location = 'Dropoff location must be different from pickup location';
    }

    // Validate start time
    if (!isRequired(formData.start_time)) {
      newErrors.start_time = 'Start time is required';
    }

    // Validate arrival time
    if (!isRequired(formData.arrival_time)) {
      newErrors.arrival_time = 'Arrival time is required';
    } else if (!isAfter(formData.start_time, formData.arrival_time)) {
      newErrors.arrival_time = 'Arrival time must be after start time';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError(null);

    // Validate form
    if (!validateForm()) {
      return;
    }

    try {
      setSubmitting(true);

      // Format datetime for backend (YYYY-MM-DDTHH:MM:SS format without milliseconds/timezone)
      const formatForBackend = (dateTimeStr) => {
        const date = new Date(dateTimeStr);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
      };

      const submitData = {
        ...formData,
        start_time: formatForBackend(formData.start_time),
        arrival_time: formatForBackend(formData.arrival_time),
      };

      if (isEditMode) {
        // Update existing ride
        await rideService.update(ride.ride_id, submitData);
        onSuccess('Ride updated successfully');
      } else {
        // Create new ride
        await rideService.create(submitData);
        onSuccess('Ride created successfully');
      }
    } catch (err) {
      setApiError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  if (loadingData) {
    return (
      <div className="ride-form-container">
        <h3>{isEditMode ? 'Edit Ride' : 'Add New Ride'}</h3>
        <p className="loading-text">Loading form data...</p>
      </div>
    );
  }

  return (
    <div className="ride-form-container">
      <h3>{isEditMode ? 'Edit Ride' : 'Add New Ride'}</h3>

      {apiError && <ErrorMessage message={apiError} onClose={() => setApiError(null)} />}

      <form onSubmit={handleSubmit} className="ride-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="customer_id">
              Customer <span className="required">*</span>
            </label>
            <select
              id="customer_id"
              name="customer_id"
              value={formData.customer_id}
              onChange={handleChange}
              className={errors.customer_id ? 'error' : ''}
              disabled={submitting}
            >
              <option value="">-- Select a customer --</option>
              {customers.map((customer) => (
                <option key={customer.customer_id} value={customer.customer_id}>
                  {customer.customer_name} (ID: {customer.customer_id})
                </option>
              ))}
            </select>
            {errors.customer_id && (
              <span className="error-text">{errors.customer_id}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="driver_id">
              Driver <span className="required">*</span>
            </label>
            <select
              id="driver_id"
              name="driver_id"
              value={formData.driver_id}
              onChange={handleChange}
              className={errors.driver_id ? 'error' : ''}
              disabled={submitting}
            >
              <option value="">-- Select a driver --</option>
              {drivers.map((driver) => (
                <option key={driver.driver_id} value={driver.driver_id}>
                  {driver.driver_name} (ID: {driver.driver_id})
                </option>
              ))}
            </select>
            {errors.driver_id && (
              <span className="error-text">{errors.driver_id}</span>
            )}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="vehicle_vin">
            Vehicle <span className="required">*</span>
          </label>
          <select
            id="vehicle_vin"
            name="vehicle_vin"
            value={formData.vehicle_vin}
            onChange={handleChange}
            className={errors.vehicle_vin ? 'error' : ''}
            disabled={submitting}
          >
            <option value="">-- Select a vehicle --</option>
            {vehicles.map((vehicle) => (
              <option key={vehicle.vehicle_vin} value={vehicle.vehicle_vin}>
                {vehicle.model} - {vehicle.color} (VIN: {vehicle.vehicle_vin})
              </option>
            ))}
          </select>
          {errors.vehicle_vin && (
            <span className="error-text">{errors.vehicle_vin}</span>
          )}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="pickup_location">
              Pickup Location <span className="required">*</span>
            </label>
            <select
              id="pickup_location"
              name="pickup_location"
              value={formData.pickup_location}
              onChange={handleChange}
              className={errors.pickup_location ? 'error' : ''}
              disabled={submitting}
            >
              <option value="">-- Select pickup location --</option>
              {locations.map((location) => (
                <option key={location.location_id} value={location.location_id}>
                  {location.address}, {location.city}
                </option>
              ))}
            </select>
            {errors.pickup_location && (
              <span className="error-text">{errors.pickup_location}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="dropoff_location">
              Dropoff Location <span className="required">*</span>
            </label>
            <select
              id="dropoff_location"
              name="dropoff_location"
              value={formData.dropoff_location}
              onChange={handleChange}
              className={errors.dropoff_location ? 'error' : ''}
              disabled={submitting}
            >
              <option value="">-- Select dropoff location --</option>
              {locations.map((location) => (
                <option key={location.location_id} value={location.location_id}>
                  {location.address}, {location.city}
                </option>
              ))}
            </select>
            {errors.dropoff_location && (
              <span className="error-text">{errors.dropoff_location}</span>
            )}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="start_time">
              Start Time <span className="required">*</span>
            </label>
            <input
              type="datetime-local"
              id="start_time"
              name="start_time"
              value={formData.start_time}
              onChange={handleChange}
              className={errors.start_time ? 'error' : ''}
              disabled={submitting}
            />
            {errors.start_time && (
              <span className="error-text">{errors.start_time}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="arrival_time">
              Arrival Time <span className="required">*</span>
            </label>
            <input
              type="datetime-local"
              id="arrival_time"
              name="arrival_time"
              value={formData.arrival_time}
              onChange={handleChange}
              className={errors.arrival_time ? 'error' : ''}
              disabled={submitting}
            />
            {errors.arrival_time && (
              <span className="error-text">{errors.arrival_time}</span>
            )}
          </div>
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting}
          >
            {submitting ? 'Saving...' : isEditMode ? 'Update Ride' : 'Create Ride'}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
            disabled={submitting}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export default RideForm;
