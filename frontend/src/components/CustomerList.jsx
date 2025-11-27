import { useState, useEffect } from 'react';
import { customerService } from '../services/api';
import CustomerForm from './CustomerForm';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import SuccessMessage from './SuccessMessage';
import ConfirmDialog from './ConfirmDialog';
import { getErrorMessage } from '../utils/validation';
import './CustomerList.css';

function CustomerList() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // Load customers on component mount
  useEffect(() => {
    loadCustomers();
  }, []);

  // Fetch all customers from API
  const loadCustomers = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await customerService.getAll();
      setCustomers(response.data || []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // Handle add customer button click
  const handleAdd = () => {
    setEditingCustomer(null);
    setShowForm(true);
    setError(null);
    setSuccess(null);
  };

  // Handle edit customer button click
  const handleEdit = (customer) => {
    setEditingCustomer(customer);
    setShowForm(true);
    setError(null);
    setSuccess(null);
  };

  // Handle delete customer button click
  const handleDelete = (customer) => {
    setDeleteConfirm(customer);
  };

  // Confirm delete operation
  const confirmDelete = async () => {
    if (!deleteConfirm) return;

    try {
      setError(null);
      await customerService.delete(deleteConfirm.customer_id);
      setSuccess(`Customer "${deleteConfirm.customer_name}" deleted successfully`);
      setDeleteConfirm(null);
      loadCustomers();
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
    setEditingCustomer(null);
    loadCustomers();
  };

  // Handle form cancel
  const handleFormCancel = () => {
    setShowForm(false);
    setEditingCustomer(null);
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="customer-list-container">
      <div className="customer-list-header">
        <h2>Customer Management</h2>
        {!showForm && (
          <button className="btn btn-primary" onClick={handleAdd}>
            Add Customer
          </button>
        )}
      </div>

      {error && <ErrorMessage message={error} onClose={() => setError(null)} />}
      {success && <SuccessMessage message={success} onClose={() => setSuccess(null)} />}

      {showForm ? (
        <CustomerForm
          customer={editingCustomer}
          onSuccess={handleFormSuccess}
          onCancel={handleFormCancel}
        />
      ) : (
        <div className="customer-table-wrapper">
          {customers.length === 0 ? (
            <p className="no-data">No customers found. Click "Add Customer" to create one.</p>
          ) : (
            <table className="customer-table">
              <thead>
                <tr>
                  <th>Customer ID</th>
                  <th>Name</th>
                  <th>Phone Number</th>
                  <th>Email</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((customer) => (
                  <tr key={customer.customer_id}>
                    <td>{customer.customer_id}</td>
                    <td>{customer.customer_name}</td>
                    <td>{customer.phone_number}</td>
                    <td>{customer.email}</td>
                    <td className="actions">
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleEdit(customer)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(customer)}
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
        title="Delete Customer"
        message={deleteConfirm ? `Are you sure you want to delete customer "${deleteConfirm.customer_name}"? This action cannot be undone.` : ''}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  );
}

export default CustomerList;
