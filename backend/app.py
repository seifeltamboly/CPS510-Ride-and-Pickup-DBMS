"""
Ride & Pickup DBMS - Flask Backend API
Main application file with Flask initialization and API endpoints
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import cx_Oracle
from db import get_connection
import re

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Configure CORS to allow frontend communication
# In development, allow all origins. In production, specify frontend URL
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# Health check endpoint to verify server is running
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the server is running
    Returns server status and basic information
    """
    return jsonify({
        "success": True,
        "message": "Server is running",
        "status": "healthy"
    }), 200


# ============================================================================
# CUSTOMER API ENDPOINTS
# ============================================================================

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """
    Retrieve all customers from the database.
    
    Returns:
        JSON response with list of all customers including:
        - Customer_ID
        - Customer_Name
        - Phone_Number
        - Email
        
    Response format:
        {
            "success": true,
            "data": [
                {
                    "customer_id": 1,
                    "customer_name": "John Doe",
                    "phone_number": "555-1234",
                    "email": "john@example.com"
                },
                ...
            ]
        }
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: SELECT all customers from Customer table
        # Returns all customer records ordered by Customer_ID for consistent display
        query = """
            SELECT Customer_ID, Customer_Name, Phone_Number, Email
            FROM Customer
            ORDER BY Customer_ID
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert database rows to list of dictionaries for JSON response
        customers = []
        for row in rows:
            customers.append({
                "customer_id": row[0],
                "customer_name": row[1],
                "phone_number": row[2],
                "email": row[3]
            })
        
        return jsonify({
            "success": True,
            "data": customers
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """
    Retrieve a single customer by ID.
    
    Args:
        customer_id: The ID of the customer to retrieve
        
    Returns:
        JSON response with customer details or error if not found
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: SELECT single customer by Customer_ID
        # Uses parameterized query to prevent SQL injection
        query = """
            SELECT Customer_ID, Customer_Name, Phone_Number, Email
            FROM Customer
            WHERE Customer_ID = :customer_id
        """
        
        cursor.execute(query, {"customer_id": customer_id})
        row = cursor.fetchone()
        
        if row is None:
            return jsonify({
                "success": False,
                "error": f"Customer with ID {customer_id} not found"
            }), 404
        
        customer = {
            "customer_id": row[0],
            "customer_name": row[1],
            "phone_number": row[2],
            "email": row[3]
        }
        
        return jsonify({
            "success": True,
            "data": customer
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/customers', methods=['POST'])
def create_customer():
    """
    Create a new customer record.
    
    Expected JSON body:
        {
            "customer_name": "John Doe",
            "phone_number": "555-1234",
            "email": "john@example.com"
        }
        
    Returns:
        JSON response with created customer data including generated ID
    """
    conn = None
    cursor = None
    
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['customer_name', 'phone_number', 'email']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({
                "success": False,
                "error": "Invalid email format"
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: INSERT new customer into Customer table
        # Uses RETURNING clause to get the auto-generated Customer_ID
        # Assumes Customer_ID is generated by a sequence or trigger
        query = """
            INSERT INTO Customer (Customer_Name, Phone_Number, Email)
            VALUES (:customer_name, :phone_number, :email)
            RETURNING Customer_ID INTO :customer_id
        """
        
        # Variable to capture the returned Customer_ID
        customer_id_var = cursor.var(cx_Oracle.NUMBER)
        
        cursor.execute(query, {
            "customer_name": data['customer_name'],
            "phone_number": data['phone_number'],
            "email": data['email'],
            "customer_id": customer_id_var
        })
        
        conn.commit()
        
        # Get the generated customer ID
        new_customer_id = customer_id_var.getvalue()[0]
        
        return jsonify({
            "success": True,
            "data": {
                "customer_id": int(new_customer_id),
                "customer_name": data['customer_name'],
                "phone_number": data['phone_number'],
                "email": data['email']
            },
            "message": "Customer created successfully"
        }), 201
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        # Handle unique constraint violations (e.g., duplicate email)
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Data integrity error: {error_obj.message}"
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """
    Update an existing customer record.
    
    Args:
        customer_id: The ID of the customer to update
        
    Expected JSON body:
        {
            "customer_name": "John Doe Updated",
            "phone_number": "555-5678",
            "email": "john.updated@example.com"
        }
        
    Returns:
        JSON response with updated customer data
    """
    conn = None
    cursor = None
    
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['customer_name', 'phone_number', 'email']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({
                "success": False,
                "error": "Invalid email format"
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if customer exists
        check_query = "SELECT Customer_ID FROM Customer WHERE Customer_ID = :customer_id"
        cursor.execute(check_query, {"customer_id": customer_id})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Customer with ID {customer_id} not found"
            }), 404
        
        # SQL Query: UPDATE customer record in Customer table
        # Updates all customer fields based on provided data
        # Uses WHERE clause to target specific customer by ID
        query = """
            UPDATE Customer
            SET Customer_Name = :customer_name,
                Phone_Number = :phone_number,
                Email = :email
            WHERE Customer_ID = :customer_id
        """
        
        cursor.execute(query, {
            "customer_name": data['customer_name'],
            "phone_number": data['phone_number'],
            "email": data['email'],
            "customer_id": customer_id
        })
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "customer_id": customer_id,
                "customer_name": data['customer_name'],
                "phone_number": data['phone_number'],
                "email": data['email']
            },
            "message": "Customer updated successfully"
        }), 200
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Data integrity error: {error_obj.message}"
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """
    Delete a customer record.
    
    Args:
        customer_id: The ID of the customer to delete
        
    Returns:
        JSON response confirming deletion or error if customer has associated rides
        
    Note:
        This operation will fail if the customer has associated rides due to
        foreign key constraints. The error message will inform the user about
        the constraint violation.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if customer exists
        check_query = "SELECT Customer_ID FROM Customer WHERE Customer_ID = :customer_id"
        cursor.execute(check_query, {"customer_id": customer_id})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Customer with ID {customer_id} not found"
            }), 404
        
        # SQL Query: DELETE customer from Customer table
        # This will fail if customer has associated rides due to foreign key constraint
        # The foreign key constraint ensures referential integrity
        query = """
            DELETE FROM Customer
            WHERE Customer_ID = :customer_id
        """
        
        cursor.execute(query, {"customer_id": customer_id})
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Customer with ID {customer_id} deleted successfully"
        }), 200
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        
        # Handle foreign key constraint violation
        # This occurs when trying to delete a customer with existing rides
        return jsonify({
            "success": False,
            "error": "Cannot delete customer with existing rides. Please delete associated rides first.",
            "details": error_obj.message
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============================================================================
# DRIVER API ENDPOINTS
# ============================================================================

@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    """
    Retrieve all drivers from the database.
    
    Returns:
        JSON response with list of all drivers including:
        - Driver_ID
        - Driver_Name
        - Phone_Number
        - License_Number
        
    Response format:
        {
            "success": true,
            "data": [
                {
                    "driver_id": 1,
                    "driver_name": "Jane Smith",
                    "phone_number": "555-5678",
                    "license_number": "DL123456"
                },
                ...
            ]
        }
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: SELECT all drivers from Driver table
        # Returns all driver records ordered by Driver_ID for consistent display
        query = """
            SELECT Driver_ID, Driver_Name, Phone_Number, License_Number
            FROM Driver
            ORDER BY Driver_ID
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert database rows to list of dictionaries for JSON response
        drivers = []
        for row in rows:
            drivers.append({
                "driver_id": row[0],
                "driver_name": row[1],
                "phone_number": row[2],
                "license_number": row[3]
            })
        
        return jsonify({
            "success": True,
            "data": drivers
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/drivers/<int:driver_id>', methods=['GET'])
def get_driver(driver_id):
    """
    Retrieve a single driver by ID.
    
    Args:
        driver_id: The ID of the driver to retrieve
        
    Returns:
        JSON response with driver details or error if not found
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: SELECT single driver by Driver_ID
        # Uses parameterized query to prevent SQL injection
        query = """
            SELECT Driver_ID, Driver_Name, Phone_Number, License_Number
            FROM Driver
            WHERE Driver_ID = :driver_id
        """
        
        cursor.execute(query, {"driver_id": driver_id})
        row = cursor.fetchone()
        
        if row is None:
            return jsonify({
                "success": False,
                "error": f"Driver with ID {driver_id} not found"
            }), 404
        
        driver = {
            "driver_id": row[0],
            "driver_name": row[1],
            "phone_number": row[2],
            "license_number": row[3]
        }
        
        return jsonify({
            "success": True,
            "data": driver
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/drivers', methods=['POST'])
def create_driver():
    """
    Create a new driver record.
    
    Expected JSON body:
        {
            "driver_name": "Jane Smith",
            "phone_number": "555-5678",
            "license_number": "DL123456"
        }
        
    Returns:
        JSON response with created driver data including generated ID
    """
    conn = None
    cursor = None
    
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['driver_name', 'phone_number', 'license_number']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: INSERT new driver into Driver table
        # Uses RETURNING clause to get the auto-generated Driver_ID
        # Assumes Driver_ID is generated by a sequence or trigger
        query = """
            INSERT INTO Driver (Driver_Name, Phone_Number, License_Number)
            VALUES (:driver_name, :phone_number, :license_number)
            RETURNING Driver_ID INTO :driver_id
        """
        
        # Variable to capture the returned Driver_ID
        driver_id_var = cursor.var(cx_Oracle.NUMBER)
        
        cursor.execute(query, {
            "driver_name": data['driver_name'],
            "phone_number": data['phone_number'],
            "license_number": data['license_number'],
            "driver_id": driver_id_var
        })
        
        conn.commit()
        
        # Get the generated driver ID
        new_driver_id = driver_id_var.getvalue()[0]
        
        return jsonify({
            "success": True,
            "data": {
                "driver_id": int(new_driver_id),
                "driver_name": data['driver_name'],
                "phone_number": data['phone_number'],
                "license_number": data['license_number']
            },
            "message": "Driver created successfully"
        }), 201
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        # Handle unique constraint violations (e.g., duplicate license number)
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Data integrity error: {error_obj.message}"
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/drivers/<int:driver_id>', methods=['PUT'])
def update_driver(driver_id):
    """
    Update an existing driver record.
    
    Args:
        driver_id: The ID of the driver to update
        
    Expected JSON body:
        {
            "driver_name": "Jane Smith Updated",
            "phone_number": "555-9999",
            "license_number": "DL789012"
        }
        
    Returns:
        JSON response with updated driver data
    """
    conn = None
    cursor = None
    
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['driver_name', 'phone_number', 'license_number']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if driver exists
        check_query = "SELECT Driver_ID FROM Driver WHERE Driver_ID = :driver_id"
        cursor.execute(check_query, {"driver_id": driver_id})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Driver with ID {driver_id} not found"
            }), 404
        
        # SQL Query: UPDATE driver record in Driver table
        # Updates all driver fields based on provided data
        # Uses WHERE clause to target specific driver by ID
        query = """
            UPDATE Driver
            SET Driver_Name = :driver_name,
                Phone_Number = :phone_number,
                License_Number = :license_number
            WHERE Driver_ID = :driver_id
        """
        
        cursor.execute(query, {
            "driver_name": data['driver_name'],
            "phone_number": data['phone_number'],
            "license_number": data['license_number'],
            "driver_id": driver_id
        })
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "driver_id": driver_id,
                "driver_name": data['driver_name'],
                "phone_number": data['phone_number'],
                "license_number": data['license_number']
            },
            "message": "Driver updated successfully"
        }), 200
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Data integrity error: {error_obj.message}"
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/drivers/<int:driver_id>', methods=['DELETE'])
def delete_driver(driver_id):
    """
    Delete a driver record.
    
    Args:
        driver_id: The ID of the driver to delete
        
    Returns:
        JSON response confirming deletion or error if driver has associated vehicles or rides
        
    Note:
        This operation will fail if the driver has associated vehicles or rides due to
        foreign key constraints. The error message will inform the user about
        the constraint violation.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if driver exists
        check_query = "SELECT Driver_ID FROM Driver WHERE Driver_ID = :driver_id"
        cursor.execute(check_query, {"driver_id": driver_id})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Driver with ID {driver_id} not found"
            }), 404
        
        # SQL Query: DELETE driver from Driver table
        # This will fail if driver has associated vehicles or rides due to foreign key constraint
        # The foreign key constraint ensures referential integrity between Driver, Vehicle, and Ride tables
        query = """
            DELETE FROM Driver
            WHERE Driver_ID = :driver_id
        """
        
        cursor.execute(query, {"driver_id": driver_id})
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Driver with ID {driver_id} deleted successfully"
        }), 200
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        
        # Handle foreign key constraint violation
        # This occurs when trying to delete a driver with existing vehicles or rides
        return jsonify({
            "success": False,
            "error": "Cannot delete driver with existing vehicles or rides. Please delete associated records first.",
            "details": error_obj.message
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============================================================================
# VEHICLE API ENDPOINTS
# ============================================================================

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    """
    Retrieve all vehicles from the database with driver information.
    
    Returns:
        JSON response with list of all vehicles including:
        - Vehicle_VIN
        - Model
        - Color
        - Registration_Year
        - Driver_ID
        - Driver_Name (from JOIN with Driver table)
        
    Response format:
        {
            "success": true,
            "data": [
                {
                    "vehicle_vin": "1HGBH41JXMN109186",
                    "model": "Toyota Camry",
                    "color": "Blue",
                    "registration_year": 2020,
                    "driver_id": 1,
                    "driver_name": "Jane Smith"
                },
                ...
            ]
        }
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: SELECT all vehicles with driver information
        # Uses LEFT JOIN to include vehicles even if they don't have an assigned driver
        # The LEFT JOIN ensures vehicles with NULL Driver_ID are still returned
        # Returns vehicle details along with the driver's name for better readability
        query = """
            SELECT 
                v.Vehicle_VIN,
                v.Model,
                v.Color,
                v.Registration_Year,
                v.Driver_ID,
                d.Driver_Name
            FROM Vehicle v
            LEFT JOIN Driver d ON v.Driver_ID = d.Driver_ID
            ORDER BY v.Vehicle_VIN
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert database rows to list of dictionaries for JSON response
        vehicles = []
        for row in rows:
            vehicles.append({
                "vehicle_vin": row[0],
                "model": row[1],
                "color": row[2],
                "registration_year": row[3],
                "driver_id": row[4],
                "driver_name": row[5] if row[5] else None
            })
        
        return jsonify({
            "success": True,
            "data": vehicles
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/vehicles/<string:vin>', methods=['GET'])
def get_vehicle(vin):
    """
    Retrieve a single vehicle by VIN with driver information.
    
    Args:
        vin: The VIN (Vehicle Identification Number) of the vehicle to retrieve
        
    Returns:
        JSON response with vehicle details including driver information or error if not found
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: SELECT single vehicle by Vehicle_VIN with driver information
        # Uses LEFT JOIN to include driver details if assigned
        # Uses parameterized query to prevent SQL injection
        query = """
            SELECT 
                v.Vehicle_VIN,
                v.Model,
                v.Color,
                v.Registration_Year,
                v.Driver_ID,
                d.Driver_Name
            FROM Vehicle v
            LEFT JOIN Driver d ON v.Driver_ID = d.Driver_ID
            WHERE v.Vehicle_VIN = :vin
        """
        
        cursor.execute(query, {"vin": vin})
        row = cursor.fetchone()
        
        if row is None:
            return jsonify({
                "success": False,
                "error": f"Vehicle with VIN {vin} not found"
            }), 404
        
        vehicle = {
            "vehicle_vin": row[0],
            "model": row[1],
            "color": row[2],
            "registration_year": row[3],
            "driver_id": row[4],
            "driver_name": row[5] if row[5] else None
        }
        
        return jsonify({
            "success": True,
            "data": vehicle
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/vehicles', methods=['POST'])
def create_vehicle():
    """
    Create a new vehicle record.
    
    Expected JSON body:
        {
            "vehicle_vin": "1HGBH41JXMN109186",
            "model": "Toyota Camry",
            "color": "Blue",
            "registration_year": 2020,
            "driver_id": 1
        }
        
    Returns:
        JSON response with created vehicle data
        
    Note:
        The driver_id must reference an existing driver in the Driver table.
        If an invalid driver_id is provided, the operation will fail due to
        foreign key constraint.
    """
    conn = None
    cursor = None
    
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['vehicle_vin', 'model', 'color', 'registration_year', 'driver_id']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None or data[field] == '']
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate registration year is a valid number
        try:
            registration_year = int(data['registration_year'])
            if registration_year < 1900 or registration_year > 2100:
                return jsonify({
                    "success": False,
                    "error": "Registration year must be between 1900 and 2100"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Registration year must be a valid number"
            }), 400
        
        # Validate driver_id is a valid number
        try:
            driver_id = int(data['driver_id'])
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Driver ID must be a valid number"
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Validate that the driver exists before creating the vehicle
        # This provides a more user-friendly error message than a foreign key constraint violation
        driver_check_query = "SELECT Driver_ID FROM Driver WHERE Driver_ID = :driver_id"
        cursor.execute(driver_check_query, {"driver_id": driver_id})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Driver with ID {driver_id} does not exist. Please select a valid driver."
            }), 400
        
        # SQL Query: INSERT new vehicle into Vehicle table
        # The Driver_ID is a foreign key referencing the Driver table
        # This ensures referential integrity - only valid drivers can be assigned to vehicles
        query = """
            INSERT INTO Vehicle (Vehicle_VIN, Model, Color, Registration_Year, Driver_ID)
            VALUES (:vehicle_vin, :model, :color, :registration_year, :driver_id)
        """
        
        cursor.execute(query, {
            "vehicle_vin": data['vehicle_vin'],
            "model": data['model'],
            "color": data['color'],
            "registration_year": registration_year,
            "driver_id": driver_id
        })
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "vehicle_vin": data['vehicle_vin'],
                "model": data['model'],
                "color": data['color'],
                "registration_year": registration_year,
                "driver_id": driver_id
            },
            "message": "Vehicle created successfully"
        }), 201
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        
        # Handle unique constraint violations (e.g., duplicate VIN)
        # or foreign key constraint violations (invalid driver_id)
        error_message = error_obj.message.lower()
        if 'unique constraint' in error_message or 'duplicate' in error_message:
            return jsonify({
                "success": False,
                "error": f"Vehicle with VIN {data.get('vehicle_vin')} already exists"
            }), 400
        elif 'foreign key' in error_message or 'integrity constraint' in error_message:
            return jsonify({
                "success": False,
                "error": f"Invalid driver ID. Driver with ID {data.get('driver_id')} does not exist."
            }), 400
        else:
            return jsonify({
                "success": False,
                "error": f"Data integrity error: {error_obj.message}"
            }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/vehicles/<string:vin>', methods=['PUT'])
def update_vehicle(vin):
    """
    Update an existing vehicle record.
    
    Args:
        vin: The VIN of the vehicle to update
        
    Expected JSON body:
        {
            "model": "Toyota Camry Updated",
            "color": "Red",
            "registration_year": 2021,
            "driver_id": 2
        }
        
    Returns:
        JSON response with updated vehicle data
        
    Note:
        The driver_id must reference an existing driver in the Driver table.
    """
    conn = None
    cursor = None
    
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['model', 'color', 'registration_year', 'driver_id']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None or data[field] == '']
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate registration year is a valid number
        try:
            registration_year = int(data['registration_year'])
            if registration_year < 1900 or registration_year > 2100:
                return jsonify({
                    "success": False,
                    "error": "Registration year must be between 1900 and 2100"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Registration year must be a valid number"
            }), 400
        
        # Validate driver_id is a valid number
        try:
            driver_id = int(data['driver_id'])
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Driver ID must be a valid number"
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if vehicle exists
        check_query = "SELECT Vehicle_VIN FROM Vehicle WHERE Vehicle_VIN = :vin"
        cursor.execute(check_query, {"vin": vin})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Vehicle with VIN {vin} not found"
            }), 404
        
        # Validate that the driver exists before updating the vehicle
        driver_check_query = "SELECT Driver_ID FROM Driver WHERE Driver_ID = :driver_id"
        cursor.execute(driver_check_query, {"driver_id": driver_id})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Driver with ID {driver_id} does not exist. Please select a valid driver."
            }), 400
        
        # SQL Query: UPDATE vehicle record in Vehicle table
        # Updates all vehicle fields based on provided data
        # Uses WHERE clause to target specific vehicle by VIN
        # The Driver_ID foreign key constraint ensures only valid drivers can be assigned
        query = """
            UPDATE Vehicle
            SET Model = :model,
                Color = :color,
                Registration_Year = :registration_year,
                Driver_ID = :driver_id
            WHERE Vehicle_VIN = :vin
        """
        
        cursor.execute(query, {
            "model": data['model'],
            "color": data['color'],
            "registration_year": registration_year,
            "driver_id": driver_id,
            "vin": vin
        })
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "vehicle_vin": vin,
                "model": data['model'],
                "color": data['color'],
                "registration_year": registration_year,
                "driver_id": driver_id
            },
            "message": "Vehicle updated successfully"
        }), 200
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        
        # Handle foreign key constraint violations (invalid driver_id)
        error_message = error_obj.message.lower()
        if 'foreign key' in error_message or 'integrity constraint' in error_message:
            return jsonify({
                "success": False,
                "error": f"Invalid driver ID. Driver with ID {data.get('driver_id')} does not exist."
            }), 400
        else:
            return jsonify({
                "success": False,
                "error": f"Data integrity error: {error_obj.message}"
            }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/vehicles/<string:vin>', methods=['DELETE'])
def delete_vehicle(vin):
    """
    Delete a vehicle record.
    
    Args:
        vin: The VIN of the vehicle to delete
        
    Returns:
        JSON response confirming deletion or error if vehicle has associated rides
        
    Note:
        This operation will fail if the vehicle has associated rides due to
        foreign key constraints. The error message will inform the user about
        the constraint violation and suggest deleting associated rides first.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if vehicle exists
        check_query = "SELECT Vehicle_VIN FROM Vehicle WHERE Vehicle_VIN = :vin"
        cursor.execute(check_query, {"vin": vin})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Vehicle with VIN {vin} not found"
            }), 404
        
        # SQL Query: DELETE vehicle from Vehicle table
        # This will fail if vehicle has associated rides due to foreign key constraint
        # The foreign key constraint in the Ride table (Vehicle_VIN references Vehicle)
        # ensures referential integrity and prevents orphaned ride records
        query = """
            DELETE FROM Vehicle
            WHERE Vehicle_VIN = :vin
        """
        
        cursor.execute(query, {"vin": vin})
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Vehicle with VIN {vin} deleted successfully"
        }), 200
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        
        # Handle foreign key constraint violation
        # This occurs when trying to delete a vehicle with existing rides
        return jsonify({
            "success": False,
            "error": "Cannot delete vehicle with existing rides. Please delete associated rides first.",
            "details": error_obj.message
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============================================================================
# LOCATION API ENDPOINTS
# ============================================================================

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """
    Retrieve all locations from the database.
    
    Returns:
        JSON response with list of all locations including:
        - Location_ID
        - Address
        - City
        - Postal_Code
        
    Response format:
        {
            "success": true,
            "data": [
                {
                    "location_id": 1,
                    "address": "123 Main St",
                    "city": "Springfield",
                    "postal_code": "12345"
                },
                ...
            ]
        }
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: SELECT all locations from Location table
        # Returns all location records ordered by Location_ID for consistent display
        query = """
            SELECT Location_ID, Address, City, Postal_Code
            FROM Location
            ORDER BY Location_ID
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert database rows to list of dictionaries for JSON response
        locations = []
        for row in rows:
            locations.append({
                "location_id": row[0],
                "address": row[1],
                "city": row[2],
                "postal_code": row[3]
            })
        
        return jsonify({
            "success": True,
            "data": locations
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/locations/<int:location_id>', methods=['GET'])
def get_location(location_id):
    """
    Retrieve a single location by ID.
    
    Args:
        location_id: The ID of the location to retrieve
        
    Returns:
        JSON response with location details or error if not found
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: SELECT single location by Location_ID
        # Uses parameterized query to prevent SQL injection
        query = """
            SELECT Location_ID, Address, City, Postal_Code
            FROM Location
            WHERE Location_ID = :location_id
        """
        
        cursor.execute(query, {"location_id": location_id})
        row = cursor.fetchone()
        
        if row is None:
            return jsonify({
                "success": False,
                "error": f"Location with ID {location_id} not found"
            }), 404
        
        location = {
            "location_id": row[0],
            "address": row[1],
            "city": row[2],
            "postal_code": row[3]
        }
        
        return jsonify({
            "success": True,
            "data": location
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/locations', methods=['POST'])
def create_location():
    """
    Create a new location record.
    
    Expected JSON body:
        {
            "address": "123 Main St",
            "city": "Springfield",
            "postal_code": "12345"
        }
        
    Returns:
        JSON response with created location data including generated ID
    """
    conn = None
    cursor = None
    
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['address', 'city', 'postal_code']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: INSERT new location into Location table
        # Uses RETURNING clause to get the auto-generated Location_ID
        # Assumes Location_ID is generated by a sequence or trigger
        query = """
            INSERT INTO Location (Address, City, Postal_Code)
            VALUES (:address, :city, :postal_code)
            RETURNING Location_ID INTO :location_id
        """
        
        # Variable to capture the returned Location_ID
        location_id_var = cursor.var(cx_Oracle.NUMBER)
        
        cursor.execute(query, {
            "address": data['address'],
            "city": data['city'],
            "postal_code": data['postal_code'],
            "location_id": location_id_var
        })
        
        conn.commit()
        
        # Get the generated location ID
        new_location_id = location_id_var.getvalue()[0]
        
        return jsonify({
            "success": True,
            "data": {
                "location_id": int(new_location_id),
                "address": data['address'],
                "city": data['city'],
                "postal_code": data['postal_code']
            },
            "message": "Location created successfully"
        }), 201
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        # Handle unique constraint violations if any
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Data integrity error: {error_obj.message}"
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/locations/<int:location_id>', methods=['PUT'])
def update_location(location_id):
    """
    Update an existing location record.
    
    Args:
        location_id: The ID of the location to update
        
    Expected JSON body:
        {
            "address": "456 Oak Ave",
            "city": "Springfield",
            "postal_code": "12346"
        }
        
    Returns:
        JSON response with updated location data
    """
    conn = None
    cursor = None
    
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['address', 'city', 'postal_code']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if location exists
        check_query = "SELECT Location_ID FROM Location WHERE Location_ID = :location_id"
        cursor.execute(check_query, {"location_id": location_id})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Location with ID {location_id} not found"
            }), 404
        
        # SQL Query: UPDATE location record in Location table
        # Updates all location fields based on provided data
        # Uses WHERE clause to target specific location by ID
        query = """
            UPDATE Location
            SET Address = :address,
                City = :city,
                Postal_Code = :postal_code
            WHERE Location_ID = :location_id
        """
        
        cursor.execute(query, {
            "address": data['address'],
            "city": data['city'],
            "postal_code": data['postal_code'],
            "location_id": location_id
        })
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "location_id": location_id,
                "address": data['address'],
                "city": data['city'],
                "postal_code": data['postal_code']
            },
            "message": "Location updated successfully"
        }), 200
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Data integrity error: {error_obj.message}"
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/locations/<int:location_id>', methods=['DELETE'])
def delete_location(location_id):
    """
    Delete a location record.
    
    Args:
        location_id: The ID of the location to delete
        
    Returns:
        JSON response confirming deletion or error if location has associated rides
        
    Note:
        This operation will fail if the location is used as a pickup or dropoff location
        in any rides due to foreign key constraints. The error message will inform the user
        about the constraint violation.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if location exists
        check_query = "SELECT Location_ID FROM Location WHERE Location_ID = :location_id"
        cursor.execute(check_query, {"location_id": location_id})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Location with ID {location_id} not found"
            }), 404
        
        # SQL Query: DELETE location from Location table
        # This will fail if location is referenced in Ride table as Pickup_Location or Dropoff_Location
        # The foreign key constraints ensure referential integrity between Location and Ride tables
        query = """
            DELETE FROM Location
            WHERE Location_ID = :location_id
        """
        
        cursor.execute(query, {"location_id": location_id})
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Location with ID {location_id} deleted successfully"
        }), 200
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        
        # Handle foreign key constraint violation
        # This occurs when trying to delete a location that is used in existing rides
        return jsonify({
            "success": False,
            "error": "Cannot delete location that is used in existing rides. Please delete associated rides first.",
            "details": error_obj.message
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============================================================================
# RIDE API ENDPOINTS
# ============================================================================

@app.route('/api/rides', methods=['GET'])
def get_rides():
    """
    Retrieve all rides from the database with full details from related tables.
    
    This endpoint performs complex JOINs across multiple tables to provide
    comprehensive ride information including customer, driver, vehicle, and location details.
    
    Returns:
        JSON response with list of all rides including:
        - Ride_ID
        - Customer_ID and Customer_Name
        - Driver_ID and Driver_Name
        - Vehicle_VIN and Vehicle Model
        - Pickup_Location ID and Address
        - Dropoff_Location ID and Address
        - Start_Time
        - Arrival_Time
        
    Response format:
        {
            "success": true,
            "data": [
                {
                    "ride_id": 1,
                    "customer_id": 1,
                    "customer_name": "John Doe",
                    "driver_id": 1,
                    "driver_name": "Jane Smith",
                    "vehicle_vin": "1HGBH41JXMN109186",
                    "vehicle_model": "Toyota Camry",
                    "pickup_location_id": 1,
                    "pickup_address": "123 Main St, Springfield",
                    "dropoff_location_id": 2,
                    "dropoff_address": "456 Oak Ave, Springfield",
                    "start_time": "2024-01-15T10:30:00",
                    "arrival_time": "2024-01-15T11:00:00"
                },
                ...
            ]
        }
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: SELECT all rides with comprehensive JOIN operations
        # This query demonstrates complex multi-table JOINs to retrieve related data:
        # 
        # 1. JOIN with Customer table to get customer name
        # 2. JOIN with Driver table to get driver name
        # 3. JOIN with Vehicle table to get vehicle model
        # 4. JOIN with Location table TWICE (aliased as l1 and l2) to get both
        #    pickup and dropoff location addresses
        #
        # The double JOIN on Location is necessary because each ride references
        # the Location table twice (for pickup and dropoff), requiring table aliases
        # to distinguish between the two location references.
        #
        # All JOINs use INNER JOIN to ensure we only return rides with valid
        # foreign key references (rides must have valid customer, driver, vehicle,
        # and location records).
        query = """
            SELECT 
                r.Ride_ID,
                r.Customer_ID,
                c.Customer_Name,
                r.Driver_ID,
                d.Driver_Name,
                r.Vehicle_VIN,
                v.Model as Vehicle_Model,
                r.Pickup_Location,
                l1.Address || ', ' || l1.City as Pickup_Address,
                r.Dropoff_Location,
                l2.Address || ', ' || l2.City as Dropoff_Address,
                r.Start_Time,
                r.Arrival_Time
            FROM Ride r
            INNER JOIN Customer c ON r.Customer_ID = c.Customer_ID
            INNER JOIN Driver d ON r.Driver_ID = d.Driver_ID
            INNER JOIN Vehicle v ON r.Vehicle_VIN = v.Vehicle_VIN
            INNER JOIN Location l1 ON r.Pickup_Location = l1.Location_ID
            INNER JOIN Location l2 ON r.Dropoff_Location = l2.Location_ID
            ORDER BY r.Ride_ID DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert database rows to list of dictionaries for JSON response
        rides = []
        for row in rows:
            rides.append({
                "ride_id": row[0],
                "customer_id": row[1],
                "customer_name": row[2],
                "driver_id": row[3],
                "driver_name": row[4],
                "vehicle_vin": row[5],
                "vehicle_model": row[6],
                "pickup_location_id": row[7],
                "pickup_address": row[8],
                "dropoff_location_id": row[9],
                "dropoff_address": row[10],
                "start_time": row[11].isoformat() if row[11] else None,
                "arrival_time": row[12].isoformat() if row[12] else None
            })
        
        return jsonify({
            "success": True,
            "data": rides
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/rides/<int:ride_id>', methods=['GET'])
def get_ride(ride_id):
    """
    Retrieve a single ride by ID with full details from related tables.
    
    This endpoint performs the same complex JOINs as get_rides() but filters
    for a specific ride ID.
    
    Args:
        ride_id: The ID of the ride to retrieve
        
    Returns:
        JSON response with complete ride details or error if not found
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: SELECT single ride by Ride_ID with full JOIN details
        # Uses the same multi-table JOIN strategy as get_rides() but adds
        # a WHERE clause to filter for a specific ride.
        # 
        # The query structure:
        # - Joins Customer table for customer information
        # - Joins Driver table for driver information
        # - Joins Vehicle table for vehicle information
        # - Joins Location table twice (l1 for pickup, l2 for dropoff)
        # - Filters by Ride_ID using parameterized query for security
        query = """
            SELECT 
                r.Ride_ID,
                r.Customer_ID,
                c.Customer_Name,
                r.Driver_ID,
                d.Driver_Name,
                r.Vehicle_VIN,
                v.Model as Vehicle_Model,
                r.Pickup_Location,
                l1.Address || ', ' || l1.City as Pickup_Address,
                r.Dropoff_Location,
                l2.Address || ', ' || l2.City as Dropoff_Address,
                r.Start_Time,
                r.Arrival_Time
            FROM Ride r
            INNER JOIN Customer c ON r.Customer_ID = c.Customer_ID
            INNER JOIN Driver d ON r.Driver_ID = d.Driver_ID
            INNER JOIN Vehicle v ON r.Vehicle_VIN = v.Vehicle_VIN
            INNER JOIN Location l1 ON r.Pickup_Location = l1.Location_ID
            INNER JOIN Location l2 ON r.Dropoff_Location = l2.Location_ID
            WHERE r.Ride_ID = :ride_id
        """
        
        cursor.execute(query, {"ride_id": ride_id})
        row = cursor.fetchone()
        
        if row is None:
            return jsonify({
                "success": False,
                "error": f"Ride with ID {ride_id} not found"
            }), 404
        
        ride = {
            "ride_id": row[0],
            "customer_id": row[1],
            "customer_name": row[2],
            "driver_id": row[3],
            "driver_name": row[4],
            "vehicle_vin": row[5],
            "vehicle_model": row[6],
            "pickup_location_id": row[7],
            "pickup_address": row[8],
            "dropoff_location_id": row[9],
            "dropoff_address": row[10],
            "start_time": row[11].isoformat() if row[11] else None,
            "arrival_time": row[12].isoformat() if row[12] else None
        }
        
        return jsonify({
            "success": True,
            "data": ride
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/rides', methods=['POST'])
def create_ride():
    """
    Create a new ride record with foreign key validation.
    
    This endpoint validates that all foreign key references (customer, driver,
    vehicle, and locations) exist before creating the ride record.
    
    Expected JSON body:
        {
            "customer_id": 1,
            "driver_id": 1,
            "vehicle_vin": "1HGBH41JXMN109186",
            "pickup_location": 1,
            "dropoff_location": 2,
            "start_time": "2024-01-15T10:30:00",
            "arrival_time": "2024-01-15T11:00:00"
        }
        
    Returns:
        JSON response with created ride data including generated ID
        
    Note:
        All foreign key references are validated before insertion to provide
        clear error messages if any referenced entity doesn't exist.
    """
    conn = None
    cursor = None
    
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['customer_id', 'driver_id', 'vehicle_vin', 'pickup_location', 
                          'dropoff_location', 'start_time', 'arrival_time']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Foreign Key Validation: Verify that all referenced entities exist
        # This provides better error messages than relying on database constraint violations
        
        # Validate Customer exists
        cursor.execute("SELECT Customer_ID FROM Customer WHERE Customer_ID = :id", 
                      {"id": data['customer_id']})
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Customer with ID {data['customer_id']} does not exist"
            }), 400
        
        # Validate Driver exists
        cursor.execute("SELECT Driver_ID FROM Driver WHERE Driver_ID = :id", 
                      {"id": data['driver_id']})
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Driver with ID {data['driver_id']} does not exist"
            }), 400
        
        # Validate Vehicle exists
        cursor.execute("SELECT Vehicle_VIN FROM Vehicle WHERE Vehicle_VIN = :vin", 
                      {"vin": data['vehicle_vin']})
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Vehicle with VIN {data['vehicle_vin']} does not exist"
            }), 400
        
        # Validate Pickup Location exists
        cursor.execute("SELECT Location_ID FROM Location WHERE Location_ID = :id", 
                      {"id": data['pickup_location']})
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Pickup location with ID {data['pickup_location']} does not exist"
            }), 400
        
        # Validate Dropoff Location exists
        cursor.execute("SELECT Location_ID FROM Location WHERE Location_ID = :id", 
                      {"id": data['dropoff_location']})
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Dropoff location with ID {data['dropoff_location']} does not exist"
            }), 400
        
        # SQL Query: INSERT new ride into Ride table
        # Uses RETURNING clause to get the auto-generated Ride_ID
        # All foreign keys have been validated above to ensure referential integrity
        # 
        # The TO_TIMESTAMP function converts ISO 8601 datetime strings to Oracle TIMESTAMP
        # Format: 'YYYY-MM-DD"T"HH24:MI:SS' matches the expected input format
        query = """
            INSERT INTO Ride (Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, 
                            Dropoff_Location, Start_Time, Arrival_Time)
            VALUES (:customer_id, :driver_id, :vehicle_vin, :pickup_location, 
                   :dropoff_location, 
                   TO_TIMESTAMP(:start_time, 'YYYY-MM-DD"T"HH24:MI:SS'),
                   TO_TIMESTAMP(:arrival_time, 'YYYY-MM-DD"T"HH24:MI:SS'))
            RETURNING Ride_ID INTO :ride_id
        """
        
        # Variable to capture the returned Ride_ID
        ride_id_var = cursor.var(cx_Oracle.NUMBER)
        
        cursor.execute(query, {
            "customer_id": data['customer_id'],
            "driver_id": data['driver_id'],
            "vehicle_vin": data['vehicle_vin'],
            "pickup_location": data['pickup_location'],
            "dropoff_location": data['dropoff_location'],
            "start_time": data['start_time'],
            "arrival_time": data['arrival_time'],
            "ride_id": ride_id_var
        })
        
        conn.commit()
        
        # Get the generated ride ID
        new_ride_id = ride_id_var.getvalue()[0]
        
        return jsonify({
            "success": True,
            "data": {
                "ride_id": int(new_ride_id),
                "customer_id": data['customer_id'],
                "driver_id": data['driver_id'],
                "vehicle_vin": data['vehicle_vin'],
                "pickup_location": data['pickup_location'],
                "dropoff_location": data['dropoff_location'],
                "start_time": data['start_time'],
                "arrival_time": data['arrival_time']
            },
            "message": "Ride created successfully"
        }), 201
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Data integrity error: {error_obj.message}"
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/rides/<int:ride_id>', methods=['PUT'])
def update_ride(ride_id):
    """
    Update an existing ride record with foreign key validation.
    
    Args:
        ride_id: The ID of the ride to update
        
    Expected JSON body:
        {
            "customer_id": 1,
            "driver_id": 1,
            "vehicle_vin": "1HGBH41JXMN109186",
            "pickup_location": 1,
            "dropoff_location": 2,
            "start_time": "2024-01-15T10:30:00",
            "arrival_time": "2024-01-15T11:00:00"
        }
        
    Returns:
        JSON response with updated ride data
        
    Note:
        All foreign key references are validated before update to provide
        clear error messages if any referenced entity doesn't exist.
    """
    conn = None
    cursor = None
    
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['customer_id', 'driver_id', 'vehicle_vin', 'pickup_location', 
                          'dropoff_location', 'start_time', 'arrival_time']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if ride exists
        cursor.execute("SELECT Ride_ID FROM Ride WHERE Ride_ID = :ride_id", 
                      {"ride_id": ride_id})
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Ride with ID {ride_id} not found"
            }), 404
        
        # Foreign Key Validation: Verify that all referenced entities exist
        
        # Validate Customer exists
        cursor.execute("SELECT Customer_ID FROM Customer WHERE Customer_ID = :id", 
                      {"id": data['customer_id']})
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Customer with ID {data['customer_id']} does not exist"
            }), 400
        
        # Validate Driver exists
        cursor.execute("SELECT Driver_ID FROM Driver WHERE Driver_ID = :id", 
                      {"id": data['driver_id']})
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Driver with ID {data['driver_id']} does not exist"
            }), 400
        
        # Validate Vehicle exists
        cursor.execute("SELECT Vehicle_VIN FROM Vehicle WHERE Vehicle_VIN = :vin", 
                      {"vin": data['vehicle_vin']})
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Vehicle with VIN {data['vehicle_vin']} does not exist"
            }), 400
        
        # Validate Pickup Location exists
        cursor.execute("SELECT Location_ID FROM Location WHERE Location_ID = :id", 
                      {"id": data['pickup_location']})
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Pickup location with ID {data['pickup_location']} does not exist"
            }), 400
        
        # Validate Dropoff Location exists
        cursor.execute("SELECT Location_ID FROM Location WHERE Location_ID = :id", 
                      {"id": data['dropoff_location']})
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Dropoff location with ID {data['dropoff_location']} does not exist"
            }), 400
        
        # SQL Query: UPDATE ride record in Ride table
        # Updates all ride fields based on provided data
        # Uses WHERE clause to target specific ride by ID
        # All foreign keys have been validated above
        # 
        # The TO_TIMESTAMP function converts ISO 8601 datetime strings to Oracle TIMESTAMP
        query = """
            UPDATE Ride
            SET Customer_ID = :customer_id,
                Driver_ID = :driver_id,
                Vehicle_VIN = :vehicle_vin,
                Pickup_Location = :pickup_location,
                Dropoff_Location = :dropoff_location,
                Start_Time = TO_TIMESTAMP(:start_time, 'YYYY-MM-DD"T"HH24:MI:SS'),
                Arrival_Time = TO_TIMESTAMP(:arrival_time, 'YYYY-MM-DD"T"HH24:MI:SS')
            WHERE Ride_ID = :ride_id
        """
        
        cursor.execute(query, {
            "customer_id": data['customer_id'],
            "driver_id": data['driver_id'],
            "vehicle_vin": data['vehicle_vin'],
            "pickup_location": data['pickup_location'],
            "dropoff_location": data['dropoff_location'],
            "start_time": data['start_time'],
            "arrival_time": data['arrival_time'],
            "ride_id": ride_id
        })
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "ride_id": ride_id,
                "customer_id": data['customer_id'],
                "driver_id": data['driver_id'],
                "vehicle_vin": data['vehicle_vin'],
                "pickup_location": data['pickup_location'],
                "dropoff_location": data['dropoff_location'],
                "start_time": data['start_time'],
                "arrival_time": data['arrival_time']
            },
            "message": "Ride updated successfully"
        }), 200
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Data integrity error: {error_obj.message}"
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/rides/<int:ride_id>', methods=['DELETE'])
def delete_ride(ride_id):
    """
    Delete a ride record.
    
    Args:
        ride_id: The ID of the ride to delete
        
    Returns:
        JSON response confirming deletion or error if ride has associated payments or ratings
        
    Note:
        This operation may fail if the ride has associated payments or ratings due to
        foreign key constraints. The error message will inform the user about
        the constraint violation.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if ride exists
        cursor.execute("SELECT Ride_ID FROM Ride WHERE Ride_ID = :ride_id", 
                      {"ride_id": ride_id})
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Ride with ID {ride_id} not found"
            }), 404
        
        # SQL Query: DELETE ride from Ride table
        # This may fail if ride has associated payments or ratings due to foreign key constraints
        # The foreign key constraints ensure referential integrity between Ride, Payment, and Rating tables
        query = """
            DELETE FROM Ride
            WHERE Ride_ID = :ride_id
        """
        
        cursor.execute(query, {"ride_id": ride_id})
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Ride with ID {ride_id} deleted successfully"
        }), 200
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        
        # Handle foreign key constraint violation
        # This occurs when trying to delete a ride with existing payments or ratings
        return jsonify({
            "success": False,
            "error": "Cannot delete ride with existing payments or ratings. Please delete associated records first.",
            "details": error_obj.message
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============================================================================
# PAYMENT API ENDPOINTS
# ============================================================================

@app.route('/api/payments', methods=['GET'])
def get_payments():
    """
    Retrieve all payments from the database with ride information.
    
    Returns:
        JSON response with list of all payments including:
        - Transaction_ID
        - Ride_ID
        - Amount
        - Payment_Method
        - Payment_Status
        - Payment_Date
        - Ride details (Customer name, Driver name, etc.)
        
    Response format:
        {
            "success": true,
            "data": [
                {
                    "transaction_id": 1,
                    "ride_id": 1,
                    "amount": 25.50,
                    "payment_method": "Credit Card",
                    "payment_status": "Completed",
                    "payment_date": "2024-01-15",
                    "customer_name": "John Doe",
                    "driver_name": "Jane Smith"
                },
                ...
            ]
        }
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: SELECT all payments with JOIN to Ride table and related entities
        # This query joins Payment with Ride, Customer, and Driver tables to provide
        # comprehensive payment information including customer and driver names
        # The LEFT JOIN ensures we get all payments even if some ride data is missing
        query = """
            SELECT 
                p.Transaction_ID,
                p.Ride_ID,
                p.Amount,
                p.Payment_Method,
                p.Payment_Status,
                p.Payment_Date,
                c.Customer_Name,
                d.Driver_Name
            FROM Payment p
            LEFT JOIN Ride r ON p.Ride_ID = r.Ride_ID
            LEFT JOIN Customer c ON r.Customer_ID = c.Customer_ID
            LEFT JOIN Driver d ON r.Driver_ID = d.Driver_ID
            ORDER BY p.Transaction_ID
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert database rows to list of dictionaries for JSON response
        payments = []
        for row in rows:
            payments.append({
                "transaction_id": row[0],
                "ride_id": row[1],
                "amount": float(row[2]) if row[2] is not None else None,
                "payment_method": row[3],
                "payment_status": row[4],
                "payment_date": row[5].strftime('%Y-%m-%d') if row[5] else None,
                "customer_name": row[6],
                "driver_name": row[7]
            })
        
        return jsonify({
            "success": True,
            "data": payments
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/payments/<int:transaction_id>', methods=['GET'])
def get_payment(transaction_id):
    """
    Retrieve a single payment by Transaction ID.
    
    Args:
        transaction_id: The Transaction ID of the payment to retrieve
        
    Returns:
        JSON response with payment details including ride information or error if not found
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: SELECT single payment by Transaction_ID with ride details
        # Uses parameterized query to prevent SQL injection
        # Joins with Ride, Customer, and Driver tables for complete context
        query = """
            SELECT 
                p.Transaction_ID,
                p.Ride_ID,
                p.Amount,
                p.Payment_Method,
                p.Payment_Status,
                p.Payment_Date,
                c.Customer_Name,
                d.Driver_Name
            FROM Payment p
            LEFT JOIN Ride r ON p.Ride_ID = r.Ride_ID
            LEFT JOIN Customer c ON r.Customer_ID = c.Customer_ID
            LEFT JOIN Driver d ON r.Driver_ID = d.Driver_ID
            WHERE p.Transaction_ID = :transaction_id
        """
        
        cursor.execute(query, {"transaction_id": transaction_id})
        row = cursor.fetchone()
        
        if row is None:
            return jsonify({
                "success": False,
                "error": f"Payment with Transaction ID {transaction_id} not found"
            }), 404
        
        payment = {
            "transaction_id": row[0],
            "ride_id": row[1],
            "amount": float(row[2]) if row[2] is not None else None,
            "payment_method": row[3],
            "payment_status": row[4],
            "payment_date": row[5].strftime('%Y-%m-%d') if row[5] else None,
            "customer_name": row[6],
            "driver_name": row[7]
        }
        
        return jsonify({
            "success": True,
            "data": payment
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/payments', methods=['POST'])
def create_payment():
    """
    Create a new payment record.
    
    Expected JSON body:
        {
            "ride_id": 1,
            "amount": 25.50,
            "payment_method": "Credit Card",
            "payment_status": "Completed",
            "payment_date": "2024-01-15"
        }
        
    Returns:
        JSON response with created payment data including generated Transaction ID
        
    Note:
        The ride_id must reference an existing ride in the Ride table.
        Foreign key validation ensures referential integrity.
    """
    conn = None
    cursor = None
    
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['ride_id', 'amount', 'payment_method', 'payment_status', 'payment_date']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None or data[field] == '']
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate amount is a positive number
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({
                    "success": False,
                    "error": "Amount must be a positive number"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Invalid amount format"
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Validate that the ride exists
        # This ensures foreign key integrity before attempting the insert
        ride_check_query = "SELECT Ride_ID FROM Ride WHERE Ride_ID = :ride_id"
        cursor.execute(ride_check_query, {"ride_id": data['ride_id']})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Ride with ID {data['ride_id']} does not exist"
            }), 400
        
        # SQL Query: INSERT new payment into Payment table
        # Uses RETURNING clause to get the auto-generated Transaction_ID
        # The Ride_ID foreign key ensures the payment is linked to a valid ride
        query = """
            INSERT INTO Payment (Ride_ID, Amount, Payment_Method, Payment_Status, Payment_Date)
            VALUES (:ride_id, :amount, :payment_method, :payment_status, TO_DATE(:payment_date, 'YYYY-MM-DD'))
            RETURNING Transaction_ID INTO :transaction_id
        """
        
        # Variable to capture the returned Transaction_ID
        transaction_id_var = cursor.var(cx_Oracle.NUMBER)
        
        cursor.execute(query, {
            "ride_id": data['ride_id'],
            "amount": amount,
            "payment_method": data['payment_method'],
            "payment_status": data['payment_status'],
            "payment_date": data['payment_date'],
            "transaction_id": transaction_id_var
        })
        
        conn.commit()
        
        # Get the generated transaction ID
        new_transaction_id = transaction_id_var.getvalue()[0]
        
        return jsonify({
            "success": True,
            "data": {
                "transaction_id": int(new_transaction_id),
                "ride_id": data['ride_id'],
                "amount": amount,
                "payment_method": data['payment_method'],
                "payment_status": data['payment_status'],
                "payment_date": data['payment_date']
            },
            "message": "Payment created successfully"
        }), 201
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Data integrity error: {error_obj.message}"
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/payments/<int:transaction_id>', methods=['PUT'])
def update_payment(transaction_id):
    """
    Update an existing payment record.
    
    Args:
        transaction_id: The Transaction ID of the payment to update
        
    Expected JSON body:
        {
            "ride_id": 1,
            "amount": 30.00,
            "payment_method": "Cash",
            "payment_status": "Completed",
            "payment_date": "2024-01-16"
        }
        
    Returns:
        JSON response with updated payment data
    """
    conn = None
    cursor = None
    
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['ride_id', 'amount', 'payment_method', 'payment_status', 'payment_date']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None or data[field] == '']
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate amount is a positive number
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({
                    "success": False,
                    "error": "Amount must be a positive number"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Invalid amount format"
            }), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if payment exists
        check_query = "SELECT Transaction_ID FROM Payment WHERE Transaction_ID = :transaction_id"
        cursor.execute(check_query, {"transaction_id": transaction_id})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Payment with Transaction ID {transaction_id} not found"
            }), 404
        
        # Validate that the ride exists
        # This ensures foreign key integrity before attempting the update
        ride_check_query = "SELECT Ride_ID FROM Ride WHERE Ride_ID = :ride_id"
        cursor.execute(ride_check_query, {"ride_id": data['ride_id']})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Ride with ID {data['ride_id']} does not exist"
            }), 400
        
        # SQL Query: UPDATE payment record in Payment table
        # Updates all payment fields based on provided data
        # Uses WHERE clause to target specific payment by Transaction_ID
        # The Ride_ID foreign key ensures the payment remains linked to a valid ride
        query = """
            UPDATE Payment
            SET Ride_ID = :ride_id,
                Amount = :amount,
                Payment_Method = :payment_method,
                Payment_Status = :payment_status,
                Payment_Date = TO_DATE(:payment_date, 'YYYY-MM-DD')
            WHERE Transaction_ID = :transaction_id
        """
        
        cursor.execute(query, {
            "ride_id": data['ride_id'],
            "amount": amount,
            "payment_method": data['payment_method'],
            "payment_status": data['payment_status'],
            "payment_date": data['payment_date'],
            "transaction_id": transaction_id
        })
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "transaction_id": transaction_id,
                "ride_id": data['ride_id'],
                "amount": amount,
                "payment_method": data['payment_method'],
                "payment_status": data['payment_status'],
                "payment_date": data['payment_date']
            },
            "message": "Payment updated successfully"
        }), 200
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Data integrity error: {error_obj.message}"
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/payments/<int:transaction_id>', methods=['DELETE'])
def delete_payment(transaction_id):
    """
    Delete a payment record.
    
    Args:
        transaction_id: The Transaction ID of the payment to delete
        
    Returns:
        JSON response confirming deletion or error if payment not found
        
    Note:
        This operation removes the payment record from the database.
        Since Payment is typically a leaf table (no other tables reference it),
        this operation should succeed if the payment exists.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if payment exists
        check_query = "SELECT Transaction_ID FROM Payment WHERE Transaction_ID = :transaction_id"
        cursor.execute(check_query, {"transaction_id": transaction_id})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Payment with Transaction ID {transaction_id} not found"
            }), 404
        
        # SQL Query: DELETE payment from Payment table
        # Removes the payment record identified by Transaction_ID
        # This operation should succeed as Payment is typically not referenced by other tables
        query = """
            DELETE FROM Payment
            WHERE Transaction_ID = :transaction_id
        """
        
        cursor.execute(query, {"transaction_id": transaction_id})
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Payment with Transaction ID {transaction_id} deleted successfully"
        }), 200
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        
        # Handle any unexpected foreign key constraint violation
        return jsonify({
            "success": False,
            "error": "Cannot delete payment due to data integrity constraints.",
            "details": error_obj.message
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============================================================================
# RATING API ENDPOINTS
# ============================================================================

@app.route('/api/ratings', methods=['GET'])
def get_ratings():
    """
    Retrieve all ratings from the database with ride information.
    
    Returns:
        JSON response with list of all ratings including:
        - Rating_ID
        - Ride_ID
        - Customer_Rating
        - Driver_Rating
        - Comments
        - Ride details (Customer name, Driver name, etc.)
        
    Response format:
        {
            "success": true,
            "data": [
                {
                    "rating_id": 1,
                    "ride_id": 1,
                    "customer_rating": 5,
                    "driver_rating": 4,
                    "comments": "Great ride!",
                    "customer_name": "John Doe",
                    "driver_name": "Jane Smith"
                },
                ...
            ]
        }
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: SELECT all ratings with JOIN to Ride table and related entities
        # This query joins Rating with Ride, Customer, and Driver tables to provide
        # comprehensive rating information including customer and driver names
        # The LEFT JOIN ensures we get all ratings even if some ride data is missing
        query = """
            SELECT 
                rt.Rating_ID,
                rt.Ride_ID,
                rt.Customer_Rating,
                rt.Driver_Rating,
                rt.Comments,
                c.Customer_Name,
                d.Driver_Name
            FROM Rating rt
            LEFT JOIN Ride r ON rt.Ride_ID = r.Ride_ID
            LEFT JOIN Customer c ON r.Customer_ID = c.Customer_ID
            LEFT JOIN Driver d ON r.Driver_ID = d.Driver_ID
            ORDER BY rt.Rating_ID
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert database rows to list of dictionaries for JSON response
        ratings = []
        for row in rows:
            ratings.append({
                "rating_id": row[0],
                "ride_id": row[1],
                "customer_rating": row[2],
                "driver_rating": row[3],
                "comments": row[4],
                "customer_name": row[5],
                "driver_name": row[6]
            })
        
        return jsonify({
            "success": True,
            "data": ratings
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/ratings/<int:rating_id>', methods=['GET'])
def get_rating(rating_id):
    """
    Retrieve a single rating by Rating ID.
    
    Args:
        rating_id: The Rating ID of the rating to retrieve
        
    Returns:
        JSON response with rating details including ride information or error if not found
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: SELECT single rating by Rating_ID with ride details
        # Uses parameterized query to prevent SQL injection
        # Joins with Ride, Customer, and Driver tables for complete context
        query = """
            SELECT 
                rt.Rating_ID,
                rt.Ride_ID,
                rt.Customer_Rating,
                rt.Driver_Rating,
                rt.Comments,
                c.Customer_Name,
                d.Driver_Name
            FROM Rating rt
            LEFT JOIN Ride r ON rt.Ride_ID = r.Ride_ID
            LEFT JOIN Customer c ON r.Customer_ID = c.Customer_ID
            LEFT JOIN Driver d ON r.Driver_ID = d.Driver_ID
            WHERE rt.Rating_ID = :rating_id
        """
        
        cursor.execute(query, {"rating_id": rating_id})
        row = cursor.fetchone()
        
        if row is None:
            return jsonify({
                "success": False,
                "error": f"Rating with ID {rating_id} not found"
            }), 404
        
        rating = {
            "rating_id": row[0],
            "ride_id": row[1],
            "customer_rating": row[2],
            "driver_rating": row[3],
            "comments": row[4],
            "customer_name": row[5],
            "driver_name": row[6]
        }
        
        return jsonify({
            "success": True,
            "data": rating
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/ratings', methods=['POST'])
def create_rating():
    """
    Create a new rating record.
    
    Expected JSON body:
        {
            "ride_id": 1,
            "customer_rating": 5,
            "driver_rating": 4,
            "comments": "Great ride!"
        }
        
    Returns:
        JSON response with created rating data including generated Rating ID
        
    Note:
        The ride_id must reference an existing ride in the Ride table.
        Foreign key validation ensures referential integrity.
        Customer_rating and driver_rating should be between 1 and 5.
    """
    conn = None
    cursor = None
    
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields (comments is optional)
        required_fields = ['ride_id', 'customer_rating', 'driver_rating']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None or data[field] == '']
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate rating values are between 1 and 5
        try:
            customer_rating = int(data['customer_rating'])
            driver_rating = int(data['driver_rating'])
            
            if not (1 <= customer_rating <= 5):
                return jsonify({
                    "success": False,
                    "error": "Customer rating must be between 1 and 5"
                }), 400
            
            if not (1 <= driver_rating <= 5):
                return jsonify({
                    "success": False,
                    "error": "Driver rating must be between 1 and 5"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Invalid rating format. Ratings must be integers."
            }), 400
        
        # Comments is optional, default to empty string if not provided
        comments = data.get('comments', '')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Validate that the ride exists
        # This ensures foreign key integrity before attempting the insert
        ride_check_query = "SELECT Ride_ID FROM Ride WHERE Ride_ID = :ride_id"
        cursor.execute(ride_check_query, {"ride_id": data['ride_id']})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Ride with ID {data['ride_id']} does not exist"
            }), 400
        
        # SQL Query: INSERT new rating into Rating table
        # Uses RETURNING clause to get the auto-generated Rating_ID
        # The Ride_ID foreign key ensures the rating is linked to a valid ride
        query = """
            INSERT INTO Rating (Ride_ID, Customer_Rating, Driver_Rating, Comments)
            VALUES (:ride_id, :customer_rating, :driver_rating, :comments)
            RETURNING Rating_ID INTO :rating_id
        """
        
        # Variable to capture the returned Rating_ID
        rating_id_var = cursor.var(cx_Oracle.NUMBER)
        
        cursor.execute(query, {
            "ride_id": data['ride_id'],
            "customer_rating": customer_rating,
            "driver_rating": driver_rating,
            "comments": comments,
            "rating_id": rating_id_var
        })
        
        conn.commit()
        
        # Get the generated rating ID
        new_rating_id = rating_id_var.getvalue()[0]
        
        return jsonify({
            "success": True,
            "data": {
                "rating_id": int(new_rating_id),
                "ride_id": data['ride_id'],
                "customer_rating": customer_rating,
                "driver_rating": driver_rating,
                "comments": comments
            },
            "message": "Rating created successfully"
        }), 201
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Data integrity error: {error_obj.message}"
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/ratings/<int:rating_id>', methods=['PUT'])
def update_rating(rating_id):
    """
    Update an existing rating record.
    
    Args:
        rating_id: The Rating ID of the rating to update
        
    Expected JSON body:
        {
            "ride_id": 1,
            "customer_rating": 5,
            "driver_rating": 5,
            "comments": "Excellent service!"
        }
        
    Returns:
        JSON response with updated rating data
    """
    conn = None
    cursor = None
    
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields (comments is optional)
        required_fields = ['ride_id', 'customer_rating', 'driver_rating']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None or data[field] == '']
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate rating values are between 1 and 5
        try:
            customer_rating = int(data['customer_rating'])
            driver_rating = int(data['driver_rating'])
            
            if not (1 <= customer_rating <= 5):
                return jsonify({
                    "success": False,
                    "error": "Customer rating must be between 1 and 5"
                }), 400
            
            if not (1 <= driver_rating <= 5):
                return jsonify({
                    "success": False,
                    "error": "Driver rating must be between 1 and 5"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Invalid rating format. Ratings must be integers."
            }), 400
        
        # Comments is optional, default to empty string if not provided
        comments = data.get('comments', '')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if rating exists
        check_query = "SELECT Rating_ID FROM Rating WHERE Rating_ID = :rating_id"
        cursor.execute(check_query, {"rating_id": rating_id})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Rating with ID {rating_id} not found"
            }), 404
        
        # Validate that the ride exists
        # This ensures foreign key integrity before attempting the update
        ride_check_query = "SELECT Ride_ID FROM Ride WHERE Ride_ID = :ride_id"
        cursor.execute(ride_check_query, {"ride_id": data['ride_id']})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Ride with ID {data['ride_id']} does not exist"
            }), 400
        
        # SQL Query: UPDATE rating record in Rating table
        # Updates all rating fields based on provided data
        # Uses WHERE clause to target specific rating by Rating_ID
        # The Ride_ID foreign key ensures the rating remains linked to a valid ride
        query = """
            UPDATE Rating
            SET Ride_ID = :ride_id,
                Customer_Rating = :customer_rating,
                Driver_Rating = :driver_rating,
                Comments = :comments
            WHERE Rating_ID = :rating_id
        """
        
        cursor.execute(query, {
            "ride_id": data['ride_id'],
            "customer_rating": customer_rating,
            "driver_rating": driver_rating,
            "comments": comments,
            "rating_id": rating_id
        })
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "rating_id": rating_id,
                "ride_id": data['ride_id'],
                "customer_rating": customer_rating,
                "driver_rating": driver_rating,
                "comments": comments
            },
            "message": "Rating updated successfully"
        }), 200
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Data integrity error: {error_obj.message}"
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/ratings/<int:rating_id>', methods=['DELETE'])
def delete_rating(rating_id):
    """
    Delete a rating record.
    
    Args:
        rating_id: The Rating ID of the rating to delete
        
    Returns:
        JSON response confirming deletion or error if rating not found
        
    Note:
        This operation removes the rating record from the database.
        Since Rating is typically a leaf table (no other tables reference it),
        this operation should succeed if the rating exists.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if rating exists
        check_query = "SELECT Rating_ID FROM Rating WHERE Rating_ID = :rating_id"
        cursor.execute(check_query, {"rating_id": rating_id})
        
        if cursor.fetchone() is None:
            return jsonify({
                "success": False,
                "error": f"Rating with ID {rating_id} not found"
            }), 404
        
        # SQL Query: DELETE rating from Rating table
        # Removes the rating record identified by Rating_ID
        # This operation should succeed as Rating is typically not referenced by other tables
        query = """
            DELETE FROM Rating
            WHERE Rating_ID = :rating_id
        """
        
        cursor.execute(query, {"rating_id": rating_id})
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Rating with ID {rating_id} deleted successfully"
        }), 200
        
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        
        # Handle any unexpected foreign key constraint violation
        return jsonify({
            "success": False,
            "error": "Cannot delete rating due to data integrity constraints.",
            "details": error_obj.message
        }), 400
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Error handler for 404 Not Found
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with JSON response"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

# Error handler for 500 Internal Server Error
@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with JSON response"""
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

# ============================================================================
# REPORT API ENDPOINTS
# ============================================================================

@app.route('/api/reports/top-drivers', methods=['GET'])
def get_top_drivers():
    """
    Generate report of top drivers by ride count.
    
    This report uses GROUP BY to aggregate rides per driver and COUNT to calculate
    the total number of rides each driver has completed. It includes drivers with
    zero rides using LEFT JOIN.
    
    Returns:
        JSON response with list of drivers sorted by ride count (descending):
        - driver_id: The unique identifier for the driver
        - driver_name: The name of the driver
        - ride_count: Total number of rides completed by this driver
        
    Response format:
        {
            "success": true,
            "data": [
                {
                    "driver_id": 1,
                    "driver_name": "Jane Smith",
                    "ride_count": 15
                },
                ...
            ]
        }
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: Top Drivers by Ride Count
        # - Uses LEFT JOIN to include drivers even if they have no rides
        # - GROUP BY aggregates rides per driver (Driver_ID and Driver_Name must be in GROUP BY)
        # - COUNT(r.Ride_ID) counts the number of rides for each driver
        #   (using r.Ride_ID instead of * ensures NULL values from LEFT JOIN are not counted)
        # - ORDER BY Ride_Count DESC sorts drivers with most rides first
        query = """
            SELECT 
                d.Driver_ID,
                d.Driver_Name,
                COUNT(r.Ride_ID) as Ride_Count
            FROM Driver d
            LEFT JOIN Ride r ON d.Driver_ID = r.Driver_ID
            GROUP BY d.Driver_ID, d.Driver_Name
            ORDER BY Ride_Count DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert database rows to list of dictionaries for JSON response
        top_drivers = []
        for row in rows:
            top_drivers.append({
                "driver_id": row[0],
                "driver_name": row[1],
                "ride_count": row[2]
            })
        
        return jsonify({
            "success": True,
            "data": top_drivers
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/reports/revenue-by-method', methods=['GET'])
def get_revenue_by_method():
    """
    Generate report of total revenue grouped by payment method.
    
    This report uses GROUP BY to aggregate payments by payment method and SUM to
    calculate total revenue for each method. It also includes transaction count.
    
    Returns:
        JSON response with revenue breakdown by payment method:
        - payment_method: The payment method (e.g., 'Credit Card', 'Cash', 'Debit Card')
        - total_revenue: Sum of all payment amounts for this method
        - transaction_count: Number of transactions using this method
        
    Response format:
        {
            "success": true,
            "data": [
                {
                    "payment_method": "Credit Card",
                    "total_revenue": 1250.50,
                    "transaction_count": 25
                },
                ...
            ]
        }
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: Revenue by Payment Method
        # - GROUP BY Payment_Method aggregates all payments by their payment method
        # - SUM(Amount) calculates the total revenue for each payment method
        # - COUNT(*) counts the number of transactions for each payment method
        # - ORDER BY Total_Revenue DESC shows highest revenue methods first
        # Note: This query only includes payment methods that have at least one transaction
        query = """
            SELECT 
                Payment_Method,
                SUM(Amount) as Total_Revenue,
                COUNT(*) as Transaction_Count
            FROM Payment
            GROUP BY Payment_Method
            ORDER BY Total_Revenue DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert database rows to list of dictionaries for JSON response
        revenue_by_method = []
        for row in rows:
            revenue_by_method.append({
                "payment_method": row[0],
                "total_revenue": float(row[1]) if row[1] is not None else 0.0,
                "transaction_count": row[2]
            })
        
        return jsonify({
            "success": True,
            "data": revenue_by_method
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/reports/average-ratings', methods=['GET'])
def get_average_ratings():
    """
    Generate report of average driver ratings.
    
    This report uses multiple JOINs to connect Driver, Ride, and Rating tables,
    then calculates the average driver rating for each driver using AVG aggregate.
    
    Returns:
        JSON response with average ratings per driver:
        - driver_id: The unique identifier for the driver
        - driver_name: The name of the driver
        - avg_rating: Average of all driver ratings (1-5 scale)
        - rating_count: Number of ratings received
        
    Response format:
        {
            "success": true,
            "data": [
                {
                    "driver_id": 1,
                    "driver_name": "Jane Smith",
                    "avg_rating": 4.5,
                    "rating_count": 10
                },
                ...
            ]
        }
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: Average Rating by Driver
        # - First LEFT JOIN connects Driver to Ride (to get all rides for each driver)
        # - Second LEFT JOIN connects Ride to Rating (to get ratings for each ride)
        # - WHERE clause filters to only include rides that have ratings with non-NULL Driver_Rating
        # - AVG(rt.Driver_Rating) calculates the average rating across all rated rides
        # - COUNT(rt.Rating_ID) counts how many ratings each driver has received
        # - GROUP BY aggregates by driver (Driver_ID and Driver_Name)
        # - ORDER BY Avg_Rating DESC shows highest-rated drivers first
        # Note: Drivers without any ratings will not appear in this report due to WHERE clause
        query = """
            SELECT 
                d.Driver_ID,
                d.Driver_Name,
                AVG(rt.Driver_Rating) as Avg_Rating,
                COUNT(rt.Rating_ID) as Rating_Count
            FROM Driver d
            LEFT JOIN Ride r ON d.Driver_ID = r.Driver_ID
            LEFT JOIN Rating rt ON r.Ride_ID = rt.Ride_ID
            WHERE rt.Driver_Rating IS NOT NULL
            GROUP BY d.Driver_ID, d.Driver_Name
            ORDER BY Avg_Rating DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert database rows to list of dictionaries for JSON response
        average_ratings = []
        for row in rows:
            average_ratings.append({
                "driver_id": row[0],
                "driver_name": row[1],
                "avg_rating": round(float(row[2]), 2) if row[2] is not None else None,
                "rating_count": row[3]
            })
        
        return jsonify({
            "success": True,
            "data": average_ratings
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/reports/rides-by-location', methods=['GET'])
def get_rides_by_location():
    """
    Generate report of ride counts by location (both pickup and dropoff).
    
    This report uses complex JOINs to count how many times each location has been
    used as a pickup location and as a dropoff location separately.
    
    Returns:
        JSON response with location usage statistics:
        - location_id: The unique identifier for the location
        - address: The street address of the location
        - city: The city where the location is
        - pickup_count: Number of times used as pickup location
        - dropoff_count: Number of times used as dropoff location
        - total_count: Combined pickup and dropoff count
        
    Response format:
        {
            "success": true,
            "data": [
                {
                    "location_id": 1,
                    "address": "123 Main St",
                    "city": "Springfield",
                    "pickup_count": 15,
                    "dropoff_count": 12,
                    "total_count": 27
                },
                ...
            ]
        }
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: Rides by Location
        # - First LEFT JOIN (r1) connects Location to Ride where Location is the Pickup_Location
        # - Second LEFT JOIN (r2) connects Location to Ride where Location is the Dropoff_Location
        # - COUNT(DISTINCT r1.Ride_ID) counts unique rides where this location was pickup
        #   (DISTINCT ensures we don't double-count if there are any data issues)
        # - COUNT(DISTINCT r2.Ride_ID) counts unique rides where this location was dropoff
        # - The two separate JOINs allow us to count pickup and dropoff independently
        # - GROUP BY aggregates by location (Location_ID, Address, City)
        # - ORDER BY total usage (pickup + dropoff) to show most popular locations first
        query = """
            SELECT 
                l.Location_ID,
                l.Address,
                l.City,
                COUNT(DISTINCT r1.Ride_ID) as Pickup_Count,
                COUNT(DISTINCT r2.Ride_ID) as Dropoff_Count,
                (COUNT(DISTINCT r1.Ride_ID) + COUNT(DISTINCT r2.Ride_ID)) as Total_Count
            FROM Location l
            LEFT JOIN Ride r1 ON l.Location_ID = r1.Pickup_Location
            LEFT JOIN Ride r2 ON l.Location_ID = r2.Dropoff_Location
            GROUP BY l.Location_ID, l.Address, l.City
            ORDER BY Total_Count DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert database rows to list of dictionaries for JSON response
        rides_by_location = []
        for row in rows:
            rides_by_location.append({
                "location_id": row[0],
                "address": row[1],
                "city": row[2],
                "pickup_count": row[3],
                "dropoff_count": row[4],
                "total_count": row[5]
            })
        
        return jsonify({
            "success": True,
            "data": rides_by_location
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/reports/customer-history/<int:customer_id>', methods=['GET'])
def get_customer_history(customer_id):
    """
    Generate detailed ride history report for a specific customer.
    
    This report uses multi-table JOINs to retrieve comprehensive information about
    all rides taken by a specific customer, including driver, vehicle, locations,
    and payment details.
    
    Args:
        customer_id: The ID of the customer whose ride history to retrieve
    
    Returns:
        JSON response with detailed ride history:
        - ride_id: The unique identifier for the ride
        - start_time: When the ride started
        - arrival_time: When the ride ended
        - driver_name: Name of the driver
        - vehicle_model: Model of the vehicle used
        - pickup_address: Full address of pickup location
        - dropoff_address: Full address of dropoff location
        - amount: Payment amount (if payment exists)
        - payment_status: Status of payment (if payment exists)
        
    Response format:
        {
            "success": true,
            "data": [
                {
                    "ride_id": 1,
                    "start_time": "2024-01-15 10:30:00",
                    "arrival_time": "2024-01-15 11:00:00",
                    "driver_name": "Jane Smith",
                    "vehicle_model": "Toyota Camry",
                    "pickup_address": "123 Main St",
                    "dropoff_address": "456 Oak Ave",
                    "amount": 25.50,
                    "payment_status": "Completed"
                },
                ...
            ]
        }
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL Query: Customer Ride History
        # This complex query joins 6 tables to provide complete ride information:
        # - Ride table is the central table containing the ride record
        # - JOIN Driver to get driver name (INNER JOIN because every ride must have a driver)
        # - JOIN Vehicle to get vehicle model (INNER JOIN because every ride must have a vehicle)
        # - JOIN Location l1 (aliased) to get pickup location address
        # - JOIN Location l2 (aliased) to get dropoff location address
        #   (Note: l1 and l2 are aliases for the same Location table, used twice for pickup and dropoff)
        # - LEFT JOIN Payment to get payment details (LEFT JOIN because payment might not exist yet)
        # - WHERE clause filters rides for the specific customer
        # - ORDER BY Start_Time DESC shows most recent rides first
        query = """
            SELECT 
                r.Ride_ID,
                r.Start_Time,
                r.Arrival_Time,
                d.Driver_Name,
                v.Model as Vehicle_Model,
                l1.Address as Pickup_Address,
                l2.Address as Dropoff_Address,
                p.Amount,
                p.Payment_Status
            FROM Ride r
            JOIN Driver d ON r.Driver_ID = d.Driver_ID
            JOIN Vehicle v ON r.Vehicle_VIN = v.Vehicle_VIN
            JOIN Location l1 ON r.Pickup_Location = l1.Location_ID
            JOIN Location l2 ON r.Dropoff_Location = l2.Location_ID
            LEFT JOIN Payment p ON r.Ride_ID = p.Ride_ID
            WHERE r.Customer_ID = :customer_id
            ORDER BY r.Start_Time DESC
        """
        
        cursor.execute(query, {"customer_id": customer_id})
        rows = cursor.fetchall()
        
        # Convert database rows to list of dictionaries for JSON response
        customer_history = []
        for row in rows:
            customer_history.append({
                "ride_id": row[0],
                "start_time": str(row[1]) if row[1] is not None else None,
                "arrival_time": str(row[2]) if row[2] is not None else None,
                "driver_name": row[3],
                "vehicle_model": row[4],
                "pickup_address": row[5],
                "dropoff_address": row[6],
                "amount": float(row[7]) if row[7] is not None else None,
                "payment_status": row[8]
            })
        
        return jsonify({
            "success": True,
            "data": customer_history,
            "customer_id": customer_id,
            "total_rides": len(customer_history)
        }), 200
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        return jsonify({
            "success": False,
            "error": f"Database error: {error_obj.message}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == '__main__':
    # Run Flask development server
    # Debug mode enabled for development (disable in production)
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
