"""
Database Seeding Script for Ride & Pickup DBMS
This script populates the Oracle database with dummy data for testing and demonstration.

Test Data Scenarios:
- 5 customers with varied contact information
- 5 drivers with different license numbers
- 5 vehicles assigned to drivers
- 10 locations covering different cities
- 15 rides showing various pickup/dropoff combinations
- 10 payments with different methods and statuses
- 8 ratings showing customer and driver feedback

Run this script after creating the database tables to populate with test data.
"""

import cx_Oracle
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

def get_connection():
    """Establish connection to Oracle database"""
    try:
        connection = cx_Oracle.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dsn=os.getenv('DB_DSN')
        )
        print("✓ Connected to Oracle database")
        return connection
    except cx_Oracle.Error as error:
        print(f"✗ Error connecting to database: {error}")
        raise

def clear_existing_data(cursor):
    """Clear existing data from all tables (in correct order due to foreign keys)"""
    print("\nClearing existing data...")
    tables = ['Rating', 'Payment', 'Ride', 'Vehicle', 'Location', 'Driver', 'Customer']
    
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  ✓ Cleared {table} table")
        except cx_Oracle.Error as error:
            print(f"  ✗ Error clearing {table}: {error}")

def seed_customers(cursor):
    """Insert dummy customer records"""
    print("\nSeeding Customers...")
    
    # Test scenario: Mix of personal and business customers with various contact methods
    customers = [
        (1, 'Alice Johnson', '416-555-0101', 'alice.johnson@email.com'),
        (2, 'Bob Smith', '416-555-0102', 'bob.smith@email.com'),
        (3, 'Carol Williams', '647-555-0103', 'carol.w@email.com'),
        (4, 'David Brown', '416-555-0104', 'david.brown@email.com'),
        (5, 'Emma Davis', '647-555-0105', 'emma.davis@email.com'),
    ]
    
    for customer in customers:
        cursor.execute("""
            INSERT INTO Customer (Customer_ID, Customer_Name, Phone_Number, Email)
            VALUES (:1, :2, :3, :4)
        """, customer)
    
    print(f"  ✓ Inserted {len(customers)} customers")

def seed_drivers(cursor):
    """Insert dummy driver records"""
    print("\nSeeding Drivers...")
    
    # Test scenario: Drivers with different license types and experience levels
    drivers = [
        (1, 'John Driver', '416-555-0201', 'DL123456'),
        (2, 'Sarah Wheeler', '647-555-0202', 'DL234567'),
        (3, 'Mike Roadster', '416-555-0203', 'DL345678'),
        (4, 'Lisa Cruise', '647-555-0204', 'DL456789'),
        (5, 'Tom Navigator', '416-555-0205', 'DL567890'),
    ]
    
    for driver in drivers:
        cursor.execute("""
            INSERT INTO Driver (Driver_ID, Driver_Name, Phone_Number, License_Number)
            VALUES (:1, :2, :3, :4)
        """, driver)
    
    print(f"  ✓ Inserted {len(drivers)} drivers")

def seed_vehicles(cursor):
    """Insert dummy vehicle records"""
    print("\nSeeding Vehicles...")
    
    # Test scenario: Different vehicle types and years, each assigned to a driver
    vehicles = [
        ('1HGCM82633A123456', 'Honda Accord', 'Silver', 2020, 1),
        ('2T1BURHE0FC123457', 'Toyota Corolla', 'Blue', 2019, 2),
        ('3VW2B7AJ8DM123458', 'Volkswagen Jetta', 'Black', 2021, 3),
        ('5FNRL6H78GB123459', 'Honda Odyssey', 'White', 2018, 4),
        ('1G1ZD5ST8LF123460', 'Chevrolet Malibu', 'Red', 2022, 5),
    ]
    
    for vehicle in vehicles:
        cursor.execute("""
            INSERT INTO Vehicle (Vehicle_VIN, Model, Color, Registration_Year, Driver_ID)
            VALUES (:1, :2, :3, :4, :5)
        """, vehicle)
    
    print(f"  ✓ Inserted {len(vehicles)} vehicles")

def seed_locations(cursor):
    """Insert dummy location records"""
    print("\nSeeding Locations...")
    
    # Test scenario: Mix of residential, commercial, and popular destinations
    locations = [
        (1, '123 King St W', 'Toronto', 'M5H 1A1'),
        (2, '456 Queen St E', 'Toronto', 'M5A 1T1'),
        (3, '789 Yonge St', 'Toronto', 'M4Y 2B2'),
        (4, '321 Bay St', 'Toronto', 'M5H 2Y4'),
        (5, '654 Bloor St W', 'Toronto', 'M6G 1K4'),
        (6, '987 Dundas St W', 'Toronto', 'M6J 1W3'),
        (7, '147 College St', 'Toronto', 'M5T 1P7'),
        (8, '258 Spadina Ave', 'Toronto', 'M5T 2C2'),
        (9, '369 Front St E', 'Toronto', 'M5A 1G1'),
        (10, '741 Harbourfront', 'Toronto', 'M5J 2R8'),
    ]
    
    for location in locations:
        cursor.execute("""
            INSERT INTO Location (Location_ID, Address, City, Postal_Code)
            VALUES (:1, :2, :3, :4)
        """, location)
    
    print(f"  ✓ Inserted {len(locations)} locations")

def seed_rides(cursor):
    """Insert dummy ride records"""
    print("\nSeeding Rides...")
    
    # Test scenario: Various ride patterns including short trips, long trips, 
    # different times of day, and multiple rides per customer/driver
    base_date = datetime(2024, 1, 15, 8, 0, 0)
    
    rides = [
        # Customer 1 (Alice) - frequent rider, 3 rides
        (1, 1, 1, '1HGCM82633A123456', 1, 3, base_date, base_date + timedelta(minutes=20)),
        (2, 1, 2, '2T1BURHE0FC123457', 3, 5, base_date + timedelta(days=2), base_date + timedelta(days=2, minutes=25)),
        (3, 1, 3, '3VW2B7AJ8DM123458', 5, 7, base_date + timedelta(days=5), base_date + timedelta(days=5, minutes=30)),
        
        # Customer 2 (Bob) - occasional rider, 2 rides
        (4, 2, 4, '5FNRL6H78GB123459', 2, 4, base_date + timedelta(days=1), base_date + timedelta(days=1, minutes=15)),
        (5, 2, 5, '1G1ZD5ST8LF123460', 4, 6, base_date + timedelta(days=4), base_date + timedelta(days=4, minutes=35)),
        
        # Customer 3 (Carol) - regular rider, 4 rides
        (6, 3, 1, '1HGCM82633A123456', 6, 8, base_date + timedelta(days=1, hours=2), base_date + timedelta(days=1, hours=2, minutes=18)),
        (7, 3, 2, '2T1BURHE0FC123457', 8, 10, base_date + timedelta(days=3), base_date + timedelta(days=3, minutes=22)),
        (8, 3, 3, '3VW2B7AJ8DM123458', 10, 1, base_date + timedelta(days=6), base_date + timedelta(days=6, minutes=28)),
        (9, 3, 4, '5FNRL6H78GB123459', 1, 9, base_date + timedelta(days=8), base_date + timedelta(days=8, minutes=40)),
        
        # Customer 4 (David) - new rider, 3 rides
        (10, 4, 5, '1G1ZD5ST8LF123460', 2, 7, base_date + timedelta(days=2, hours=3), base_date + timedelta(days=2, hours=3, minutes=25)),
        (11, 4, 1, '1HGCM82633A123456', 7, 3, base_date + timedelta(days=5, hours=1), base_date + timedelta(days=5, hours=1, minutes=20)),
        (12, 4, 2, '2T1BURHE0FC123457', 3, 9, base_date + timedelta(days=7), base_date + timedelta(days=7, minutes=32)),
        
        # Customer 5 (Emma) - occasional rider, 3 rides
        (13, 5, 3, '3VW2B7AJ8DM123458', 4, 2, base_date + timedelta(days=3, hours=4), base_date + timedelta(days=3, hours=4, minutes=15)),
        (14, 5, 4, '5FNRL6H78GB123459', 9, 5, base_date + timedelta(days=6, hours=2), base_date + timedelta(days=6, hours=2, minutes=38)),
        (15, 5, 5, '1G1ZD5ST8LF123460', 5, 10, base_date + timedelta(days=9), base_date + timedelta(days=9, minutes=45)),
    ]
    
    for ride in rides:
        cursor.execute("""
            INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, 
                            Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8)
        """, ride)
    
    print(f"  ✓ Inserted {len(rides)} rides")

def seed_payments(cursor):
    """Insert dummy payment records"""
    print("\nSeeding Payments...")
    
    # Test scenario: Different payment methods (Credit Card, Debit, Cash, Mobile Pay)
    # and statuses (Completed, Pending, Failed) to test reporting
    base_date = datetime(2024, 1, 15, 8, 30, 0)
    
    payments = [
        (1, 1, 15.50, 'Credit Card', 'Completed', base_date),
        (2, 2, 22.75, 'Debit', 'Completed', base_date + timedelta(days=2)),
        (3, 3, 28.00, 'Mobile Pay', 'Completed', base_date + timedelta(days=5)),
        (4, 4, 12.25, 'Cash', 'Completed', base_date + timedelta(days=1)),
        (5, 5, 35.50, 'Credit Card', 'Completed', base_date + timedelta(days=4)),
        (6, 6, 18.00, 'Debit', 'Completed', base_date + timedelta(days=1, hours=2)),
        (7, 7, 20.50, 'Mobile Pay', 'Completed', base_date + timedelta(days=3)),
        (8, 8, 26.75, 'Credit Card', 'Completed', base_date + timedelta(days=6)),
        (9, 9, 38.00, 'Cash', 'Pending', base_date + timedelta(days=8)),
        (10, 10, 24.25, 'Debit', 'Completed', base_date + timedelta(days=2, hours=3)),
    ]
    
    for payment in payments:
        cursor.execute("""
            INSERT INTO Payment (Transaction_ID, Ride_ID, Amount, Payment_Method, 
                               Payment_Status, Payment_Date)
            VALUES (:1, :2, :3, :4, :5, :6)
        """, payment)
    
    print(f"  ✓ Inserted {len(payments)} payments")

def seed_ratings(cursor):
    """Insert dummy rating records"""
    print("\nSeeding Ratings...")
    
    # Test scenario: Mix of ratings from 1-5 stars for both customers and drivers
    # Some rides have ratings, others don't (realistic scenario)
    ratings = [
        (1, 1, 5, 5, 'Great ride! Very professional driver.'),
        (2, 2, 4, 5, 'Good service, arrived on time.'),
        (3, 3, 5, 4, 'Excellent driver, smooth ride.'),
        (4, 4, 3, 4, 'Decent ride, but car could be cleaner.'),
        (5, 6, 5, 5, 'Perfect experience!'),
        (6, 7, 4, 4, 'Good overall, friendly driver.'),
        (7, 8, 5, 5, 'Amazing service, highly recommend.'),
        (8, 10, 4, 5, 'Very satisfied with the ride.'),
    ]
    
    for rating in ratings:
        cursor.execute("""
            INSERT INTO Rating (Rating_ID, Ride_ID, Customer_Rating, Driver_Rating, Comments)
            VALUES (:1, :2, :3, :4, :5)
        """, rating)
    
    print(f"  ✓ Inserted {len(ratings)} ratings")

def main():
    """Main function to seed the database"""
    print("=" * 60)
    print("Ride & Pickup DBMS - Database Seeding Script")
    print("=" * 60)
    
    try:
        # Connect to database
        connection = get_connection()
        cursor = connection.cursor()
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        clear_existing_data(cursor)
        
        # Seed all tables in correct order (respecting foreign key constraints)
        seed_customers(cursor)
        seed_drivers(cursor)
        seed_vehicles(cursor)
        seed_locations(cursor)
        seed_rides(cursor)
        seed_payments(cursor)
        seed_ratings(cursor)
        
        # Commit all changes
        connection.commit()
        print("\n" + "=" * 60)
        print("✓ Database seeding completed successfully!")
        print("=" * 60)
        
        # Display summary
        print("\nData Summary:")
        tables = [
            ('Customer', 5),
            ('Driver', 5),
            ('Vehicle', 5),
            ('Location', 10),
            ('Ride', 15),
            ('Payment', 10),
            ('Rating', 8)
        ]
        
        for table, count in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            actual_count = cursor.fetchone()[0]
            print(f"  {table}: {actual_count} records")
        
        # Close cursor and connection
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        if 'connection' in locals():
            connection.rollback()
            connection.close()
        raise

if __name__ == "__main__":
    main()
