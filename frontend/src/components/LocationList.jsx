import { useState, useEffect } from 'react';
import { locationService } from '../services/api';
import LocationForm from './LocationForm';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import SuccessMessage from './SuccessMessage';
import ConfirmDialog from './ConfirmDialog';
import { getErrorMessage } from '../utils/validation';
import './LocationList.css';

function LocationList() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingLocation, setEditingLocation] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // Load locations on component mount
  useEffect(() => {
    loadLocations();
  }, []);

  // Fetch all locations from API
  const loadLocations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await locationService.getAll();
      setLocations(response.data || []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // Handle add location button click
  const handleAdd = () => {
    setEditingLocation(null);
    setShowForm(true);
    setError(null);
    setSuccess(null);
  };

  // Handle edit location button click
  const handleEdit = (location) => {
    setEditingLocation(location);
    setShowForm(true);
    setError(null);
    setSuccess(null);
  };

  // Handle delete location button click
  const handleDelete = (location) => {
    setDeleteConfirm(location);
  };

  // Confirm delete operation
  const confirmDelete = async () => {
    if (!deleteConfirm) return;

    try {
      setError(null);
      await locationService.delete(deleteConfirm.location_id);
      setSuccess(`Location "${deleteConfirm.address}" deleted successfully`);
      setDeleteConfirm(null);
      loadLocations();
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
    setEditingLocation(null);
    loadLocations();
  };

  // Handle form cancel
  const handleFormCancel = () => {
    setShowForm(false);
    setEditingLocation(null);
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="location-list-container">
      <div className="location-list-header">
        <h2>Location Management</h2>
        {!showForm && (
          <button className="btn btn-primary" onClick={handleAdd}>
            Add Location
          </button>
        )}
      </div>

      {error && <ErrorMessage message={error} onClose={() => setError(null)} />}
      {success && <SuccessMessage message={success} onClose={() => setSuccess(null)} />}

      {showForm ? (
        <LocationForm
          location={editingLocation}
          onSuccess={handleFormSuccess}
          onCancel={handleFormCancel}
        />
      ) : (
        <div className="location-table-wrapper">
          {locations.length === 0 ? (
            <p className="no-data">No locations found. Click "Add Location" to create one.</p>
          ) : (
            <table className="location-table">
              <thead>
                <tr>
                  <th>Location ID</th>
                  <th>Address</th>
                  <th>City</th>
                  <th>Postal Code</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {locations.map((location) => (
                  <tr key={location.location_id}>
                    <td>{location.location_id}</td>
                    <td>{location.address}</td>
                    <td>{location.city}</td>
                    <td>{location.postal_code}</td>
                    <td className="actions">
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleEdit(location)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(location)}
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
        title="Delete Location"
        message={deleteConfirm ? `Are you sure you want to delete location "${deleteConfirm.address}"? This action cannot be undone.` : ''}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  );
}

export default LocationList;
