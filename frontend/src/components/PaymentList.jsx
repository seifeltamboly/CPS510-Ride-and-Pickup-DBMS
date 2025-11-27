import { useState, useEffect } from 'react';
import { paymentService } from '../services/api';
import PaymentForm from './PaymentForm';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import SuccessMessage from './SuccessMessage';
import ConfirmDialog from './ConfirmDialog';
import { getErrorMessage } from '../utils/validation';
import './PaymentList.css';

function PaymentList() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingPayment, setEditingPayment] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // Load payments on component mount
  useEffect(() => {
    loadPayments();
  }, []);

  // Fetch all payments from API
  const loadPayments = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await paymentService.getAll();
      setPayments(response.data || []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // Handle add payment button click
  const handleAdd = () => {
    setEditingPayment(null);
    setShowForm(true);
    setError(null);
    setSuccess(null);
  };

  // Handle edit payment button click
  const handleEdit = (payment) => {
    setEditingPayment(payment);
    setShowForm(true);
    setError(null);
    setSuccess(null);
  };

  // Handle delete payment button click
  const handleDelete = (payment) => {
    setDeleteConfirm(payment);
  };

  // Confirm delete operation
  const confirmDelete = async () => {
    if (!deleteConfirm) return;

    try {
      setError(null);
      await paymentService.delete(deleteConfirm.transaction_id);
      setSuccess(`Payment #${deleteConfirm.transaction_id} deleted successfully`);
      setDeleteConfirm(null);
      loadPayments();
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
    setEditingPayment(null);
    loadPayments();
  };

  // Handle form cancel
  const handleFormCancel = () => {
    setShowForm(false);
    setEditingPayment(null);
  };

  // Format date for display
  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString();
    } catch {
      return dateStr;
    }
  };

  // Format currency
  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return 'N/A';
    return `$${parseFloat(amount).toFixed(2)}`;
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="payment-list-container">
      <div className="payment-list-header">
        <h2>Payment Management</h2>
        {!showForm && (
          <button className="btn btn-primary" onClick={handleAdd}>
            Add Payment
          </button>
        )}
      </div>

      {error && <ErrorMessage message={error} onClose={() => setError(null)} />}
      {success && <SuccessMessage message={success} onClose={() => setSuccess(null)} />}

      {showForm ? (
        <PaymentForm
          payment={editingPayment}
          onSuccess={handleFormSuccess}
          onCancel={handleFormCancel}
        />
      ) : (
        <div className="payment-table-wrapper">
          {payments.length === 0 ? (
            <p className="no-data">No payments found. Click "Add Payment" to create one.</p>
          ) : (
            <table className="payment-table">
              <thead>
                <tr>
                  <th>Transaction ID</th>
                  <th>Ride ID</th>
                  <th>Ride Details</th>
                  <th>Amount</th>
                  <th>Payment Method</th>
                  <th>Payment Status</th>
                  <th>Payment Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {payments.map((payment) => (
                  <tr key={payment.transaction_id}>
                    <td>{payment.transaction_id}</td>
                    <td>{payment.ride_id}</td>
                    <td>
                      {payment.customer_name && payment.driver_name ? (
                        <div className="ride-details">
                          <div>{payment.customer_name} → {payment.driver_name}</div>
                          <div className="ride-locations">
                            {payment.pickup_address && payment.dropoff_address && (
                              <small>{payment.pickup_address} to {payment.dropoff_address}</small>
                            )}
                          </div>
                        </div>
                      ) : (
                        'N/A'
                      )}
                    </td>
                    <td className="amount">{formatCurrency(payment.amount)}</td>
                    <td>{payment.payment_method || 'N/A'}</td>
                    <td>
                      <span className={`status-badge status-${payment.payment_status?.toLowerCase()}`}>
                        {payment.payment_status || 'N/A'}
                      </span>
                    </td>
                    <td>{formatDate(payment.payment_date)}</td>
                    <td className="actions">
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleEdit(payment)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(payment)}
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
        title="Delete Payment"
        message={deleteConfirm ? `Are you sure you want to delete Payment #${deleteConfirm.transaction_id}? This action cannot be undone.` : ''}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  );
}

export default PaymentList;
