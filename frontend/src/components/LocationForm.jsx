import { useState, useEffect } from 'react';
import { locationService } from '../services/api';
import ErrorMessage from './ErrorMessage';
import { isRequired, getErrorMessage } from '../utils/validation';
import './LocationForm.css';

function LocationForm({ location, onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    address: '',
    city: '',
    postal_code: '',
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState(null);

  const isEditMode = !!location;

  // Populate form when editing
  useEffect(() => {
    if (location) {
      setFormData({
        address: location.address || '',
        city: location.city || '',
        postal_code: location.postal_code || '',
      });
    }
  }, [location]);

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

    // Validate address
    if (!isRequired(formData.address)) {
      newErrors.address = 'Address is required';
    } else if (formData.address.trim().length < 5) {
      newErrors.address = 'Address must be at least 5 characters';
    }

    // Validate city
    if (!isRequired(formData.city)) {
      newErrors.city = 'City is required';
    } else if (formData.city.trim().length < 2) {
      newErrors.city = 'City must be at least 2 characters';
    }

    // Validate postal code
    if (!isRequired(formData.postal_code)) {
      newErrors.postal_code = 'Postal code is required';
    } else if (formData.postal_code.trim().length < 3) {
      newErrors.postal_code = 'Postal code must be at least 3 characters';
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
        // Update existing location
        await locationService.update(location.location_id, formData);
        onSuccess('Location updated successfully');
      } else {
        // Create new location
        await locationService.create(formData);
        onSuccess('Location created successfully');
      }
    } catch (err) {
      setApiError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="location-form-container">
      <h3>{isEditMode ? 'Edit Location' : 'Add New Location'}</h3>

      {apiError && <ErrorMessage message={apiError} onClose={() => setApiError(null)} />}

      <form onSubmit={handleSubmit} className="location-form">
        <div className="form-group">
          <label htmlFor="address">
            Address <span className="required">*</span>
          </label>
          <input
            type="text"
            id="address"
            name="address"
            value={formData.address}
            onChange={handleChange}
            className={errors.address ? 'error' : ''}
            disabled={submitting}
            placeholder="e.g., 123 Main Street"
          />
          {errors.address && (
            <span className="error-text">{errors.address}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="city">
            City <span className="required">*</span>
          </label>
          <input
            type="text"
            id="city"
            name="city"
            value={formData.city}
            onChange={handleChange}
            className={errors.city ? 'error' : ''}
            disabled={submitting}
            placeholder="e.g., New York"
          />
          {errors.city && (
            <span className="error-text">{errors.city}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="postal_code">
            Postal Code <span className="required">*</span>
          </label>
          <input
            type="text"
            id="postal_code"
            name="postal_code"
            value={formData.postal_code}
            onChange={handleChange}
            className={errors.postal_code ? 'error' : ''}
            disabled={submitting}
            placeholder="e.g., 10001"
          />
          {errors.postal_code && (
            <span className="error-text">{errors.postal_code}</span>
          )}
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting}
          >
            {submitting ? 'Saving...' : isEditMode ? 'Update Location' : 'Create Location'}
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

export default LocationForm;
