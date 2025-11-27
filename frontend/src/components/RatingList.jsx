import { useState, useEffect } from 'react';
import { ratingService } from '../services/api';
import RatingForm from './RatingForm';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import SuccessMessage from './SuccessMessage';
import ConfirmDialog from './ConfirmDialog';
import { getErrorMessage } from '../utils/validation';
import './RatingList.css';

function RatingList() {
  const [ratings, setRatings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingRating, setEditingRating] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // Load ratings on component mount
  useEffect(() => {
    loadRatings();
  }, []);

  // Fetch all ratings from API
  const loadRatings = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await ratingService.getAll();
      setRatings(response.data || []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // Handle add rating button click
  const handleAdd = () => {
    setEditingRating(null);
    setShowForm(true);
    setError(null);
    setSuccess(null);
  };

  // Handle edit rating button click
  const handleEdit = (rating) => {
    setEditingRating(rating);
    setShowForm(true);
    setError(null);
    setSuccess(null);
  };

  // Handle delete rating button click
  const handleDelete = (rating) => {
    setDeleteConfirm(rating);
  };

  // Confirm delete operation
  const confirmDelete = async () => {
    if (!deleteConfirm) return;

    try {
      setError(null);
      await ratingService.delete(deleteConfirm.rating_id);
      setSuccess(`Rating #${deleteConfirm.rating_id} deleted successfully`);
      setDeleteConfirm(null);
      loadRatings();
    } catch (err) {
      setError(getErrorMessage(err));
      setDeleteConfirm(null);
    }
  };

  // Cancel delete operation
  const cancelDelete = () => {
    setDeleteConfirm(null);
  };

  // Handle form submission success
  const handleFormSuccess = (message) => {
    setSuccess(message);
    setShowForm(false);
    setEditingRating(null);
    loadRatings();
  };

  // Handle form cancel
  const handleFormCancel = () => {
    setShowForm(false);
    setEditingRating(null);
  };

  // Render star rating display
  const renderStars = (rating) => {
    if (rating === null || rating === undefined) return 'N/A';
    const stars = '★'.repeat(rating) + '☆'.repeat(5 - rating);
    return <span className="star-rating">{stars}</span>;
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="rating-list-container">
      <div className="rating-list-header">
        <h2>Rating Management</h2>
        {!showForm && (
          <button className="btn btn-primary" onClick={handleAdd}>
            Add Rating
          </button>
        )}
      </div>

      {error && <ErrorMessage message={error} onClose={() => setError(null)} />}
      {success && <SuccessMessage message={success} onClose={() => setSuccess(null)} />}

      {showForm ? (
        <RatingForm
          rating={editingRating}
          onSuccess={handleFormSuccess}
          onCancel={handleFormCancel}
        />
      ) : (
        <div className="rating-table-wrapper">
          {ratings.length === 0 ? (
            <p className="no-data">No ratings found. Click "Add Rating" to create one.</p>
          ) : (
            <table className="rating-table">
              <thead>
                <tr>
                  <th>Rating ID</th>
                  <th>Ride ID</th>
                  <th>Ride Details</th>
                  <th>Customer Rating</th>
                  <th>Driver Rating</th>
                  <th>Comments</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {ratings.map((rating) => (
                  <tr key={rating.rating_id}>
                    <td>{rating.rating_id}</td>
                    <td>{rating.ride_id}</td>
                    <td>
                      {rating.customer_name && rating.driver_name ? (
                        <div className="ride-details">
                          <div>{rating.customer_name} → {rating.driver_name}</div>
                          <div className="ride-locations">
                            {rating.pickup_address && rating.dropoff_address && (
                              <small>{rating.pickup_address} to {rating.dropoff_address}</small>
                            )}
                          </div>
                        </div>
                      ) : (
                        'N/A'
                      )}
                    </td>
                    <td className="rating-stars">
                      {renderStars(rating.customer_rating)}
                      <span className="rating-number">({rating.customer_rating || 'N/A'})</span>
                    </td>
                    <td className="rating-stars">
                      {renderStars(rating.driver_rating)}
                      <span className="rating-number">({rating.driver_rating || 'N/A'})</span>
                    </td>
                    <td className="comments">
                      {rating.comments ? (
                        <span title={rating.comments}>
                          {rating.comments.length > 50 
                            ? `${rating.comments.substring(0, 50)}...` 
                            : rating.comments}
                        </span>
                      ) : (
                        <span className="no-comments">No comments</span>
                      )}
                    </td>
                    <td className="actions">
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleEdit(rating)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(rating)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      <ConfirmDialog
        isOpen={!!deleteConfirm}
        title="Delete Rating"
        message={deleteConfirm ? `Are you sure you want to delete Rating #${deleteConfirm.rating_id}? This action cannot be undone.` : ''}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  );
}

export default RatingList;
