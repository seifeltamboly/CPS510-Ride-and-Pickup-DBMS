import { useState, useEffect } from 'react';
import { reportService, customerService } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import { getErrorMessage } from '../utils/validation';
import './Reports.css';

function Reports() {
  const [selectedReport, setSelectedReport] = useState('top-drivers');
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [customers, setCustomers] = useState([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState('');

  // Load customers for customer history report
  useEffect(() => {
    const loadCustomers = async () => {
      try {
        const response = await customerService.getAll();
        if (response.success && response.data) {
          setCustomers(response.data);
        }
      } catch (err) {
        console.error('Error loading customers:', err);
      }
    };
    loadCustomers();
  }, []);

  // Load report data when report selection changes
  useEffect(() => {
    if (selectedReport !== 'customer-history') {
      loadReportData();
    }
  }, [selectedReport]);

  const loadReportData = async () => {
    setLoading(true);
    setError('');
    setReportData(null);

    try {
      let response;
      switch (selectedReport) {
        case 'top-drivers':
          response = await reportService.getTopDrivers();
          break;
        case 'revenue-by-method':
          response = await reportService.getRevenueByMethod();
          break;
        case 'average-ratings':
          response = await reportService.getAverageRatings();
          break;
        case 'rides-by-location':
          response = await reportService.getRidesByLocation();
          break;
        default:
          throw new Error('Invalid report type');
      }

      if (response.success && response.data) {
        setReportData(response.data);
      } else {
        setError('Failed to load report data');
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const loadCustomerHistory = async () => {
    if (!selectedCustomerId) {
      setError('Please select a customer');
      return;
    }

    setLoading(true);
    setError('');
    setReportData(null);

    try {
      const response = await reportService.getCustomerHistory(selectedCustomerId);
      if (response.success && response.data) {
        setReportData(response.data);
      } else {
        setError('Failed to load customer history');
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleReportChange = (e) => {
    setSelectedReport(e.target.value);
    setReportData(null);
    setError('');
  };

  const renderTopDriversReport = () => {
    if (!reportData || reportData.length === 0) {
      return <p className="no-data">No data available</p>;
    }

    return (
      <div className="report-table-container">
        <h3>Top Drivers by Ride Count</h3>
        <table className="report-table">
          <thead>
            <tr>
              <th>Driver ID</th>
              <th>Driver Name</th>
              <th>Total Rides</th>
            </tr>
          </thead>
          <tbody>
            {reportData.map((driver, index) => (
              <tr key={index}>
                <td>{driver.DRIVER_ID}</td>
                <td>{driver.DRIVER_NAME}</td>
                <td>{driver.RIDE_COUNT}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderRevenueByMethodReport = () => {
    if (!reportData || reportData.length === 0) {
      return <p className="no-data">No data available</p>;
    }

    return (
      <div className="report-table-container">
        <h3>Revenue by Payment Method</h3>
        <table className="report-table">
          <thead>
            <tr>
              <th>Payment Method</th>
              <th>Total Revenue</th>
              <th>Transaction Count</th>
            </tr>
          </thead>
          <tbody>
            {reportData.map((method, index) => (
              <tr key={index}>
                <td>{method.PAYMENT_METHOD}</td>
                <td>${parseFloat(method.TOTAL_REVENUE).toFixed(2)}</td>
                <td>{method.TRANSACTION_COUNT}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderAverageRatingsReport = () => {
    if (!reportData || reportData.length === 0) {
      return <p className="no-data">No data available</p>;
    }

    return (
      <div className="report-table-container">
        <h3>Average Rating by Driver</h3>
        <table className="report-table">
          <thead>
            <tr>
              <th>Driver ID</th>
              <th>Driver Name</th>
              <th>Average Rating</th>
              <th>Total Ratings</th>
            </tr>
          </thead>
          <tbody>
            {reportData.map((driver, index) => (
              <tr key={index}>
                <td>{driver.DRIVER_ID}</td>
                <td>{driver.DRIVER_NAME}</td>
                <td>{driver.AVG_RATING ? parseFloat(driver.AVG_RATING).toFixed(2) : 'N/A'}</td>
                <td>{driver.RATING_COUNT}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderRidesByLocationReport = () => {
    if (!reportData || reportData.length === 0) {
      return <p className="no-data">No data available</p>;
    }

    return (
      <div className="report-table-container">
        <h3>Rides by Location</h3>
        <table className="report-table">
          <thead>
            <tr>
              <th>Location ID</th>
              <th>Address</th>
              <th>City</th>
              <th>Pickup Count</th>
              <th>Dropoff Count</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {reportData.map((location, index) => (
              <tr key={index}>
                <td>{location.LOCATION_ID}</td>
                <td>{location.ADDRESS}</td>
                <td>{location.CITY}</td>
                <td>{location.PICKUP_COUNT}</td>
                <td>{location.DROPOFF_COUNT}</td>
                <td>{parseInt(location.PICKUP_COUNT) + parseInt(location.DROPOFF_COUNT)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderCustomerHistoryReport = () => {
    if (!reportData || reportData.length === 0) {
      return <p className="no-data">No ride history found for this customer</p>;
    }

    return (
      <div className="report-table-container">
        <h3>Customer Ride History</h3>
        <table className="report-table">
          <thead>
            <tr>
              <th>Ride ID</th>
              <th>Start Time</th>
              <th>Arrival Time</th>
              <th>Driver</th>
              <th>Vehicle</th>
              <th>Pickup</th>
              <th>Dropoff</th>
              <th>Amount</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {reportData.map((ride, index) => (
              <tr key={index}>
                <td>{ride.RIDE_ID}</td>
                <td>{new Date(ride.START_TIME).toLocaleString()}</td>
                <td>{ride.ARRIVAL_TIME ? new Date(ride.ARRIVAL_TIME).toLocaleString() : 'N/A'}</td>
                <td>{ride.DRIVER_NAME}</td>
                <td>{ride.VEHICLE_MODEL}</td>
                <td>{ride.PICKUP_ADDRESS}</td>
                <td>{ride.DROPOFF_ADDRESS}</td>
                <td>{ride.AMOUNT ? `$${parseFloat(ride.AMOUNT).toFixed(2)}` : 'N/A'}</td>
                <td>{ride.PAYMENT_STATUS || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderReportContent = () => {
    if (loading) {
      return <LoadingSpinner />;
    }

    if (error) {
      return <ErrorMessage message={error} />;
    }

    switch (selectedReport) {
      case 'top-drivers':
        return renderTopDriversReport();
      case 'revenue-by-method':
        return renderRevenueByMethodReport();
      case 'average-ratings':
        return renderAverageRatingsReport();
      case 'rides-by-location':
        return renderRidesByLocationReport();
      case 'customer-history':
        return renderCustomerHistoryReport();
      default:
        return <p>Select a report to view</p>;
    }
  };

  return (
    <div className="reports-container">
      <h2>Reports</h2>

      <div className="report-selector">
        <label htmlFor="report-type">Select Report:</label>
        <select
          id="report-type"
          value={selectedReport}
          onChange={handleReportChange}
          className="report-dropdown"
        >
          <option value="top-drivers">Top Drivers by Ride Count</option>
          <option value="revenue-by-method">Revenue by Payment Method</option>
          <option value="average-ratings">Average Rating by Driver</option>
          <option value="rides-by-location">Rides by Location</option>
          <option value="customer-history">Customer Ride History</option>
        </select>
      </div>

      {selectedReport === 'customer-history' && (
        <div className="customer-selector">
          <label htmlFor="customer-select">Select Customer:</label>
          <select
            id="customer-select"
            value={selectedCustomerId}
            onChange={(e) => setSelectedCustomerId(e.target.value)}
            className="customer-dropdown"
          >
            <option value="">-- Select a Customer --</option>
            {customers.map((customer) => (
              <option key={customer.CUSTOMER_ID} value={customer.CUSTOMER_ID}>
                {customer.CUSTOMER_NAME} (ID: {customer.CUSTOMER_ID})
              </option>
            ))}
          </select>
          <button onClick={loadCustomerHistory} className="load-history-btn">
            Load History
          </button>
        </div>
      )}

      <div className="report-content">
        {renderReportContent()}
      </div>
    </div>
  );
}

export default Reports;
