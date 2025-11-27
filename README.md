# Ride & Pickup DBMS Web Application

A full-stack web application for managing a ride-sharing database system with customers, drivers, vehicles, locations, rides, payments, and ratings. Built with React frontend, Python Flask backend, and Oracle Database.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Technologies Used](#technologies-used)

## 🎯 Overview

This application provides a comprehensive web interface for managing a ride-sharing database. It implements full CRUD (Create, Read, Update, Delete) operations for all entities and includes advanced reporting capabilities with aggregated queries. The database schema is normalized to Boyce-Codd Normal Form (BCNF) ensuring data integrity and eliminating redundancy.

### Key Capabilities

- **Entity Management**: Complete CRUD operations for Customers, Drivers, Vehicles, Locations, Rides, Payments, and Ratings
- **Advanced Reports**: Analytics including top drivers, revenue analysis, rating statistics, and location popularity
- **Data Integrity**: Foreign key constraints and validation ensure referential integrity
- **User-Friendly Interface**: Responsive React UI with intuitive navigation and error handling
- **RESTful API**: Well-structured backend API with consistent JSON responses

## 🏗️ Architecture

The application follows a three-tier architecture:

```
┌─────────────────────────────────────────┐
│         React Frontend (Vite)           │
│  - Component-based UI                   │
│  - Axios for API calls                  │
│  - Client-side routing                  │
│  - Port 5173 (development)              │
└──────────────┬──────────────────────────┘
               │ HTTP/REST (JSON)
               │
┌──────────────▼──────────────────────────┐
│      Python Flask Backend API           │
│  - RESTful endpoints                    │
│  - Business logic layer                 │
│  - Database connection pool             │
│  - Port 5000                            │
└──────────────┬──────────────────────────┘
               │ cx_Oracle
               │ SQL queries
┌──────────────▼──────────────────────────┐
│         Oracle Database                 │
│  - 7 tables in BCNF                     │
│  - Foreign key constraints              │
│  - Dummy data for demonstration         │
└─────────────────────────────────────────┘
```

### Database Schema

The application manages seven interconnected tables:

- **Customer**: Customer information (ID, Name, Phone, Email)
- **Driver**: Driver information (ID, Name, Phone, License Number)
- **Vehicle**: Vehicle details (VIN, Model, Color, Year, Driver)
- **Location**: Pickup/dropoff locations (ID, Address, City, Postal Code)
- **Ride**: Ride records linking customers, drivers, vehicles, and locations
- **Payment**: Payment transactions for rides
- **Rating**: Customer and driver ratings for completed rides

## ✨ Features

### Entity Management
- View all records in organized tables
- Add new records with validated forms
- Edit existing records with pre-filled forms
- Delete records with confirmation dialogs
- Foreign key relationship handling

### Advanced Reports
1. **Top Drivers by Ride Count**: Identifies most active drivers
2. **Revenue by Payment Method**: Analyzes payment method preferences and totals
3. **Average Rating by Driver**: Shows driver performance metrics
4. **Rides by Location**: Displays popular pickup and dropoff locations
5. **Customer Ride History**: Complete ride history for individual customers

### User Interface
- Responsive design for desktop and mobile
- Loading indicators for async operations
- Success and error message notifications
- Intuitive navigation between sections
- Form validation with inline error messages

## 📦 Prerequisites

Before installing, ensure you have the following:

### Required Software

- **Python 3.8+**: Backend runtime
- **Node.js 16+** and **npm**: Frontend development
- **Oracle Database**: Express Edition (XE) or access to school Oracle DB
- **Git**: Version control (optional)

### Oracle Database Access

You need access to an Oracle Database instance with:
- Connection credentials (username, password)
- Database DSN (host:port/service_name)
- Permissions to create and modify tables

## 🚀 Installation

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Activate on macOS/Linux:
   source venv/bin/activate
   
   # Activate on Windows:
   venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Dependencies installed:
   - `Flask==3.0.0` - Web framework
   - `Flask-CORS==4.0.0` - Cross-origin resource sharing
   - `cx_Oracle==8.3.0` - Oracle database driver
   - `python-dotenv==1.0.0` - Environment variable management

4. **Configure environment variables**:
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your database credentials:
   ```env
   # Database Configuration
   DB_USER=your_oracle_username
   DB_PASSWORD=your_oracle_password
   DB_DSN=localhost:1521/XE
   
   # For school Oracle DB, use provided connection string:
   # DB_DSN=oracle.scs.ryerson.ca:1521/orcl
   
   # Connection Pool Configuration (Optional)
   DB_POOL_MIN=2
   DB_POOL_MAX=10
   DB_POOL_INCREMENT=1
   
   # Flask Configuration
   FLASK_ENV=development
   DEBUG=True
   ```

   **Important**: Never commit the `.env` file to version control!

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

   Dependencies installed:
   - `react@19.2.0` - UI library
   - `react-dom@19.2.0` - React DOM renderer
   - `axios@1.13.2` - HTTP client
   - `vite@7.2.2` - Build tool and dev server
   - `@vitejs/plugin-react@4.3.4` - React plugin for Vite

3. **Verify configuration**:
   
   The frontend is configured to connect to the backend at `http://localhost:5000`. This is set in `frontend/src/services/api.js`:
   ```javascript
   const API_BASE_URL = 'http://localhost:5000/api';
   ```
   
   If your backend runs on a different port, update this value.

### Database Setup

The application requires the database tables to be created before use. Refer to your previous database assignments for the table creation scripts.

#### Creating Tables

Run your table creation SQL scripts in SQL*Plus, SQL Developer, or your preferred Oracle client:

```sql
-- Example table creation (use your actual schema from assignments)
CREATE TABLE Customer (
    Customer_ID NUMBER PRIMARY KEY,
    Customer_Name VARCHAR2(100) NOT NULL,
    Phone_Number VARCHAR2(15),
    Email VARCHAR2(100)
);

-- ... (create remaining tables)
```

#### Seeding Test Data

After creating tables, populate them with dummy data for testing:

**Option 1: Python Script (Recommended)**

```bash
cd backend
python seed_data.py
```

The Python script provides:
- Better error handling and feedback
- Automatic connection using `.env` credentials
- Progress indicators
- Summary of inserted records

**Option 2: SQL Script**

```bash
# Using SQL*Plus
sqlplus username/password@database @init_db.sql

# Or open init_db.sql in SQL Developer and run it
```

#### Test Data Overview

The seeding scripts create:
- 5 Customers
- 5 Drivers
- 5 Vehicles
- 10 Locations (Toronto area)
- 15 Rides
- 10 Payments
- 8 Ratings

See `backend/SEEDING_README.md` for detailed information about the test data scenarios.

#### Verify Database Setup

After seeding, verify the data:

```sql
SELECT 'Customer' AS Table_Name, COUNT(*) AS Record_Count FROM Customer
UNION ALL
SELECT 'Driver', COUNT(*) FROM Driver
UNION ALL
SELECT 'Vehicle', COUNT(*) FROM Vehicle
UNION ALL
SELECT 'Location', COUNT(*) FROM Location
UNION ALL
SELECT 'Ride', COUNT(*) FROM Ride
UNION ALL
SELECT 'Payment', COUNT(*) FROM Payment
UNION ALL
SELECT 'Rating', COUNT(*) FROM Rating;
```

Expected counts: Customer(5), Driver(5), Vehicle(5), Location(10), Ride(15), Payment(10), Rating(8)

## 🎮 Running the Application

### Start the Backend Server

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Activate virtual environment** (if using one):
   ```bash
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Run the Flask server**:
   ```bash
   python app.py
   ```

   You should see:
   ```
   * Running on http://127.0.0.1:5000
   * Debug mode: on
   ```

   The backend API is now running on port 5000.

### Start the Frontend Development Server

1. **Open a new terminal** and navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. **Run the Vite development server**:
   ```bash
   npm start
   ```

   You should see:
   ```
   VITE v7.2.2  ready in XXX ms
   
   ➜  Local:   http://localhost:5173/
   ➜  Network: use --host to expose
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:5173
   ```

### Using the Application

1. **Navigation**: Use the navigation menu to switch between sections
2. **View Records**: Each section displays a table of all records
3. **Add Records**: Click "Add [Entity]" button to open the creation form
4. **Edit Records**: Click "Edit" button next to any record
5. **Delete Records**: Click "Delete" button (confirmation required)
6. **View Reports**: Navigate to Reports section and select a report type

## 📚 API Documentation

The backend provides RESTful API endpoints for all entities. All endpoints return JSON responses.

### Response Format

**Success Response**:
```json
{
  "success": true,
  "data": { ... } or [ ... ],
  "message": "Operation completed successfully"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

### Customer Endpoints

#### Get All Customers
```http
GET /api/customers
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "CUSTOMER_ID": 1,
      "CUSTOMER_NAME": "Alice Johnson",
      "PHONE_NUMBER": "416-555-0101",
      "EMAIL": "alice.johnson@email.com"
    }
  ]
}
```

#### Get Customer by ID
```http
GET /api/customers/<id>
```

**Response**: Single customer object

#### Create Customer
```http
POST /api/customers
Content-Type: application/json

{
  "customer_name": "John Doe",
  "phone_number": "416-555-0199",
  "email": "john.doe@email.com"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "customer_id": 6
  },
  "message": "Customer created successfully"
}
```

#### Update Customer
```http
PUT /api/customers/<id>
Content-Type: application/json

{
  "customer_name": "John Doe Updated",
  "phone_number": "416-555-0199",
  "email": "john.updated@email.com"
}
```

#### Delete Customer
```http
DELETE /api/customers/<id>
```

**Error Response** (if customer has rides):
```json
{
  "success": false,
  "error": "Cannot delete customer with existing rides"
}
```

### Driver Endpoints

#### Get All Drivers
```http
GET /api/drivers
```

#### Get Driver by ID
```http
GET /api/drivers/<id>
```

#### Create Driver
```http
POST /api/drivers
Content-Type: application/json

{
  "driver_name": "Jane Driver",
  "phone_number": "647-555-0201",
  "license_number": "D1234567"
}
```

#### Update Driver
```http
PUT /api/drivers/<id>
```

#### Delete Driver
```http
DELETE /api/drivers/<id>
```

### Vehicle Endpoints

#### Get All Vehicles
```http
GET /api/vehicles
```

**Response** (includes driver information):
```json
{
  "success": true,
  "data": [
    {
      "VEHICLE_VIN": "1HGBH41JXMN109186",
      "MODEL": "Honda Civic",
      "COLOR": "Silver",
      "REGISTRATION_YEAR": 2020,
      "DRIVER_ID": 1,
      "DRIVER_NAME": "John Driver"
    }
  ]
}
```

#### Get Vehicle by VIN
```http
GET /api/vehicles/<vin>
```

#### Create Vehicle
```http
POST /api/vehicles
Content-Type: application/json

{
  "vehicle_vin": "1HGBH41JXMN109999",
  "model": "Toyota Camry",
  "color": "Blue",
  "registration_year": 2021,
  "driver_id": 2
}
```

#### Update Vehicle
```http
PUT /api/vehicles/<vin>
```

#### Delete Vehicle
```http
DELETE /api/vehicles/<vin>
```

### Location Endpoints

#### Get All Locations
```http
GET /api/locations
```

#### Get Location by ID
```http
GET /api/locations/<id>
```

#### Create Location
```http
POST /api/locations
Content-Type: application/json

{
  "address": "123 Main St",
  "city": "Toronto",
  "postal_code": "M5H 2N2"
}
```

#### Update Location
```http
PUT /api/locations/<id>
```

#### Delete Location
```http
DELETE /api/locations/<id>
```

### Ride Endpoints

#### Get All Rides
```http
GET /api/rides
```

**Response** (includes joined data from related tables):
```json
{
  "success": true,
  "data": [
    {
      "RIDE_ID": 1,
      "CUSTOMER_ID": 1,
      "CUSTOMER_NAME": "Alice Johnson",
      "DRIVER_ID": 1,
      "DRIVER_NAME": "John Driver",
      "VEHICLE_VIN": "1HGBH41JXMN109186",
      "VEHICLE_MODEL": "Honda Civic",
      "PICKUP_LOCATION": 1,
      "PICKUP_ADDRESS": "123 King St W",
      "DROPOFF_LOCATION": 2,
      "DROPOFF_ADDRESS": "456 Queen St E",
      "START_TIME": "2024-01-15T08:30:00",
      "ARRIVAL_TIME": "2024-01-15T09:00:00"
    }
  ]
}
```

#### Get Ride by ID
```http
GET /api/rides/<id>
```

#### Create Ride
```http
POST /api/rides
Content-Type: application/json

{
  "customer_id": 1,
  "driver_id": 2,
  "vehicle_vin": "1HGBH41JXMN109186",
  "pickup_location": 1,
  "dropoff_location": 5,
  "start_time": "2024-01-20T10:00:00",
  "arrival_time": "2024-01-20T10:30:00"
}
```

#### Update Ride
```http
PUT /api/rides/<id>
```

#### Delete Ride
```http
DELETE /api/rides/<id>
```

### Payment Endpoints

#### Get All Payments
```http
GET /api/payments
```

**Response** (includes ride information):
```json
{
  "success": true,
  "data": [
    {
      "TRANSACTION_ID": 1,
      "RIDE_ID": 1,
      "AMOUNT": 25.50,
      "PAYMENT_METHOD": "Credit Card",
      "PAYMENT_STATUS": "Completed",
      "PAYMENT_DATE": "2024-01-15T09:05:00"
    }
  ]
}
```

#### Get Payment by Transaction ID
```http
GET /api/payments/<id>
```

#### Create Payment
```http
POST /api/payments
Content-Type: application/json

{
  "ride_id": 1,
  "amount": 25.50,
  "payment_method": "Credit Card",
  "payment_status": "Completed",
  "payment_date": "2024-01-20T10:35:00"
}
```

#### Update Payment
```http
PUT /api/payments/<id>
```

#### Delete Payment
```http
DELETE /api/payments/<id>
```

### Rating Endpoints

#### Get All Ratings
```http
GET /api/ratings
```

#### Get Rating by ID
```http
GET /api/ratings/<id>
```

#### Create Rating
```http
POST /api/ratings
Content-Type: application/json

{
  "ride_id": 1,
  "customer_rating": 5,
  "driver_rating": 5,
  "comments": "Excellent service!"
}
```

#### Update Rating
```http
PUT /api/ratings/<id>
```

#### Delete Rating
```http
DELETE /api/ratings/<id>
```

### Report Endpoints

#### Top Drivers by Ride Count
```http
GET /api/reports/top-drivers
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "DRIVER_ID": 1,
      "DRIVER_NAME": "John Driver",
      "RIDE_COUNT": 5
    }
  ]
}
```

#### Revenue by Payment Method
```http
GET /api/reports/revenue-by-method
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "PAYMENT_METHOD": "Credit Card",
      "TOTAL_REVENUE": 105.50,
      "TRANSACTION_COUNT": 4
    }
  ]
}
```

#### Average Rating by Driver
```http
GET /api/reports/average-ratings
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "DRIVER_ID": 1,
      "DRIVER_NAME": "John Driver",
      "AVG_RATING": 4.67,
      "RATING_COUNT": 3
    }
  ]
}
```

#### Rides by Location
```http
GET /api/reports/rides-by-location
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "LOCATION_ID": 1,
      "ADDRESS": "123 King St W",
      "CITY": "Toronto",
      "PICKUP_COUNT": 3,
      "DROPOFF_COUNT": 2
    }
  ]
}
```

#### Customer Ride History
```http
GET /api/reports/customer-history/<customer_id>
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "RIDE_ID": 1,
      "START_TIME": "2024-01-15T08:30:00",
      "ARRIVAL_TIME": "2024-01-15T09:00:00",
      "DRIVER_NAME": "John Driver",
      "VEHICLE_MODEL": "Honda Civic",
      "PICKUP_ADDRESS": "123 King St W",
      "DROPOFF_ADDRESS": "456 Queen St E",
      "AMOUNT": 25.50,
      "PAYMENT_STATUS": "Completed"
    }
  ]
}
```

## 📁 Project Structure

```
ride-pickup-web-app/
├── backend/
│   ├── app.py                 # Flask application and API routes
│   ├── db.py                  # Database connection and query functions
│   ├── config.py              # Configuration management
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variable template
│   ├── .env                  # Environment variables (not in git)
│   ├── seed_data.py          # Python script to seed database
│   ├── init_db.sql           # SQL script to seed database
│   └── SEEDING_README.md     # Database seeding documentation
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Navigation.jsx
│   │   │   ├── CustomerList.jsx
│   │   │   ├── CustomerForm.jsx
│   │   │   ├── DriverList.jsx
│   │   │   ├── DriverForm.jsx
│   │   │   ├── VehicleList.jsx
│   │   │   ├── VehicleForm.jsx
│   │   │   ├── LocationList.jsx
│   │   │   ├── LocationForm.jsx
│   │   │   ├── RideList.jsx
│   │   │   ├── RideForm.jsx
│   │   │   ├── PaymentList.jsx
│   │   │   ├── PaymentForm.jsx
│   │   │   ├── RatingList.jsx
│   │   │   ├── RatingForm.jsx
│   │   │   ├── Reports.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── ErrorMessage.jsx
│   │   │   ├── SuccessMessage.jsx
│   │   │   └── ConfirmDialog.jsx
│   │   ├── services/
│   │   │   └── api.js        # Axios API service layer
│   │   ├── utils/
│   │   │   └── validation.js # Form validation utilities
│   │   ├── App.jsx           # Root component with routing
│   │   ├── App.css           # Global styles
│   │   └── main.jsx          # React entry point
│   ├── index.html            # HTML entry point
│   ├── package.json          # Node.js dependencies
│   ├── vite.config.js        # Vite configuration
│   └── dist/                 # Production build output
│
├── .kiro/
│   └── specs/
│       └── ride-pickup-web-app/
│           ├── requirements.md  # Feature requirements
│           ├── design.md        # Design document
│           └── tasks.md         # Implementation tasks
│
└── README.md                 # This file
```

## 🔧 Troubleshooting

### Backend Issues

#### Error: "No module named 'cx_Oracle'"

**Solution**: Install the cx_Oracle package
```bash
pip install cx_Oracle
```

#### Error: "DPI-1047: Cannot locate a 64-bit Oracle Client library"

**Cause**: cx_Oracle requires Oracle Instant Client to be installed

**Solution**:
1. Download Oracle Instant Client from Oracle website
2. Extract to a directory (e.g., `/opt/oracle/instantclient_19_8`)
3. Set environment variables:
   ```bash
   # macOS/Linux
   export DYLD_LIBRARY_PATH=/opt/oracle/instantclient_19_8:$DYLD_LIBRARY_PATH
   
   # Or add to ~/.bash_profile or ~/.zshrc
   ```

#### Error: "ORA-12541: TNS:no listener"

**Cause**: Cannot connect to Oracle database

**Solution**:
1. Verify Oracle database is running
2. Check DB_DSN in `.env` file is correct
3. Test connection with SQL*Plus:
   ```bash
   sqlplus username/password@host:port/service_name
   ```
4. Verify firewall allows connection to Oracle port (usually 1521)

#### Error: "ORA-01017: invalid username/password"

**Solution**: Check DB_USER and DB_PASSWORD in `.env` file

#### Error: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Cause**: CORS not properly configured

**Solution**: Verify Flask-CORS is installed and configured in `app.py`:
```python
from flask_cors import CORS
CORS(app)
```

#### Backend server won't start

**Solution**:
1. Check if port 5000 is already in use:
   ```bash
   lsof -i :5000  # macOS/Linux
   ```
2. Kill the process or change the port in `app.py`
3. Verify all dependencies are installed: `pip install -r requirements.txt`
4. Check for syntax errors in Python files

### Frontend Issues

#### Error: "Cannot GET /"

**Cause**: Frontend dev server not running

**Solution**: Start the Vite dev server:
```bash
cd frontend
npm start
```

#### Error: "Network Error" when making API calls

**Cause**: Backend server not running or wrong API URL

**Solution**:
1. Verify backend is running on port 5000
2. Check API_BASE_URL in `frontend/src/services/api.js`
3. Verify CORS is enabled on backend

#### Error: "npm: command not found"

**Solution**: Install Node.js and npm from nodejs.org

#### Error: Module not found errors

**Solution**: Install dependencies:
```bash
cd frontend
npm install
```

#### Frontend won't start

**Solution**:
1. Delete `node_modules` and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```
2. Check Node.js version: `node --version` (should be 16+)
3. Clear npm cache: `npm cache clean --force`

### Database Issues

#### Error: "ORA-00942: table or view does not exist"

**Cause**: Database tables not created

**Solution**: Run your table creation scripts before using the application

#### Error: "ORA-02291: integrity constraint violated - parent key not found"

**Cause**: Trying to create a record with invalid foreign key

**Solution**:
1. Verify the referenced record exists (e.g., driver exists before creating vehicle)
2. Check the ID/VIN you're using is correct
3. Ensure database is properly seeded with test data

#### Error: "ORA-00001: unique constraint violated"

**Cause**: Trying to insert duplicate primary key or unique value

**Solution**:
1. Use different ID/VIN for new records
2. If re-seeding database, clear existing data first
3. Check for duplicate email addresses or license numbers

#### Seeding script fails

**Solution**:
1. Verify database connection credentials in `.env`
2. Ensure tables are created before seeding
3. Clear existing data if re-running seed script
4. Check `backend/SEEDING_README.md` for detailed troubleshooting

### General Issues

#### Changes not reflecting in browser

**Solution**:
1. Hard refresh browser: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (macOS)
2. Clear browser cache
3. Check browser console for JavaScript errors
4. Verify both frontend and backend servers are running

#### Application is slow

**Solution**:
1. Check database connection pool settings in `.env`
2. Verify database has indexes on foreign keys
3. Check network latency to database
4. Monitor backend logs for slow queries

#### Can't delete records

**Cause**: Foreign key constraints prevent deletion

**Solution**: This is expected behavior. Delete dependent records first:
- Delete ratings before deleting rides
- Delete payments before deleting rides
- Delete rides before deleting customers, drivers, or vehicles
- Delete vehicles before deleting drivers

## 🛠️ Technologies Used

### Frontend
- **React 19.2.0**: JavaScript library for building user interfaces
- **Vite 7.2.2**: Fast build tool and development server
- **Axios 1.13.2**: Promise-based HTTP client
- **CSS3**: Styling and responsive design

### Backend
- **Python 3.x**: Programming language
- **Flask 3.0.0**: Lightweight web framework
- **Flask-CORS 4.0.0**: Cross-origin resource sharing
- **cx_Oracle 8.3.0**: Oracle database driver
- **python-dotenv 1.0.0**: Environment variable management

### Database
- **Oracle Database**: Relational database management system
- **SQL**: Structured Query Language for data operations

### Development Tools
- **Git**: Version control
- **npm**: Package manager for JavaScript
- **pip**: Package manager for Python
- **Virtual Environment**: Python dependency isolation

## 📝 Additional Notes

### Security Considerations

- Never commit `.env` file to version control
- Use strong database passwords
- Disable Flask debug mode in production
- Implement authentication/authorization for production use
- Validate and sanitize all user inputs
- Use HTTPS in production

### Performance Optimization

- Database connection pooling is configured for optimal performance
- Frontend uses React's virtual DOM for efficient rendering
- API responses are cached where appropriate
- Indexes should be added to foreign key columns for faster queries

### Future Enhancements

Potential improvements for the application:
- User authentication and authorization
- Real-time updates using WebSockets
- Data export functionality (CSV, PDF)
- Advanced filtering and search
- Pagination for large datasets
- Data visualization with charts
- Mobile app version
- Email notifications
- Audit logging

## 📄 License

This project is created for educational purposes as part of CPS 510 coursework.

## 👥 Contributors

Developed as part of CPS 510 Database Systems course assignments.

---

For questions or issues, please refer to the troubleshooting section or consult the course materials.
