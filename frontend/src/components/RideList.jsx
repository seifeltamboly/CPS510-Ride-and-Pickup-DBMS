import { useState, useEffect } from 'react';
import { rideService } from '../services/api';
import RideForm from './RideForm';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import SuccessMessage from './SuccessMessage';
import ConfirmDialog from './ConfirmDialog';
import { getErrorMessage } from '../utils/validation';
import './RideList.css';

function RideList() {
  const [rides, setRides] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingRide, setEditingRide] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // Load rides on component mount
  useEffect(() => {
    loadRides();
  }, []);

  // Fetch all rides from API
  const loadRides = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await rideService.getAll();
      setRides(response.data || []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // Handle add ride button click
  const handleAdd = () => {
    setEditingRide(null);
    setShowForm(true);
    setError(null);
    setSuccess(null);
  };

  // Handle edit ride button click
  const handleEdit = (ride) => {
    setEditingRide(ride);
    setShowForm(true);
    setError(null);
    setSuccess(null);
  };

  // Handle delete ride button click
  const handleDelete = (ride) => {
    setDeleteConfirm(ride);
  };

  // Confirm delete operation
  const confirmDelete = async () => {
    if (!deleteConfirm) return;

    try {
      setError(null);
      await rideService.delete(deleteConfirm.ride_id);
      setSuccess(`Ride #${deleteConfirm.ride_id} deleted successfully`);
      setDeleteConfirm(null);
      loadRides();
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
    setEditingRide(null);
    loadRides();
  };

  // Handle form cancel
  const handleFormCancel = () => {
    setShowForm(false);
    setEditingRide(null);
  };

  // Format datetime for display
  const formatDateTime = (dateTimeStr) => {
    if (!dateTimeStr) return 'N/A';
    try {
      const date = new Date(dateTimeStr);
      return date.toLocaleString();
    } catch {
      return dateTimeStr;
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="ride-list-container">
      <div className="ride-list-header">
        <h2>Ride Management</h2>
        {!showForm && (
          <button className="btn btn-primary" onClick={handleAdd}>
            Add Ride
          </button>
        )}
      </div>

      {error && <ErrorMessage message={error} onClose={() => setError(null)} />}
      {success && <SuccessMessage message={success} onClose={() => setSuccess(null)} />}

      {showForm ? (
        <RideForm
          ride={editingRide}
          onSuccess={handleFormSuccess}
          onCancel={handleFormCancel}
        />
      ) : (
        <div className="ride-table-wrapper">
          {rides.length === 0 ? (
            <p className="no-data">No rides found. Click "Add Ride" to create one.</p>
          ) : (
            <table className="ride-table">
              <thead>
                <tr>
                  <th>Ride ID</th>
                  <th>Customer</th>
                  <th>Driver</th>
                  <th>Vehicle</th>
                  <th>Pickup Location</th>
                  <th>Dropoff Location</th>
                  <th>Start Time</th>
                  <th>Arrival Time</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {rides.map((ride) => (
                  <tr key={ride.ride_id}>
                    <td>{ride.ride_id}</td>
                    <td>{ride.customer_name || `ID: ${ride.customer_id}`}</td>
                    <td>{ride.driver_name || `ID: ${ride.driver_id}`}</td>
                    <td>{ride.vehicle_model || ride.vehicle_vin}</td>
                    <td>{ride.pickup_address || `ID: ${ride.pickup_location_id}`}</td>
                    <td>{ride.dropoff_address || `ID: ${ride.dropoff_location_id}`}</td>
                    <td>{formatDateTime(ride.start_time)}</td>
                    <td>{formatDateTime(ride.arrival_time)}</td>
                    <td className="actions">
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleEdit(ride)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(ride)}
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
        title="Delete Ride"
        message={deleteConfirm ? `Are you sure you want to delete Ride #${deleteConfirm.ride_id}? This action cannot be undone.` : ''}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  );
}

export default RideList;
