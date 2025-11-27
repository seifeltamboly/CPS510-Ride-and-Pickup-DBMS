import { useState } from 'react';
import Navigation from './components/Navigation';
import CustomerList from './components/CustomerList';
import DriverList from './components/DriverList';
import VehicleList from './components/VehicleList';
import LocationList from './components/LocationList';
import RideList from './components/RideList';
import PaymentList from './components/PaymentList';
import RatingList from './components/RatingList';
import Reports from './components/Reports';

function App() {
  const [currentView, setCurrentView] = useState('home');

  return (
    <div className="app">
      <header className="app-header">
        <h1>Ride & Pickup DBMS</h1>
        <Navigation currentView={currentView} onNavigate={setCurrentView} />
      </header>
      <main className="app-content">
        {currentView === 'home' && (
          <div className="home-view">
            <h2>Welcome to Ride & Pickup DBMS</h2>
            <p>Select a section from the navigation menu to get started.</p>
            <div className="home-features">
              <div className="feature-card">
                <h3>Manage Entities</h3>
                <p>Create, view, update, and delete customers, drivers, vehicles, locations, rides, payments, and ratings.</p>
              </div>
              <div className="feature-card">
                <h3>View Reports</h3>
                <p>Access advanced reports including top drivers, revenue analysis, ratings, and location statistics.</p>
              </div>
              <div className="feature-card">
                <h3>Oracle Database</h3>
                <p>All data is stored in an Oracle database with proper normalization and foreign key constraints.</p>
              </div>
            </div>
          </div>
        )}
        {currentView === 'customers' && <CustomerList />}
        {currentView === 'drivers' && <DriverList />}
        {currentView === 'vehicles' && <VehicleList />}
        {currentView === 'locations' && <LocationList />}
        {currentView === 'rides' && <RideList />}
        {currentView === 'payments' && <PaymentList />}
        {currentView === 'ratings' && <RatingList />}
        {currentView === 'reports' && <Reports />}
      </main>
    </div>
  );
}

export default App;
