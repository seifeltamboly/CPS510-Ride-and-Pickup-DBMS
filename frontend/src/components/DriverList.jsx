import { useState, useEffect } from 'react';
import { driverService } from '../services/api';
import DriverForm from './DriverForm';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import SuccessMessage from './SuccessMessage';
import ConfirmDialog from './ConfirmDialog';
import { getErrorMessage } from '../utils/validation';
import './DriverList.css';

function DriverList() {
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingDriver, setEditingDriver] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // Load drivers on component mount
  useEffect(() => {
    loadDrivers();
  }, []);

  // Fetch all drivers from API
  const loadDrivers = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await driverService.getAll();
      setDrivers(response.data || []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // Handle add driver button click
  const handleAdd = () => {
    setEditingDriver(null);
    setShowForm(true);
    setError(null);
    setSuccess(null);
  };

  // Handle edit driver button click
  const handleEdit = (driver) => {
    setEditingDriver(driver);
    setShowForm(true);
    setError(null);
    setSuccess(null);
  };

  // Handle delete driver button click
  const handleDelete = (driver) => {
    setDeleteConfirm(driver);
  };

  // Confirm delete operation
  const confirmDelete = async () => {
    if (!deleteConfirm) return;

    try {
      setError(null);
      await driverService.delete(deleteConfirm.driver_id);
      setSuccess(`Driver "${deleteConfirm.driver_name}" deleted successfully`);
      setDeleteConfirm(null);
      loadDrivers();
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
    setEditingDriver(null);
    loadDrivers();
  };

  // Handle form cancel
  const handleFormCancel = () => {
    setShowForm(false);
    setEditingDriver(null);
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="driver-list-container">
      <div className="driver-list-header">
        <h2>Driver Management</h2>
        {!showForm && (
          <button className="btn btn-primary" onClick={handleAdd}>
            Add Driver
          </button>
        )}
      </div>

      {error && <ErrorMessage message={error} onClose={() => setError(null)} />}
      {success && <SuccessMessage message={success} onClose={() => setSuccess(null)} />}

      {showForm ? (
        <DriverForm
          driver={editingDriver}
          onSuccess={handleFormSuccess}
          onCancel={handleFormCancel}
        />
      ) : (
        <div className="driver-table-wrapper">
          {drivers.length === 0 ? (
            <p className="no-data">No drivers found. Click "Add Driver" to create one.</p>
          ) : (
            <table className="driver-table">
              <thead>
                <tr>
                  <th>Driver ID</th>
                  <th>Name</th>
                  <th>Phone Number</th>
                  <th>License Number</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {drivers.map((driver) => (
                  <tr key={driver.driver_id}>
                    <td>{driver.driver_id}</td>
                    <td>{driver.driver_name}</td>
                    <td>{driver.phone_number}</td>
                    <td>{driver.license_number}</td>
                    <td className="actions">
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleEdit(driver)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(driver)}
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
        title="Delete Driver"
        message={deleteConfirm ? `Are you sure you want to delete driver "${deleteConfirm.driver_name}"? This action cannot be undone.` : ''}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  );
}

export default DriverList;
