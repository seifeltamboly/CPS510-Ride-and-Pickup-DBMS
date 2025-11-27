import './Navigation.css';

const Navigation = ({ currentView, onNavigate }) => {
  const navItems = [
    { id: 'home', label: 'Home' },
    { id: 'customers', label: 'Customers' },
    { id: 'drivers', label: 'Drivers' },
    { id: 'vehicles', label: 'Vehicles' },
    { id: 'locations', label: 'Locations' },
    { id: 'rides', label: 'Rides' },
    { id: 'payments', label: 'Payments' },
    { id: 'ratings', label: 'Ratings' },
    { id: 'reports', label: 'Reports' }
  ];

  return (
    <nav className="navigation">
      {navItems.map((item) => (
        <button
          key={item.id}
          onClick={() => onNavigate(item.id)}
          className={currentView === item.id ? 'nav-link active' : 'nav-link'}
          aria-current={currentView === item.id ? 'page' : undefined}
        >
          {item.label}
        </button>
      ))}
    </nav>
  );
};

export default Navigation;
