import { useState, useEffect } from 'react';
import { paymentService, rideService } from '../services/api';
import ErrorMessage from './ErrorMessage';
import { isRequired, isValidPositiveNumber, hasValidDecimals, getErrorMessage } from '../utils/validation';
import './PaymentForm.css';

function PaymentForm({ payment, onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    ride_id: '',
    amount: '',
    payment_method: '',
    payment_status: '',
    payment_date: '',
  });
  
  // State for dropdown options
  const [rides, setRides] = useState([]);
  
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState(null);
  const [loadingData, setLoadingData] = useState(true);

  const isEditMode = !!payment;

  // Payment method options
  const paymentMethods = ['Credit Card', 'Debit Card', 'Cash', 'Digital Wallet', 'Bank Transfer'];
  
  // Payment status options
  const paymentStatuses = ['Pending', 'Completed', 'Failed', 'Refunded'];

  // Load all required data on component mount
  useEffect(() => {
    loadAllData();
  }, []);

  // Populate form when editing
  useEffect(() => {
    if (payment) {
      // Format date for input field (expects YYYY-MM-DD format)
      const formatForInput = (dateStr) => {
        if (!dateStr) return '';
        try {
          const date = new Date(dateStr);
          const year = date.getFullYear();
          const month = String(date.getMonth() + 1).padStart(2, '0');
          const day = String(date.getDate()).padStart(2, '0');
          return `${year}-${month}-${day}`;
        } catch {
          return '';
        }
      };

      setFormData({
        ride_id: payment.ride_id || '',
        amount: payment.amount || '',
        payment_method: payment.payment_method || '',
        payment_status: payment.payment_status || '',
        payment_date: formatForInput(payment.payment_date),
      });
    }
  }, [payment]);

  // Fetch all required data for dropdowns
  const loadAllData = async () => {
    try {
      setLoadingData(true);
      const ridesRes = await rideService.getAll();
      setRides(ridesRes.data || []);
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

    // Validate ride selection
    if (!formData.ride_id) {
      newErrors.ride_id = 'Please select a ride';
    }

    // Validate amount
    if (!isRequired(formData.amount)) {
      newErrors.amount = 'Amount is required';
    } else if (!isValidPositiveNumber(formData.amount)) {
      newErrors.amount = 'Amount must be a positive number';
    } else if (!hasValidDecimals(formData.amount, 2)) {
      newErrors.amount = 'Amount must have at most 2 decimal places';
    } else if (parseFloat(formData.amount) > 999999.99) {
      newErrors.amount = 'Amount cannot exceed $999,999.99';
    }

    // Validate payment method
    if (!formData.payment_method) {
      newErrors.payment_method = 'Please select a payment method';
    }

    // Validate payment status
    if (!formData.payment_status) {
      newErrors.payment_status = 'Please select a payment status';
    }

    // Validate payment date
    if (!isRequired(formData.payment_date)) {
      newErrors.payment_date = 'Payment date is required';
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

      // Format date for backend (YYYY-MM-DD format)
      const formatForBackend = (dateStr) => {
        const date = new Date(dateStr);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      };

      const submitData = {
        ...formData,
        amount: parseFloat(formData.amount),
        payment_date: formatForBackend(formData.payment_date),
      };

      if (isEditMode) {
        // Update existing payment
        await paymentService.update(payment.transaction_id, submitData);
        onSuccess('Payment updated successfully');
      } else {
        // Create new payment
        await paymentService.create(submitData);
        onSuccess('Payment created successfully');
      }
    } catch (err) {
      setApiError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  if (loadingData) {
    return (
      <div className="payment-form-container">
        <h3>{isEditMode ? 'Edit Payment' : 'Add New Payment'}</h3>
        <p className="loading-text">Loading form data...</p>
      </div>
    );
  }

  return (
    <div className="payment-form-container">
      <h3>{isEditMode ? 'Edit Payment' : 'Add New Payment'}</h3>

      {apiError && <ErrorMessage message={apiError} onClose={() => setApiError(null)} />}

      <form onSubmit={handleSubmit} className="payment-form">
        <div className="form-group">
          <label htmlFor="ride_id">
            Ride <span className="required">*</span>
          </label>
          <select
            id="ride_id"
            name="ride_id"
            value={formData.ride_id}
            onChange={handleChange}
            className={errors.ride_id ? 'error' : ''}
            disabled={submitting}
          >
            <option value="">-- Select a ride --</option>
            {rides.map((ride) => (
              <option key={ride.ride_id} value={ride.ride_id}>
                Ride #{ride.ride_id} - {ride.customer_name || `Customer ${ride.customer_id}`} with {ride.driver_name || `Driver ${ride.driver_id}`}
                {ride.start_time && ` (${new Date(ride.start_time).toLocaleDateString()})`}
              </option>
            ))}
          </select>
          {errors.ride_id && (
            <span className="error-text">{errors.ride_id}</span>
          )}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="amount">
              Amount <span className="required">*</span>
            </label>
            <input
              type="number"
              id="amount"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              className={errors.amount ? 'error' : ''}
              disabled={submitting}
              placeholder="0.00"
              step="0.01"
              min="0"
            />
            {errors.amount && (
              <span className="error-text">{errors.amount}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="payment_date">
              Payment Date <span className="required">*</span>
            </label>
            <input
              type="date"
              id="payment_date"
              name="payment_date"
              value={formData.payment_date}
              onChange={handleChange}
              className={errors.payment_date ? 'error' : ''}
              disabled={submitting}
            />
            {errors.payment_date && (
              <span className="error-text">{errors.payment_date}</span>
            )}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="payment_method">
              Payment Method <span className="required">*</span>
            </label>
            <select
              id="payment_method"
              name="payment_method"
              value={formData.payment_method}
              onChange={handleChange}
              className={errors.payment_method ? 'error' : ''}
              disabled={submitting}
            >
              <option value="">-- Select payment method --</option>
              {paymentMethods.map((method) => (
                <option key={method} value={method}>
                  {method}
                </option>
              ))}
            </select>
            {errors.payment_method && (
              <span className="error-text">{errors.payment_method}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="payment_status">
              Payment Status <span className="required">*</span>
            </label>
            <select
              id="payment_status"
              name="payment_status"
              value={formData.payment_status}
              onChange={handleChange}
              className={errors.payment_status ? 'error' : ''}
              disabled={submitting}
            >
              <option value="">-- Select payment status --</option>
              {paymentStatuses.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
            {errors.payment_status && (
              <span className="error-text">{errors.payment_status}</span>
            )}
          </div>
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting}
          >
            {submitting ? 'Saving...' : isEditMode ? 'Update Payment' : 'Create Payment'}
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

export default PaymentForm;
