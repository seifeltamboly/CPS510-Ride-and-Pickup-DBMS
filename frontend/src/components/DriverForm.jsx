import { useState, useEffect } from 'react';
import { driverService } from '../services/api';
import ErrorMessage from './ErrorMessage';
import { isValidPhoneNumber, isRequired, getErrorMessage } from '../utils/validation';
import './DriverForm.css';

function DriverForm({ driver, onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    driver_name: '',
    phone_number: '',
    license_number: '',
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState(null);

  const isEditMode = !!driver;

  // Populate form when editing
  useEffect(() => {
    if (driver) {
      setFormData({
        driver_name: driver.driver_name || '',
        phone_number: driver.phone_number || '',
        license_number: driver.license_number || '',
      });
    }
  }, [driver]);

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

    // Validate driver name
    if (!isRequired(formData.driver_name)) {
      newErrors.driver_name = 'Driver name is required';
    } else if (formData.driver_name.trim().length < 2) {
      newErrors.driver_name = 'Driver name must be at least 2 characters';
    }

    // Validate phone number
    if (!isRequired(formData.phone_number)) {
      newErrors.phone_number = 'Phone number is required';
    } else if (!isValidPhoneNumber(formData.phone_number)) {
      newErrors.phone_number = 'Please enter a valid phone number (e.g., 123-456-7890)';
    }

    // Validate license number
    if (!isRequired(formData.license_number)) {
      newErrors.license_number = 'License number is required';
    } else if (formData.license_number.trim().length < 5) {
      newErrors.license_number = 'License number must be at least 5 characters';
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
        // Update existing driver
        await driverService.update(driver.driver_id, formData);
        onSuccess('Driver updated successfully');
      } else {
        // Create new driver
        await driverService.create(formData);
        onSuccess('Driver created successfully');
      }
    } catch (err) {
      setApiError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="driver-form-container">
      <h3>{isEditMode ? 'Edit Driver' : 'Add New Driver'}</h3>

      {apiError && <ErrorMessage message={apiError} onClose={() => setApiError(null)} />}

      <form onSubmit={handleSubmit} className="driver-form">
        <div className="form-group">
          <label htmlFor="driver_name">
            Driver Name <span className="required">*</span>
          </label>
          <input
            type="text"
            id="driver_name"
            name="driver_name"
            value={formData.driver_name}
            onChange={handleChange}
            className={errors.driver_name ? 'error' : ''}
            disabled={submitting}
          />
          {errors.driver_name && (
            <span className="error-text">{errors.driver_name}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="phone_number">
            Phone Number <span className="required">*</span>
          </label>
          <input
            type="text"
            id="phone_number"
            name="phone_number"
            value={formData.phone_number}
            onChange={handleChange}
            className={errors.phone_number ? 'error' : ''}
            disabled={submitting}
            placeholder="e.g., 123-456-7890"
          />
          {errors.phone_number && (
            <span className="error-text">{errors.phone_number}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="license_number">
            License Number <span className="required">*</span>
          </label>
          <input
            type="text"
            id="license_number"
            name="license_number"
            value={formData.license_number}
            onChange={handleChange}
            className={errors.license_number ? 'error' : ''}
            disabled={submitting}
            placeholder="e.g., DL123456"
          />
          {errors.license_number && (
            <span className="error-text">{errors.license_number}</span>
          )}
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting}
          >
            {submitting ? 'Saving...' : isEditMode ? 'Update Driver' : 'Create Driver'}
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

export default DriverForm;
