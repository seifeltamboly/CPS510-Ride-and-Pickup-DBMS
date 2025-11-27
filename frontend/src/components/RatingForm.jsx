import { useState, useEffect } from 'react';
import { ratingService, rideService } from '../services/api';
import ErrorMessage from './ErrorMessage';
import { isRequired, isValidRating, getErrorMessage } from '../utils/validation';
import './RatingForm.css';

function RatingForm({ rating, onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    ride_id: '',
    customer_rating: '',
    driver_rating: '',
    comments: '',
  });
  
  // State for dropdown options
  const [rides, setRides] = useState([]);
  
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState(null);
  const [loadingData, setLoadingData] = useState(true);

  const isEditMode = !!rating;

  // Load all required data on component mount
  useEffect(() => {
    loadAllData();
  }, []);

  // Populate form when editing
  useEffect(() => {
    if (rating) {
      setFormData({
        ride_id: rating.ride_id || '',
        customer_rating: rating.customer_rating || '',
        driver_rating: rating.driver_rating || '',
        comments: rating.comments || '',
      });
    }
  }, [rating]);

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

    // Validate customer rating
    if (!isRequired(formData.customer_rating)) {
      newErrors.customer_rating = 'Customer rating is required';
    } else if (!isValidRating(formData.customer_rating)) {
      newErrors.customer_rating = 'Customer rating must be between 1 and 5';
    }

    // Validate driver rating
    if (!isRequired(formData.driver_rating)) {
      newErrors.driver_rating = 'Driver rating is required';
    } else if (!isValidRating(formData.driver_rating)) {
      newErrors.driver_rating = 'Driver rating must be between 1 and 5';
    }

    // Comments are optional, no validation needed

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

      const submitData = {
        ride_id: parseInt(formData.ride_id),
        customer_rating: parseInt(formData.customer_rating),
        driver_rating: parseInt(formData.driver_rating),
        comments: formData.comments || null,
      };

      if (isEditMode) {
        // Update existing rating
        await ratingService.update(rating.rating_id, submitData);
        onSuccess('Rating updated successfully');
      } else {
        // Create new rating
        await ratingService.create(submitData);
        onSuccess('Rating created successfully');
      }
    } catch (err) {
      setApiError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  // Render star rating selector
  const renderStarSelector = (name, value) => {
    return (
      <div className="star-selector">
        {[1, 2, 3, 4, 5].map((star) => (
          <label key={star} className="star-label">
            <input
              type="radio"
              name={name}
              value={star}
              checked={parseInt(value) === star}
              onChange={handleChange}
              disabled={submitting}
            />
            <span className={`star ${parseInt(value) >= star ? 'filled' : ''}`}>★</span>
          </label>
        ))}
      </div>
    );
  };

  if (loadingData) {
    return (
      <div className="rating-form-container">
        <h3>{isEditMode ? 'Edit Rating' : 'Add New Rating'}</h3>
        <p className="loading-text">Loading form data...</p>
      </div>
    );
  }

  return (
    <div className="rating-form-container">
      <h3>{isEditMode ? 'Edit Rating' : 'Add New Rating'}</h3>

      {apiError && <ErrorMessage message={apiError} onClose={() => setApiError(null)} />}

      <form onSubmit={handleSubmit} className="rating-form">
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
            <label htmlFor="customer_rating">
              Customer Rating <span className="required">*</span>
            </label>
            {renderStarSelector('customer_rating', formData.customer_rating)}
            <input
              type="number"
              id="customer_rating"
              name="customer_rating"
              value={formData.customer_rating}
              onChange={handleChange}
              className={`rating-input ${errors.customer_rating ? 'error' : ''}`}
              disabled={submitting}
              placeholder="1-5"
              min="1"
              max="5"
            />
            {errors.customer_rating && (
              <span className="error-text">{errors.customer_rating}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="driver_rating">
              Driver Rating <span className="required">*</span>
            </label>
            {renderStarSelector('driver_rating', formData.driver_rating)}
            <input
              type="number"
              id="driver_rating"
              name="driver_rating"
              value={formData.driver_rating}
              onChange={handleChange}
              className={`rating-input ${errors.driver_rating ? 'error' : ''}`}
              disabled={submitting}
              placeholder="1-5"
              min="1"
              max="5"
            />
            {errors.driver_rating && (
              <span className="error-text">{errors.driver_rating}</span>
            )}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="comments">
            Comments
          </label>
          <textarea
            id="comments"
            name="comments"
            value={formData.comments}
            onChange={handleChange}
            className={errors.comments ? 'error' : ''}
            disabled={submitting}
            placeholder="Enter any additional comments about the ride..."
            rows="4"
          />
          {errors.comments && (
            <span className="error-text">{errors.comments}</span>
          )}
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting}
          >
            {submitting ? 'Saving...' : isEditMode ? 'Update Rating' : 'Create Rating'}
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

export default RatingForm;
