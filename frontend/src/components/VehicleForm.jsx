import { useState, useEffect } from 'react';
import { vehicleService, driverService } from '../services/api';
import ErrorMessage from './ErrorMessage';
import { isValidYear, isRequired, getErrorMessage } from '../utils/validation';
import './VehicleForm.css';

function VehicleForm({ vehicle, onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    vehicle_vin: '',
    model: '',
    color: '',
    registration_year: '',
    driver_id: '',
  });
  const [drivers, setDrivers] = useState([]);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState(null);
  const [loadingDrivers, setLoadingDrivers] = useState(true);

  const isEditMode = !!vehicle;

  // Load available drivers on component mount
  useEffect(() => {
    loadDrivers();
  }, []);

  // Populate form when editing
  useEffect(() => {
    if (vehicle) {
      setFormData({
        vehicle_vin: vehicle.vehicle_vin || '',
        model: vehicle.model || '',
        color: vehicle.color || '',
        registration_year: vehicle.registration_year || '',
        driver_id: vehicle.driver_id || '',
      });
    }
  }, [vehicle]);

  // Fetch all drivers for dropdown
  const loadDrivers = async () => {
    try {
      setLoadingDrivers(true);
      const response = await driverService.getAll();
      setDrivers(response.data || []);
    } catch (err) {
      setApiError(getErrorMessage(err));
    } finally {
      setLoadingDrivers(false);
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

    // Validate VIN
    if (!isRequired(formData.vehicle_vin)) {
      newErrors.vehicle_vin = 'VIN is required';
    } else if (formData.vehicle_vin.trim().length < 11 || formData.vehicle_vin.trim().length > 17) {
      newErrors.vehicle_vin = 'VIN must be between 11 and 17 characters';
    }

    // Validate model
    if (!isRequired(formData.model)) {
      newErrors.model = 'Model is required';
    } else if (formData.model.trim().length < 2) {
      newErrors.model = 'Model must be at least 2 characters';
    }

    // Validate color
    if (!isRequired(formData.color)) {
      newErrors.color = 'Color is required';
    }

    // Validate registration year
    if (!isRequired(formData.registration_year)) {
      newErrors.registration_year = 'Registration year is required';
    } else if (!isValidYear(formData.registration_year)) {
      const currentYear = new Date().getFullYear();
      newErrors.registration_year = `Please enter a valid year between 1900 and ${currentYear + 1}`;
    }

    // Validate driver selection
    if (!formData.driver_id) {
      newErrors.driver_id = 'Please select a driver';
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

      if (isEditMode) {
        // Update existing vehicle
        await vehicleService.update(vehicle.vehicle_vin, formData);
        onSuccess('Vehicle updated successfully');
      } else {
        // Create new vehicle
        await vehicleService.create(formData);
        onSuccess('Vehicle created successfully');
      }
    } catch (err) {
      setApiError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="vehicle-form-container">
      <h3>{isEditMode ? 'Edit Vehicle' : 'Add New Vehicle'}</h3>

      {apiError && <ErrorMessage message={apiError} onClose={() => setApiError(null)} />}

      <form onSubmit={handleSubmit} className="vehicle-form">
        <div className="form-group">
          <label htmlFor="vehicle_vin">
            VIN (Vehicle Identification Number) <span className="required">*</span>
          </label>
          <input
            type="text"
            id="vehicle_vin"
            name="vehicle_vin"
            value={formData.vehicle_vin}
            onChange={handleChange}
            className={errors.vehicle_vin ? 'error' : ''}
            disabled={submitting || isEditMode}
            placeholder="e.g., 1HGBH41JXMN109186"
          />
          {isEditMode && (
            <span className="field-note">VIN cannot be changed</span>
          )}
          {errors.vehicle_vin && (
            <span className="error-text">{errors.vehicle_vin}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="model">
            Model <span className="required">*</span>
          </label>
          <input
            type="text"
            id="model"
            name="model"
            value={formData.model}
            onChange={handleChange}
            className={errors.model ? 'error' : ''}
            disabled={submitting}
            placeholder="e.g., Toyota Camry"
          />
          {errors.model && (
            <span className="error-text">{errors.model}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="color">
            Color <span className="required">*</span>
          </label>
          <input
            type="text"
            id="color"
            name="color"
            value={formData.color}
            onChange={handleChange}
            className={errors.color ? 'error' : ''}
            disabled={submitting}
            placeholder="e.g., Black"
          />
          {errors.color && (
            <span className="error-text">{errors.color}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="registration_year">
            Registration Year <span className="required">*</span>
          </label>
          <input
            type="number"
            id="registration_year"
            name="registration_year"
            value={formData.registration_year}
            onChange={handleChange}
            className={errors.registration_year ? 'error' : ''}
            disabled={submitting}
            placeholder="e.g., 2020"
            min="1900"
            max={new Date().getFullYear() + 1}
          />
          {errors.registration_year && (
            <span className="error-text">{errors.registration_year}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="driver_id">
            Driver <span className="required">*</span>
          </label>
          {loadingDrivers ? (
            <p className="loading-text">Loading drivers...</p>
          ) : (
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
          )}
          {errors.driver_id && (
            <span className="error-text">{errors.driver_id}</span>
          )}
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting || loadingDrivers}
          >
            {submitting ? 'Saving...' : isEditMode ? 'Update Vehicle' : 'Create Vehicle'}
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

export default VehicleForm;
