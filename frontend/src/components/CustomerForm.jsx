import { useState, useEffect } from 'react';
import { customerService } from '../services/api';
import ErrorMessage from './ErrorMessage';
import { isValidEmail, isValidPhoneNumber, isRequired, getErrorMessage } from '../utils/validation';
import './CustomerForm.css';

function CustomerForm({ customer, onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    customer_name: '',
    phone_number: '',
    email: '',
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState(null);

  const isEditMode = !!customer;

  // Populate form when editing
  useEffect(() => {
    if (customer) {
      setFormData({
        customer_name: customer.customer_name || '',
        phone_number: customer.phone_number || '',
        email: customer.email || '',
      });
    }
  }, [customer]);

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

    // Validate customer name
    if (!isRequired(formData.customer_name)) {
      newErrors.customer_name = 'Customer name is required';
    } else if (formData.customer_name.trim().length < 2) {
      newErrors.customer_name = 'Customer name must be at least 2 characters';
    }

    // Validate phone number
    if (!isRequired(formData.phone_number)) {
      newErrors.phone_number = 'Phone number is required';
    } else if (!isValidPhoneNumber(formData.phone_number)) {
      newErrors.phone_number = 'Please enter a valid phone number (e.g., 123-456-7890)';
    }

    // Validate email
    if (!isRequired(formData.email)) {
      newErrors.email = 'Email is required';
    } else if (!isValidEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email address (e.g., user@example.com)';
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
        // Update existing customer
        await customerService.update(customer.customer_id, formData);
        onSuccess('Customer updated successfully');
      } else {
        // Create new customer
        await customerService.create(formData);
        onSuccess('Customer created successfully');
      }
    } catch (err) {
      setApiError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="customer-form-container">
      <h3>{isEditMode ? 'Edit Customer' : 'Add New Customer'}</h3>

      {apiError && <ErrorMessage message={apiError} onClose={() => setApiError(null)} />}

      <form onSubmit={handleSubmit} className="customer-form">
        <div className="form-group">
          <label htmlFor="customer_name">
            Customer Name <span className="required">*</span>
          </label>
          <input
            type="text"
            id="customer_name"
            name="customer_name"
            value={formData.customer_name}
            onChange={handleChange}
            className={errors.customer_name ? 'error' : ''}
            disabled={submitting}
          />
          {errors.customer_name && (
            <span className="error-text">{errors.customer_name}</span>
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
          <label htmlFor="email">
            Email <span className="required">*</span>
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className={errors.email ? 'error' : ''}
            disabled={submitting}
            placeholder="e.g., customer@example.com"
          />
          {errors.email && <span className="error-text">{errors.email}</span>}
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting}
          >
            {submitting ? 'Saving...' : isEditMode ? 'Update Customer' : 'Create Customer'}
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

export default CustomerForm;
