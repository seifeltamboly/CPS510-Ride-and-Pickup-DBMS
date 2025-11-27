#!/usr/bin/env python3
"""
End-to-End Testing Script for Ride & Pickup DBMS Web Application
Tests all CRUD operations, foreign key relationships, reports, and error handling
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001/api"
TIMEOUT = 10

# Test results tracking
tests_passed = 0
tests_failed = 0
test_results = []


def log_test(test_name, passed, message=""):
    """Log test result"""
    global tests_passed, tests_failed
    status = "✓ PASS" if passed else "✗ FAIL"
    result = f"{status}: {test_name}"
    if message:
        result += f" - {message}"
    print(result)
    test_results.append({"test": test_name, "passed": passed, "message": message})
    if passed:
        tests_passed += 1
    else:
        tests_failed += 1


def test_health_check():
    """Test backend server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        log_test("Health Check", response.status_code == 200, f"Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        log_test("Health Check", False, str(e))
        return False


# ============================================================================
# CUSTOMER CRUD TESTS
# ============================================================================

def test_customer_crud():
    """Test Customer CRUD operations"""
    print("\n=== Testing Customer CRUD Operations ===")

    # CREATE - Test creating a new customer
    new_customer = {
        "customer_name": "Test Customer E2E",
        "phone_number": "555-TEST-001",
        "email": "test.e2e@example.com"
    }

    try:
        response = requests.post(f"{BASE_URL}/customers", json=new_customer, timeout=TIMEOUT)
        created = response.status_code in [200, 201]
        log_test("Customer CREATE", created, f"Status: {response.status_code}")

        if created:
            customer_id = response.json().get('data', {}).get('customer_id')

            # READ - Get all customers
            response = requests.get(f"{BASE_URL}/customers", timeout=TIMEOUT)
            log_test("Customer READ (all)", response.status_code == 200)

            # READ - Get single customer
            if customer_id:
                response = requests.get(f"{BASE_URL}/customers/{customer_id}", timeout=TIMEOUT)
                log_test("Customer READ (single)", response.status_code == 200)

                # UPDATE - Update customer
                updated_customer = {
                    "customer_name": "Updated Test Customer",
                    "phone_number": "555-TEST-002",
                    "email": "updated.test@example.com"
                }
                response = requests.put(f"{BASE_URL}/customers/{customer_id}", json=updated_customer, timeout=TIMEOUT)
                log_test("Customer UPDATE", response.status_code == 200)

                # DELETE - Delete customer
                response = requests.delete(f"{BASE_URL}/customers/{customer_id}", timeout=TIMEOUT)
                log_test("Customer DELETE", response.status_code == 200)
            else:
                log_test("Customer READ (single)", False, "No customer_id returned")
                log_test("Customer UPDATE", False, "Skipped - no customer_id")
                log_test("Customer DELETE", False, "Skipped - no customer_id")
    except Exception as e:
        log_test("Customer CRUD", False, str(e))


# ============================================================================
# DRIVER CRUD TESTS
# ============================================================================

def test_driver_crud():
    """Test Driver CRUD operations"""
    print("\n=== Testing Driver CRUD Operations ===")

    new_driver = {
        "driver_name": "Test Driver E2E",
        "phone_number": "555-DRV-001",
        "license_number": "TEST-LIC-001"
    }

    try:
        response = requests.post(f"{BASE_URL}/drivers", json=new_driver, timeout=TIMEOUT)
        created = response.status_code in [200, 201]
        log_test("Driver CREATE", created, f"Status: {response.status_code}")

        if created:
            driver_id = response.json().get('data', {}).get('driver_id')

            response = requests.get(f"{BASE_URL}/drivers", timeout=TIMEOUT)
            log_test("Driver READ (all)", response.status_code == 200)

            if driver_id:
                response = requests.get(f"{BASE_URL}/drivers/{driver_id}", timeout=TIMEOUT)
                log_test("Driver READ (single)", response.status_code == 200)

                updated_driver = {
                    "driver_name": "Updated Test Driver",
                    "phone_number": "555-DRV-002",
                    "license_number": "TEST-LIC-002"
                }
                response = requests.put(f"{BASE_URL}/drivers/{driver_id}", json=updated_driver, timeout=TIMEOUT)
                log_test("Driver UPDATE", response.status_code == 200)

                response = requests.delete(f"{BASE_URL}/drivers/{driver_id}", timeout=TIMEOUT)
                log_test("Driver DELETE", response.status_code == 200)
    except Exception as e:
        log_test("Driver CRUD", False, str(e))


# ============================================================================
# VEHICLE CRUD TESTS
# ============================================================================

def test_vehicle_crud():
    """Test Vehicle CRUD operations"""
    print("\n=== Testing Vehicle CRUD Operations ===")

    # First create a driver for the vehicle
    driver = {
        "driver_name": "Vehicle Test Driver",
        "phone_number": "555-VEH-001",
        "license_number": "VEH-LIC-001"
    }

    try:
        response = requests.post(f"{BASE_URL}/drivers", json=driver, timeout=TIMEOUT)
        driver_id = response.json().get('data', {}).get('driver_id')

        if driver_id:
            new_vehicle = {
                "vehicle_vin": "TEST-VIN-E2E-001",
                "model": "Test Model",
                "color": "Test Color",
                "registration_year": 2023,
                "driver_id": driver_id
            }

            response = requests.post(f"{BASE_URL}/vehicles", json=new_vehicle, timeout=TIMEOUT)
            created = response.status_code in [200, 201]
            log_test("Vehicle CREATE", created, f"Status: {response.status_code}")

            response = requests.get(f"{BASE_URL}/vehicles", timeout=TIMEOUT)
            log_test("Vehicle READ (all)", response.status_code == 200)

            response = requests.get(f"{BASE_URL}/vehicles/TEST-VIN-E2E-001", timeout=TIMEOUT)
            log_test("Vehicle READ (single)", response.status_code == 200)

            updated_vehicle = {
                "model": "Updated Model",
                "color": "Updated Color",
                "registration_year": 2024,
                "driver_id": driver_id
            }
            response = requests.put(f"{BASE_URL}/vehicles/TEST-VIN-E2E-001", json=updated_vehicle, timeout=TIMEOUT)
            log_test("Vehicle UPDATE", response.status_code == 200)

            response = requests.delete(f"{BASE_URL}/vehicles/TEST-VIN-E2E-001", timeout=TIMEOUT)
            log_test("Vehicle DELETE", response.status_code == 200)

            # Cleanup driver
            requests.delete(f"{BASE_URL}/drivers/{driver_id}", timeout=TIMEOUT)
    except Exception as e:
        log_test("Vehicle CRUD", False, str(e))


# ============================================================================
# LOCATION CRUD TESTS
# ============================================================================

def test_location_crud():
    """Test Location CRUD operations"""
    print("\n=== Testing Location CRUD Operations ===")

    new_location = {
        "address": "123 Test Street",
        "city": "Test City",
        "postal_code": "T3ST01"
    }

    try:
        response = requests.post(f"{BASE_URL}/locations", json=new_location, timeout=TIMEOUT)
        created = response.status_code in [200, 201]
        log_test("Location CREATE", created, f"Status: {response.status_code}")

        if created:
            location_id = response.json().get('data', {}).get('location_id')

            response = requests.get(f"{BASE_URL}/locations", timeout=TIMEOUT)
            log_test("Location READ (all)", response.status_code == 200)

            if location_id:
                response = requests.get(f"{BASE_URL}/locations/{location_id}", timeout=TIMEOUT)
                log_test("Location READ (single)", response.status_code == 200)

                updated_location = {
                    "address": "456 Updated Street",
                    "city": "Updated City",
                    "postal_code": "U3ST02"
                }
                response = requests.put(f"{BASE_URL}/locations/{location_id}", json=updated_location, timeout=TIMEOUT)
                log_test("Location UPDATE", response.status_code == 200)

                response = requests.delete(f"{BASE_URL}/locations/{location_id}", timeout=TIMEOUT)
                log_test("Location DELETE", response.status_code == 200)
    except Exception as e:
        log_test("Location CRUD", False, str(e))


# ============================================================================
# RIDE CRUD TESTS
# ============================================================================

def test_ride_crud():
    """Test Ride CRUD operations"""
    print("\n=== Testing Ride CRUD Operations ===")

    # Create dependencies
    customer = {"customer_name": "Ride Test Customer", "phone_number": "555-RIDE-001", "email": "ride@test.com"}
    driver = {"driver_name": "Ride Test Driver", "phone_number": "555-RIDE-002", "license_number": "RIDE-LIC"}
    location1 = {"address": "Pickup Address", "city": "Test City", "postal_code": "P1CK01"}
    location2 = {"address": "Dropoff Address", "city": "Test City", "postal_code": "DR0P01"}

    try:
        customer_resp = requests.post(f"{BASE_URL}/customers", json=customer, timeout=TIMEOUT)
        customer_id = customer_resp.json().get('data', {}).get('customer_id')

        driver_resp = requests.post(f"{BASE_URL}/drivers", json=driver, timeout=TIMEOUT)
        driver_id = driver_resp.json().get('data', {}).get('driver_id')

        vehicle = {"vehicle_vin": "RIDE-VIN-001", "model": "Test", "color": "Blue", "registration_year": 2023, "driver_id": driver_id}
        requests.post(f"{BASE_URL}/vehicles", json=vehicle, timeout=TIMEOUT)

        loc1_resp = requests.post(f"{BASE_URL}/locations", json=location1, timeout=TIMEOUT)
        pickup_id = loc1_resp.json().get('data', {}).get('location_id')

        loc2_resp = requests.post(f"{BASE_URL}/locations", json=location2, timeout=TIMEOUT)
        dropoff_id = loc2_resp.json().get('data', {}).get('location_id')

        if all([customer_id, driver_id, pickup_id, dropoff_id]):
            new_ride = {
                "customer_id": customer_id,
                "driver_id": driver_id,
                "vehicle_vin": "RIDE-VIN-001",
                "pickup_location": pickup_id,
                "dropoff_location": dropoff_id,
                "start_time": "2024-01-15 10:00:00",
                "arrival_time": "2024-01-15 10:30:00"
            }

            response = requests.post(f"{BASE_URL}/rides", json=new_ride, timeout=TIMEOUT)
            created = response.status_code in [200, 201]
            log_test("Ride CREATE", created, f"Status: {response.status_code}")

            if created:
                ride_id = response.json().get('data', {}).get('ride_id')

                response = requests.get(f"{BASE_URL}/rides", timeout=TIMEOUT)
                log_test("Ride READ (all)", response.status_code == 200)

                if ride_id:
                    response = requests.get(f"{BASE_URL}/rides/{ride_id}", timeout=TIMEOUT)
                    log_test("Ride READ (single)", response.status_code == 200)

                    updated_ride = {
                        "customer_id": customer_id,
                        "driver_id": driver_id,
                        "vehicle_vin": "RIDE-VIN-001",
                        "pickup_location": pickup_id,
                        "dropoff_location": dropoff_id,
                        "start_time": "2024-01-15 11:00:00",
                        "arrival_time": "2024-01-15 11:30:00"
                    }
                    response = requests.put(f"{BASE_URL}/rides/{ride_id}", json=updated_ride, timeout=TIMEOUT)
                    log_test("Ride UPDATE", response.status_code == 200)

                    response = requests.delete(f"{BASE_URL}/rides/{ride_id}", timeout=TIMEOUT)
                    log_test("Ride DELETE", response.status_code == 200)

            # Cleanup
            requests.delete(f"{BASE_URL}/vehicles/RIDE-VIN-001", timeout=TIMEOUT)
            requests.delete(f"{BASE_URL}/drivers/{driver_id}", timeout=TIMEOUT)
            requests.delete(f"{BASE_URL}/customers/{customer_id}", timeout=TIMEOUT)
            requests.delete(f"{BASE_URL}/locations/{pickup_id}", timeout=TIMEOUT)
            requests.delete(f"{BASE_URL}/locations/{dropoff_id}", timeout=TIMEOUT)
    except Exception as e:
        log_test("Ride CRUD", False, str(e))


# ============================================================================
# PAYMENT CRUD TESTS
# ============================================================================

def test_payment_crud():
    """Test Payment CRUD operations"""
    print("\n=== Testing Payment CRUD Operations ===")

    # Create a ride first
    customer = {"customer_name": "Payment Test Customer", "phone_number": "555-PAY-001", "email": "pay@test.com"}
    driver = {"driver_name": "Payment Test Driver", "phone_number": "555-PAY-002", "license_number": "PAY-LIC"}
    location = {"address": "Payment Address", "city": "Test City", "postal_code": "PAY001"}

    try:
        customer_resp = requests.post(f"{BASE_URL}/customers", json=customer, timeout=TIMEOUT)
        customer_id = customer_resp.json().get('data', {}).get('customer_id')

        driver_resp = requests.post(f"{BASE_URL}/drivers", json=driver, timeout=TIMEOUT)
        driver_id = driver_resp.json().get('data', {}).get('driver_id')

        vehicle = {"vehicle_vin": "PAY-VIN-001", "model": "Test", "color": "Red", "registration_year": 2023, "driver_id": driver_id}
        requests.post(f"{BASE_URL}/vehicles", json=vehicle, timeout=TIMEOUT)

        loc_resp = requests.post(f"{BASE_URL}/locations", json=location, timeout=TIMEOUT)
        location_id = loc_resp.json().get('data', {}).get('location_id')

        ride = {
            "customer_id": customer_id,
            "driver_id": driver_id,
            "vehicle_vin": "PAY-VIN-001",
            "pickup_location": location_id,
            "dropoff_location": location_id,
            "start_time": "2024-01-15 12:00:00",
            "arrival_time": "2024-01-15 12:30:00"
        }
        ride_resp = requests.post(f"{BASE_URL}/rides", json=ride, timeout=TIMEOUT)
        ride_id = ride_resp.json().get('data', {}).get('ride_id')

        if ride_id:
            new_payment = {
                "ride_id": ride_id,
                "amount": 25.50,
                "payment_method": "Credit Card",
                "payment_status": "Completed",
                "payment_date": "2024-01-15"
            }

            response = requests.post(f"{BASE_URL}/payments", json=new_payment, timeout=TIMEOUT)
            created = response.status_code in [200, 201]
            log_test("Payment CREATE", created, f"Status: {response.status_code}")

            if created:
                transaction_id = response.json().get('data', {}).get('transaction_id')

                response = requests.get(f"{BASE_URL}/payments", timeout=TIMEOUT)
                log_test("Payment READ (all)", response.status_code == 200)

                if transaction_id:
                    response = requests.get(f"{BASE_URL}/payments/{transaction_id}", timeout=TIMEOUT)
                    log_test("Payment READ (single)", response.status_code == 200)

                    updated_payment = {
                        "ride_id": ride_id,
                        "amount": 30.00,
                        "payment_method": "Cash",
                        "payment_status": "Completed",
                        "payment_date": "2024-01-15"
                    }
                    response = requests.put(f"{BASE_URL}/payments/{transaction_id}", json=updated_payment, timeout=TIMEOUT)
                    log_test("Payment UPDATE", response.status_code == 200)

                    response = requests.delete(f"{BASE_URL}/payments/{transaction_id}", timeout=TIMEOUT)
                    log_test("Payment DELETE", response.status_code == 200)

            # Cleanup
            requests.delete(f"{BASE_URL}/rides/{ride_id}", timeout=TIMEOUT)
            requests.delete(f"{BASE_URL}/vehicles/PAY-VIN-001", timeout=TIMEOUT)
            requests.delete(f"{BASE_URL}/drivers/{driver_id}", timeout=TIMEOUT)
            requests.delete(f"{BASE_URL}/customers/{customer_id}", timeout=TIMEOUT)
            requests.delete(f"{BASE_URL}/locations/{location_id}", timeout=TIMEOUT)
    except Exception as e:
        log_test("Payment CRUD", False, str(e))


# ============================================================================
# RATING CRUD TESTS
# ============================================================================

def test_rating_crud():
    """Test Rating CRUD operations"""
    print("\n=== Testing Rating CRUD Operations ===")

    # Create a ride first
    customer = {"customer_name": "Rating Test Customer", "phone_number": "555-RAT-001", "email": "rating@test.com"}
    driver = {"driver_name": "Rating Test Driver", "phone_number": "555-RAT-002", "license_number": "RAT-LIC"}
    location = {"address": "Rating Address", "city": "Test City", "postal_code": "RAT001"}

    try:
        customer_resp = requests.post(f"{BASE_URL}/customers", json=customer, timeout=TIMEOUT)
        customer_id = customer_resp.json().get('data', {}).get('customer_id')

        driver_resp = requests.post(f"{BASE_URL}/drivers", json=driver, timeout=TIMEOUT)
        driver_id = driver_resp.json().get('data', {}).get('driver_id')

        vehicle = {"vehicle_vin": "RAT-VIN-001", "model": "Test", "color": "Green", "registration_year": 2023, "driver_id": driver_id}
        requests.post(f"{BASE_URL}/vehicles", json=vehicle, timeout=TIMEOUT)

        loc_resp = requests.post(f"{BASE_URL}/locations", json=location, timeout=TIMEOUT)
        location_id = loc_resp.json().get('data', {}).get('location_id')

        ride = {
            "customer_id": customer_id,
            "driver_id": driver_id,
            "vehicle_vin": "RAT-VIN-001",
            "pickup_location": location_id,
            "dropoff_location": location_id,
            "start_time": "2024-01-15 13:00:00",
            "arrival_time": "2024-01-15 13:30:00"
        }
        ride_resp = requests.post(f"{BASE_URL}/rides", json=ride, timeout=TIMEOUT)
        ride_id = ride_resp.json().get('data', {}).get('ride_id')

        if ride_id:
            new_rating = {
                "ride_id": ride_id,
                "customer_rating": 5,
                "driver_rating": 4,
                "comments": "Great ride!"
            }

            response = requests.post(f"{BASE_URL}/ratings", json=new_rating, timeout=TIMEOUT)
            created = response.status_code in [200, 201]
            log_test("Rating CREATE", created, f"Status: {response.status_code}")

            if created:
                rating_id = response.json().get('data', {}).get('rating_id')

                response = requests.get(f"{BASE_URL}/ratings", timeout=TIMEOUT)
                log_test("Rating READ (all)", response.status_code == 200)

                if rating_id:
                    response = requests.get(f"{BASE_URL}/ratings/{rating_id}", timeout=TIMEOUT)
                    log_test("Rating READ (single)", response.status_code == 200)

                    updated_rating = {
                        "ride_id": ride_id,
                        "customer_rating": 4,
                        "driver_rating": 5,
                        "comments": "Updated comment"
                    }
                    response = requests.put(f"{BASE_URL}/ratings/{rating_id}", json=updated_rating, timeout=TIMEOUT)
                    log_test("Rating UPDATE", response.status_code == 200)

                    response = requests.delete(f"{BASE_URL}/ratings/{rating_id}", timeout=TIMEOUT)
                    log_test("Rating DELETE", response.status_code == 200)

            # Cleanup
            requests.delete(f"{BASE_URL}/rides/{ride_id}", timeout=TIMEOUT)
            requests.delete(f"{BASE_URL}/vehicles/RAT-VIN-001", timeout=TIMEOUT)
            requests.delete(f"{BASE_URL}/drivers/{driver_id}", timeout=TIMEOUT)
            requests.delete(f"{BASE_URL}/customers/{customer_id}", timeout=TIMEOUT)
            requests.delete(f"{BASE_URL}/locations/{location_id}", timeout=TIMEOUT)
    except Exception as e:
        log_test("Rating CRUD", False, str(e))


# ============================================================================
# FOREIGN KEY CONSTRAINT TESTS
# ============================================================================

def test_foreign_key_constraints():
    """Test foreign key constraint handling"""
    print("\n=== Testing Foreign Key Constraints ===")

    # Create test data
    customer = {"customer_name": "FK Test Customer", "phone_number": "555-FK-001", "email": "fk@test.com"}
    driver = {"driver_name": "FK Test Driver", "phone_number": "555-FK-002", "license_number": "FK-LIC"}
    location = {"address": "FK Address", "city": "Test City", "postal_code": "FK0001"}

    try:
        customer_resp = requests.post(f"{BASE_URL}/customers", json=customer, timeout=TIMEOUT)
        customer_id = customer_resp.json().get('data', {}).get('customer_id')

        driver_resp = requests.post(f"{BASE_URL}/drivers", json=driver, timeout=TIMEOUT)
        driver_id = driver_resp.json().get('data', {}).get('driver_id')

        vehicle = {"vehicle_vin": "FK-VIN-001", "model": "Test", "color": "Black", "registration_year": 2023, "driver_id": driver_id}
        requests.post(f"{BASE_URL}/vehicles", json=vehicle, timeout=TIMEOUT)

        loc_resp = requests.post(f"{BASE_URL}/locations", json=location, timeout=TIMEOUT)
        location_id = loc_resp.json().get('data', {}).get('location_id')

        ride = {
            "customer_id": customer_id,
            "driver_id": driver_id,
            "vehicle_vin": "FK-VIN-001",
            "pickup_location": location_id,
            "dropoff_location": location_id,
            "start_time": "2024-01-15 14:00:00",
            "arrival_time": "2024-01-15 14:30:00"
        }
        ride_resp = requests.post(f"{BASE_URL}/rides", json=ride, timeout=TIMEOUT)
        ride_id = ride_resp.json().get('data', {}).get('ride_id')

        # Test: Try to delete customer with existing rides (should fail)
        response = requests.delete(f"{BASE_URL}/customers/{customer_id}", timeout=TIMEOUT)
        log_test("FK Constraint: Delete customer with rides", response.status_code == 400, "Should return 400")

        # Test: Try to delete driver with existing rides (should fail)
        response = requests.delete(f"{BASE_URL}/drivers/{driver_id}", timeout=TIMEOUT)
        log_test("FK Constraint: Delete driver with rides", response.status_code == 400, "Should return 400")

        # Test: Try to delete vehicle with existing rides (should fail)
        response = requests.delete(f"{BASE_URL}/vehicles/FK-VIN-001", timeout=TIMEOUT)
        log_test("FK Constraint: Delete vehicle with rides", response.status_code == 400, "Should return 400")

        # Cleanup in correct order
        if ride_id:
            requests.delete(f"{BASE_URL}/rides/{ride_id}", timeout=TIMEOUT)
        requests.delete(f"{BASE_URL}/vehicles/FK-VIN-001", timeout=TIMEOUT)
        requests.delete(f"{BASE_URL}/drivers/{driver_id}", timeout=TIMEOUT)
        requests.delete(f"{BASE_URL}/customers/{customer_id}", timeout=TIMEOUT)
        requests.delete(f"{BASE_URL}/locations/{location_id}", timeout=TIMEOUT)

    except Exception as e:
        log_test("Foreign Key Constraints", False, str(e))


# ============================================================================
# VALIDATION ERROR TESTS
# ============================================================================

def test_validation_errors():
    """Test input validation and error handling"""
    print("\n=== Testing Validation and Error Handling ===")

    # Test: Create customer with missing required fields
    invalid_customer = {"customer_name": "Test"}  # Missing phone and email
    response = requests.post(f"{BASE_URL}/customers", json=invalid_customer, timeout=TIMEOUT)
    log_test("Validation: Missing required fields", response.status_code == 400, "Should return 400")

    # Test: Create vehicle with non-existent driver
    invalid_vehicle = {
        "vehicle_vin": "INVALID-VIN",
        "model": "Test",
        "color": "Red",
        "registration_year": 2023,
        "driver_id": 999999  # Non-existent driver
    }
    response = requests.post(f"{BASE_URL}/vehicles", json=invalid_vehicle, timeout=TIMEOUT)
    log_test("Validation: Non-existent foreign key", response.status_code in [400, 404], "Should return 400 or 404")

    # Test: Get non-existent customer
    response = requests.get(f"{BASE_URL}/customers/999999", timeout=TIMEOUT)
    log_test("Validation: Get non-existent record", response.status_code == 404, "Should return 404")


# ============================================================================
# REPORT TESTS
# ============================================================================

def test_reports():
    """Test all report endpoints"""
    print("\n=== Testing Report Endpoints ===")

    try:
        # Test: Top Drivers by Ride Count
        response = requests.get(f"{BASE_URL}/reports/top-drivers", timeout=TIMEOUT)
        log_test("Report: Top Drivers", response.status_code == 200)

        # Test: Revenue by Payment Method
        response = requests.get(f"{BASE_URL}/reports/revenue-by-method", timeout=TIMEOUT)
        log_test("Report: Revenue by Method", response.status_code == 200)

        # Test: Average Ratings
        response = requests.get(f"{BASE_URL}/reports/average-ratings", timeout=TIMEOUT)
        log_test("Report: Average Ratings", response.status_code == 200)

        # Test: Rides by Location
        response = requests.get(f"{BASE_URL}/reports/rides-by-location", timeout=TIMEOUT)
        log_test("Report: Rides by Location", response.status_code == 200)

        # Test: Customer History (use customer ID 1 if exists)
        response = requests.get(f"{BASE_URL}/reports/customer-history/1", timeout=TIMEOUT)
        log_test("Report: Customer History", response.status_code in [200, 404], "200 if customer exists, 404 otherwise")

    except Exception as e:
        log_test("Reports", False, str(e))


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all tests"""
    print("=" * 70)
    print("RIDE & PICKUP DBMS - END-TO-END TEST SUITE")
    print("=" * 70)

    # Check if backend is running
    if not test_health_check():
        print("\n❌ Backend server is not running. Please start the backend first.")
        sys.exit(1)

    # Run all test suites
    test_customer_crud()
    test_driver_crud()
    test_vehicle_crud()
    test_location_crud()
    test_ride_crud()
    test_payment_crud()
    test_rating_crud()
    test_foreign_key_constraints()
    test_validation_errors()
    test_reports()

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {tests_passed + tests_failed}")
    print(f"✓ Passed: {tests_passed}")
    print(f"✗ Failed: {tests_failed}")
    print(f"Success Rate: {(tests_passed / (tests_passed + tests_failed) * 100):.1f}%")
    print("=" * 70)

    # Exit with appropriate code
    sys.exit(0 if tests_failed == 0 else 1)


if __name__ == "__main__":
    main()
