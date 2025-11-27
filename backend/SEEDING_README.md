# Database Seeding Instructions

This directory contains two options for populating the Ride & Pickup DBMS database with dummy data for testing and demonstration.

## Test Data Overview

The seeding scripts create the following test data:

- **5 Customers**: Alice Johnson, Bob Smith, Carol Williams, David Brown, Emma Davis
- **5 Drivers**: John Driver, Sarah Wheeler, Mike Roadster, Lisa Cruise, Tom Navigator
- **5 Vehicles**: Mix of Honda, Toyota, Volkswagen, and Chevrolet models (2018-2022)
- **10 Locations**: Various addresses across Toronto
- **15 Rides**: Different patterns showing frequent and occasional riders
- **10 Payments**: Mix of Credit Card, Debit, Cash, and Mobile Pay methods
- **8 Ratings**: Customer and driver ratings ranging from 3-5 stars

## Option 1: Python Script (Recommended)

The Python script (`seed_data.py`) provides better error handling and feedback.

### Prerequisites

- Python 3.x installed
- cx_Oracle library installed (`pip install cx_Oracle`)
- `.env` file configured with database credentials

### Usage

```bash
# From the backend directory
python seed_data.py
```

### Features

- Automatic connection to Oracle database using environment variables
- Clears existing data before seeding (optional)
- Provides detailed progress feedback
- Displays summary of inserted records
- Better error handling and rollback on failure

## Option 2: SQL Script

The SQL script (`init_db.sql`) can be run directly in SQL*Plus or SQL Developer.

### Usage with SQL*Plus

```bash
sqlplus username/password@database @init_db.sql
```

### Usage with SQL Developer

1. Open SQL Developer
2. Connect to your Oracle database
3. Open the `init_db.sql` file
4. Click "Run Script" (F5)

### Features

- Pure SQL implementation
- Includes detailed comments explaining test scenarios
- Contains verification queries at the end
- Can be easily modified for custom data

## Data Scenarios

### Customer Usage Patterns

- **Alice Johnson** (Customer 1): Frequent rider - 3 rides
- **Bob Smith** (Customer 2): Occasional rider - 2 rides
- **Carol Williams** (Customer 3): Most active rider - 4 rides
- **David Brown** (Customer 4): New rider - 3 rides
- **Emma Davis** (Customer 5): Occasional rider - 3 rides

### Driver Performance

- **John Driver** (Driver 1): 3 rides, 3 ratings, avg 4.67 stars
- **Sarah Wheeler** (Driver 2): 3 rides, 2 ratings, avg 4.5 stars
- **Mike Roadster** (Driver 3): 3 rides, 2 ratings, avg 4.5 stars
- **Lisa Cruise** (Driver 4): 3 rides, 2 ratings, avg 4.0 stars
- **Tom Navigator** (Driver 5): 3 rides, 1 rating, avg 5.0 stars

### Payment Methods Distribution

- **Credit Card**: 4 payments, $105.50 total
- **Debit**: 3 payments, $65.00 total
- **Cash**: 2 payments, $50.25 total
- **Mobile Pay**: 2 payments, $48.50 total

### Rating Distribution

- 8 ratings out of 15 rides (53% rating completion)
- Customer ratings: 3-5 stars
- Driver ratings: 4-5 stars
- Mix of positive feedback with constructive comments

## Testing Reports

This data is designed to test all advanced report queries:

1. **Top Drivers by Ride Count**: All drivers have 3 rides each
2. **Revenue by Payment Method**: Credit Card leads with $105.50
3. **Average Rating by Driver**: Ratings range from 4.0 to 5.0 stars
4. **Rides by Location**: Various pickup/dropoff combinations
5. **Customer Ride History**: Carol Williams has the most rides (4)

## Verification

After running either script, verify the data with:

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

Expected output:
- Customer: 5
- Driver: 5
- Vehicle: 5
- Location: 10
- Ride: 15
- Payment: 10
- Rating: 8

## Troubleshooting

### Python Script Issues

**Error: "No module named 'cx_Oracle'"**
```bash
pip install cx_Oracle
```

**Error: "Unable to connect to database"**
- Check your `.env` file has correct credentials
- Verify database is running and accessible
- Test connection with SQL*Plus or SQL Developer first

### SQL Script Issues

**Error: "ORA-02291: integrity constraint violated"**
- Ensure tables are created before running this script
- Check that foreign key relationships are properly defined

**Error: "ORA-00001: unique constraint violated"**
- Data already exists in tables
- Run the DELETE statements at the top of the script first
- Or manually clear tables before re-running

## Customization

To modify the test data:

1. **Python Script**: Edit the data lists in each `seed_*` function
2. **SQL Script**: Modify the INSERT statements directly

Remember to maintain referential integrity when modifying:
- Vehicles must reference existing Drivers
- Rides must reference existing Customers, Drivers, Vehicles, and Locations
- Payments must reference existing Rides
- Ratings must reference existing Rides

## Notes

- The Python script automatically clears existing data before seeding
- The SQL script includes DELETE statements at the beginning
- All timestamps use January 2024 dates for consistency
- VIN numbers are realistic format but fictional
- Phone numbers use Toronto area codes (416, 647)
- Email addresses are fictional
