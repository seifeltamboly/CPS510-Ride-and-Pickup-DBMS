-- ============================================================================
-- Ride & Pickup DBMS - Database Initialization Script
-- ============================================================================
-- This script populates the Oracle database with dummy data for testing
-- and demonstration purposes.
--
-- Test Data Scenarios:
-- - 5 customers with varied contact information
-- - 5 drivers with different license numbers
-- - 5 vehicles assigned to drivers (one vehicle per driver)
-- - 10 locations covering different areas in Toronto
-- - 15 rides showing various pickup/dropoff combinations and patterns
-- - 10 payments with different methods (Credit Card, Debit, Cash, Mobile Pay)
-- - 8 ratings showing customer and driver feedback (mix of 3-5 stars)
--
-- Usage: Run this script in SQL*Plus or SQL Developer after creating tables
-- ============================================================================

-- Clear existing data (in correct order due to foreign key constraints)
DELETE FROM Rating;
DELETE FROM Payment;
DELETE FROM Ride;
DELETE FROM Vehicle;
DELETE FROM Location;
DELETE FROM Driver;
DELETE FROM Customer;

-- ============================================================================
-- CUSTOMERS
-- ============================================================================
-- Test scenario: Mix of personal customers with various contact methods
-- These customers represent different usage patterns (frequent, occasional, new)

INSERT INTO Customer (Customer_ID, Customer_Name, Phone_Number, Email)
VALUES (1, 'Alice Johnson', '416-555-0101', 'alice.johnson@email.com');

INSERT INTO Customer (Customer_ID, Customer_Name, Phone_Number, Email)
VALUES (2, 'Bob Smith', '416-555-0102', 'bob.smith@email.com');

INSERT INTO Customer (Customer_ID, Customer_Name, Phone_Number, Email)
VALUES (3, 'Carol Williams', '647-555-0103', 'carol.w@email.com');

INSERT INTO Customer (Customer_ID, Customer_Name, Phone_Number, Email)
VALUES (4, 'David Brown', '416-555-0104', 'david.brown@email.com');

INSERT INTO Customer (Customer_ID, Customer_Name, Phone_Number, Email)
VALUES (5, 'Emma Davis', '647-555-0105', 'emma.davis@email.com');

-- ============================================================================
-- DRIVERS
-- ============================================================================
-- Test scenario: Drivers with different license numbers
-- Each driver will be assigned one vehicle and handle multiple rides

INSERT INTO Driver (Driver_ID, Driver_Name, Phone_Number, License_Number)
VALUES (1, 'John Driver', '416-555-0201', 'DL123456');

INSERT INTO Driver (Driver_ID, Driver_Name, Phone_Number, License_Number)
VALUES (2, 'Sarah Wheeler', '647-555-0202', 'DL234567');

INSERT INTO Driver (Driver_ID, Driver_Name, Phone_Number, License_Number)
VALUES (3, 'Mike Roadster', '416-555-0203', 'DL345678');

INSERT INTO Driver (Driver_ID, Driver_Name, Phone_Number, License_Number)
VALUES (4, 'Lisa Cruise', '647-555-0204', 'DL456789');

INSERT INTO Driver (Driver_ID, Driver_Name, Phone_Number, License_Number)
VALUES (5, 'Tom Navigator', '416-555-0205', 'DL567890');

-- ============================================================================
-- VEHICLES
-- ============================================================================
-- Test scenario: Different vehicle types and years, each assigned to a driver
-- Mix of sedans, SUVs, and family vehicles from various manufacturers

INSERT INTO Vehicle (Vehicle_VIN, Model, Color, Registration_Year, Driver_ID)
VALUES ('1HGCM82633A123456', 'Honda Accord', 'Silver', 2020, 1);

INSERT INTO Vehicle (Vehicle_VIN, Model, Color, Registration_Year, Driver_ID)
VALUES ('2T1BURHE0FC123457', 'Toyota Corolla', 'Blue', 2019, 2);

INSERT INTO Vehicle (Vehicle_VIN, Model, Color, Registration_Year, Driver_ID)
VALUES ('3VW2B7AJ8DM123458', 'Volkswagen Jetta', 'Black', 2021, 3);

INSERT INTO Vehicle (Vehicle_VIN, Model, Color, Registration_Year, Driver_ID)
VALUES ('5FNRL6H78GB123459', 'Honda Odyssey', 'White', 2018, 4);

INSERT INTO Vehicle (Vehicle_VIN, Model, Color, Registration_Year, Driver_ID)
VALUES ('1G1ZD5ST8LF123460', 'Chevrolet Malibu', 'Red', 2022, 5);

-- ============================================================================
-- LOCATIONS
-- ============================================================================
-- Test scenario: Mix of residential, commercial, and popular destinations
-- Covers various neighborhoods and districts in Toronto

INSERT INTO Location (Location_ID, Address, City, Postal_Code)
VALUES (1, '123 King St W', 'Toronto', 'M5H 1A1');

INSERT INTO Location (Location_ID, Address, City, Postal_Code)
VALUES (2, '456 Queen St E', 'Toronto', 'M5A 1T1');

INSERT INTO Location (Location_ID, Address, City, Postal_Code)
VALUES (3, '789 Yonge St', 'Toronto', 'M4Y 2B2');

INSERT INTO Location (Location_ID, Address, City, Postal_Code)
VALUES (4, '321 Bay St', 'Toronto', 'M5H 2Y4');

INSERT INTO Location (Location_ID, Address, City, Postal_Code)
VALUES (5, '654 Bloor St W', 'Toronto', 'M6G 1K4');

INSERT INTO Location (Location_ID, Address, City, Postal_Code)
VALUES (6, '987 Dundas St W', 'Toronto', 'M6J 1W3');

INSERT INTO Location (Location_ID, Address, City, Postal_Code)
VALUES (7, '147 College St', 'Toronto', 'M5T 1P7');

INSERT INTO Location (Location_ID, Address, City, Postal_Code)
VALUES (8, '258 Spadina Ave', 'Toronto', 'M5T 2C2');

INSERT INTO Location (Location_ID, Address, City, Postal_Code)
VALUES (9, '369 Front St E', 'Toronto', 'M5A 1G1');

INSERT INTO Location (Location_ID, Address, City, Postal_Code)
VALUES (10, '741 Harbourfront', 'Toronto', 'M5J 2R8');

-- ============================================================================
-- RIDES
-- ============================================================================
-- Test scenario: Various ride patterns including:
-- - Short trips (15-20 minutes) and longer trips (30-45 minutes)
-- - Different times of day and dates
-- - Multiple rides per customer (Alice: 3, Bob: 2, Carol: 4, David: 3, Emma: 3)
-- - Multiple rides per driver to test "Top Drivers" report
-- - Various pickup/dropoff location combinations

-- Customer 1 (Alice Johnson) - Frequent rider with 3 rides
INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (1, 1, 1, '1HGCM82633A123456', 1, 3, TO_TIMESTAMP('2024-01-15 08:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-15 08:20:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (2, 1, 2, '2T1BURHE0FC123457', 3, 5, TO_TIMESTAMP('2024-01-17 09:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-17 09:25:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (3, 1, 3, '3VW2B7AJ8DM123458', 5, 7, TO_TIMESTAMP('2024-01-20 14:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-20 14:30:00', 'YYYY-MM-DD HH24:MI:SS'));

-- Customer 2 (Bob Smith) - Occasional rider with 2 rides
INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (4, 2, 4, '5FNRL6H78GB123459', 2, 4, TO_TIMESTAMP('2024-01-16 10:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-16 10:15:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (5, 2, 5, '1G1ZD5ST8LF123460', 4, 6, TO_TIMESTAMP('2024-01-19 16:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-19 16:35:00', 'YYYY-MM-DD HH24:MI:SS'));

-- Customer 3 (Carol Williams) - Regular rider with 4 rides (most active customer)
INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (6, 3, 1, '1HGCM82633A123456', 6, 8, TO_TIMESTAMP('2024-01-16 10:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-16 10:18:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (7, 3, 2, '2T1BURHE0FC123457', 8, 10, TO_TIMESTAMP('2024-01-18 11:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-18 11:22:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (8, 3, 3, '3VW2B7AJ8DM123458', 10, 1, TO_TIMESTAMP('2024-01-21 15:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-21 15:28:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (9, 3, 4, '5FNRL6H78GB123459', 1, 9, TO_TIMESTAMP('2024-01-23 13:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-23 13:40:00', 'YYYY-MM-DD HH24:MI:SS'));

-- Customer 4 (David Brown) - New rider with 3 rides
INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (10, 4, 5, '1G1ZD5ST8LF123460', 2, 7, TO_TIMESTAMP('2024-01-17 11:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-17 11:25:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (11, 4, 1, '1HGCM82633A123456', 7, 3, TO_TIMESTAMP('2024-01-20 09:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-20 09:20:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (12, 4, 2, '2T1BURHE0FC123457', 3, 9, TO_TIMESTAMP('2024-01-22 17:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-22 17:32:00', 'YYYY-MM-DD HH24:MI:SS'));

-- Customer 5 (Emma Davis) - Occasional rider with 3 rides
INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (13, 5, 3, '3VW2B7AJ8DM123458', 4, 2, TO_TIMESTAMP('2024-01-18 12:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-18 12:15:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (14, 5, 4, '5FNRL6H78GB123459', 9, 5, TO_TIMESTAMP('2024-01-21 14:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-21 14:38:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Ride (Ride_ID, Customer_ID, Driver_ID, Vehicle_VIN, Pickup_Location, Dropoff_Location, Start_Time, Arrival_Time)
VALUES (15, 5, 5, '1G1ZD5ST8LF123460', 5, 10, TO_TIMESTAMP('2024-01-24 10:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2024-01-24 10:45:00', 'YYYY-MM-DD HH24:MI:SS'));

-- ============================================================================
-- PAYMENTS
-- ============================================================================
-- Test scenario: Different payment methods to test "Revenue by Payment Method" report
-- - Credit Card: 4 payments (most popular)
-- - Debit: 3 payments
-- - Cash: 2 payments
-- - Mobile Pay: 2 payments
-- Mix of Completed and Pending statuses (1 pending payment for testing)

INSERT INTO Payment (Transaction_ID, Ride_ID, Amount, Payment_Method, Payment_Status, Payment_Date)
VALUES (1, 1, 15.50, 'Credit Card', 'Completed', TO_TIMESTAMP('2024-01-15 08:30:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Payment (Transaction_ID, Ride_ID, Amount, Payment_Method, Payment_Status, Payment_Date)
VALUES (2, 2, 22.75, 'Debit', 'Completed', TO_TIMESTAMP('2024-01-17 09:30:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Payment (Transaction_ID, Ride_ID, Amount, Payment_Method, Payment_Status, Payment_Date)
VALUES (3, 3, 28.00, 'Mobile Pay', 'Completed', TO_TIMESTAMP('2024-01-20 14:35:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Payment (Transaction_ID, Ride_ID, Amount, Payment_Method, Payment_Status, Payment_Date)
VALUES (4, 4, 12.25, 'Cash', 'Completed', TO_TIMESTAMP('2024-01-16 10:20:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Payment (Transaction_ID, Ride_ID, Amount, Payment_Method, Payment_Status, Payment_Date)
VALUES (5, 5, 35.50, 'Credit Card', 'Completed', TO_TIMESTAMP('2024-01-19 16:40:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Payment (Transaction_ID, Ride_ID, Amount, Payment_Method, Payment_Status, Payment_Date)
VALUES (6, 6, 18.00, 'Debit', 'Completed', TO_TIMESTAMP('2024-01-16 10:25:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Payment (Transaction_ID, Ride_ID, Amount, Payment_Method, Payment_Status, Payment_Date)
VALUES (7, 7, 20.50, 'Mobile Pay', 'Completed', TO_TIMESTAMP('2024-01-18 11:30:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Payment (Transaction_ID, Ride_ID, Amount, Payment_Method, Payment_Status, Payment_Date)
VALUES (8, 8, 26.75, 'Credit Card', 'Completed', TO_TIMESTAMP('2024-01-21 15:35:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Payment (Transaction_ID, Ride_ID, Amount, Payment_Method, Payment_Status, Payment_Date)
VALUES (9, 9, 38.00, 'Cash', 'Pending', TO_TIMESTAMP('2024-01-23 13:45:00', 'YYYY-MM-DD HH24:MI:SS'));

INSERT INTO Payment (Transaction_ID, Ride_ID, Amount, Payment_Method, Payment_Status, Payment_Date)
VALUES (10, 10, 24.25, 'Debit', 'Completed', TO_TIMESTAMP('2024-01-17 11:30:00', 'YYYY-MM-DD HH24:MI:SS'));

-- ============================================================================
-- RATINGS
-- ============================================================================
-- Test scenario: Mix of ratings from 3-5 stars for both customers and drivers
-- to test "Average Rating by Driver" report
-- Not all rides have ratings (realistic scenario - 8 ratings for 15 rides)
-- Driver 1 (John): 3 ratings, avg 4.67
-- Driver 2 (Sarah): 2 ratings, avg 4.5
-- Driver 3 (Mike): 2 ratings, avg 4.5
-- Driver 4 (Lisa): 2 ratings, avg 4.0
-- Driver 5 (Tom): 1 rating, avg 5.0

INSERT INTO Rating (Rating_ID, Ride_ID, Customer_Rating, Driver_Rating, Comments)
VALUES (1, 1, 5, 5, 'Great ride! Very professional driver.');

INSERT INTO Rating (Rating_ID, Ride_ID, Customer_Rating, Driver_Rating, Comments)
VALUES (2, 2, 4, 5, 'Good service, arrived on time.');

INSERT INTO Rating (Rating_ID, Ride_ID, Customer_Rating, Driver_Rating, Comments)
VALUES (3, 3, 5, 4, 'Excellent driver, smooth ride.');

INSERT INTO Rating (Rating_ID, Ride_ID, Customer_Rating, Driver_Rating, Comments)
VALUES (4, 4, 3, 4, 'Decent ride, but car could be cleaner.');

INSERT INTO Rating (Rating_ID, Ride_ID, Customer_Rating, Driver_Rating, Comments)
VALUES (5, 6, 5, 5, 'Perfect experience!');

INSERT INTO Rating (Rating_ID, Ride_ID, Customer_Rating, Driver_Rating, Comments)
VALUES (6, 7, 4, 4, 'Good overall, friendly driver.');

INSERT INTO Rating (Rating_ID, Ride_ID, Customer_Rating, Driver_Rating, Comments)
VALUES (7, 8, 5, 5, 'Amazing service, highly recommend.');

INSERT INTO Rating (Rating_ID, Ride_ID, Customer_Rating, Driver_Rating, Comments)
VALUES (8, 10, 4, 5, 'Very satisfied with the ride.');

-- ============================================================================
-- Commit all changes
-- ============================================================================
COMMIT;

-- ============================================================================
-- Verification Queries
-- ============================================================================
-- Run these queries to verify the data was inserted correctly

-- Check record counts
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

-- ============================================================================
-- End of Script
-- ============================================================================
