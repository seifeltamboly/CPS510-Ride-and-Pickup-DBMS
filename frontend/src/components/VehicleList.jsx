import { useState, useEffect } from 'react';
import { vehicleService } from '../services/api';
import VehicleForm from './VehicleForm';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import SuccessMessage from './SuccessMessage';
import ConfirmDialog from './ConfirmDialog';
import { getErrorMessage } from '../utils/validation';
import './VehicleList.css';

function VehicleList() {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // Load vehicles on component mount
  useEffect(() => {
    loadVehicles();
  }, []);

  // Fetch all vehicles from API
  const loadVehicles = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await vehicleService.getAll();
      setVehicles(response.data || []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // Handle add vehicle button click
  const handleAdd = () => {
    setEditingVehicle(null);
    setShowForm(true);
    setError(null);
    setSuccess(null);
  };

  // Handle edit vehicle button click
  const handleEdit = (vehicle) => {
    setEditingVehicle(vehicle);
    setShowForm(true);
    setError(null);
    setSuccess(null);
  };

  // Handle delete vehicle button click
  const handleDelete = (vehicle) => {
    setDeleteConfirm(vehicle);
  };

  // Confirm delete operation
  const confirmDelete = async () => {
    if (!deleteConfirm) return;

    try {
      setError(null);
      await vehicleService.delete(deleteConfirm.vehicle_vin);
      setSuccess(`Vehicle "${deleteConfirm.model}" (VIN: ${deleteConfirm.vehicle_vin}) deleted successfully`);
      setDeleteConfirm(null);
      loadVehicles();
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
    setEditingVehicle(null);
    loadVehicles();
  };

  // Handle form cancel
  const handleFormCancel = () => {
    setShowForm(false);
    setEditingVehicle(null);
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="vehicle-list-container">
      <div className="vehicle-list-header">
        <h2>Vehicle Management</h2>
        {!showForm && (
          <button className="btn btn-primary" onClick={handleAdd}>
            Add Vehicle
          </button>
        )}
      </div>

      {error && <ErrorMessage message={error} onClose={() => setError(null)} />}
      {success && <SuccessMessage message={success} onClose={() => setSuccess(null)} />}

      {showForm ? (
        <VehicleForm
          vehicle={editingVehicle}
          onSuccess={handleFormSuccess}
          onCancel={handleFormCancel}
        />
      ) : (
        <div className="vehicle-table-wrapper">
          {vehicles.length === 0 ? (
            <p className="no-data">No vehicles found. Click "Add Vehicle" to create one.</p>
          ) : (
            <table className="vehicle-table">
              <thead>
                <tr>
                  <th>VIN</th>
                  <th>Model</th>
                  <th>Color</th>
                  <th>Registration Year</th>
                  <th>Driver</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {vehicles.map((vehicle) => (
                  <tr key={vehicle.vehicle_vin}>
                    <td>{vehicle.vehicle_vin}</td>
                    <td>{vehicle.model}</td>
                    <td>{vehicle.color}</td>
                    <td>{vehicle.registration_year}</td>
                    <td>{vehicle.driver_name || 'N/A'}</td>
                    <td className="actions">
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleEdit(vehicle)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(vehicle)}
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
        title="Delete Vehicle"
        message={deleteConfirm ? `Are you sure you want to delete vehicle "${deleteConfirm.model}" (VIN: ${deleteConfirm.vehicle_vin})? This action cannot be undone.` : ''}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  );
}

export default VehicleList;
