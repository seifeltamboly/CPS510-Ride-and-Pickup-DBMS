"""
Database connection management for Oracle Database.

This module provides connection pooling and database access functions using cx_Oracle.
It manages a connection pool for efficient database connections and provides error
handling for common database operations.
"""

import cx_Oracle
import logging
from config import Config

# Configure logging for database operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection pool variable
_connection_pool = None


def initialize_pool():
    """
    Initialize the Oracle database connection pool.
    
    Creates a connection pool with the following parameters:
    - min: Minimum number of connections kept open (reduces connection overhead)
    - max: Maximum number of connections allowed (prevents resource exhaustion)
    - increment: Number of connections created when pool needs to grow
    
    The connection pool improves performance by reusing database connections
    instead of creating new ones for each request.
    
    Returns:
        cx_Oracle.SessionPool: The initialized connection pool
        
    Raises:
        cx_Oracle.DatabaseError: If connection to database fails
        ValueError: If configuration is invalid
    """
    global _connection_pool
    
    if _connection_pool is not None:
        logger.info("Connection pool already initialized")
        return _connection_pool
    
    try:
        # Validate configuration before attempting connection
        Config.validate()
        
        logger.info(f"Initializing connection pool to {Config.DB_DSN}")
        
        # Create connection pool with configured parameters
        # min: Start with minimum connections to reduce initial overhead
        # max: Limit maximum connections to prevent database overload
        # increment: Grow pool gradually as needed
        _connection_pool = cx_Oracle.SessionPool(
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            dsn=Config.DB_DSN,
            min=Config.DB_POOL_MIN,
            max=Config.DB_POOL_MAX,
            increment=Config.DB_POOL_INCREMENT,
            threaded=True  # Enable thread safety for Flask multi-threading
        )
        
        logger.info(
            f"Connection pool initialized successfully "
            f"(min={Config.DB_POOL_MIN}, max={Config.DB_POOL_MAX})"
        )
        
        return _connection_pool
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        logger.error(
            f"Database connection failed: {error_obj.message} "
            f"(Code: {error_obj.code})"
        )
        raise
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error initializing connection pool: {str(e)}")
        raise


def get_connection():
    """
    Acquire a connection from the connection pool.
    
    This function retrieves an available connection from the pool. If the pool
    is not initialized, it will be created automatically. Connections should be
    released back to the pool after use by calling connection.close().
    
    Returns:
        cx_Oracle.Connection: A database connection from the pool
        
    Raises:
        cx_Oracle.DatabaseError: If unable to acquire connection
        RuntimeError: If connection pool is not initialized
        
    Example:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Customer")
            results = cursor.fetchall()
            cursor.close()
        finally:
            conn.close()  # Return connection to pool
    """
    global _connection_pool
    
    try:
        # Initialize pool if not already done
        if _connection_pool is None:
            logger.info("Connection pool not initialized, initializing now")
            initialize_pool()
        
        # Acquire connection from pool
        # This will wait if all connections are in use (up to max)
        connection = _connection_pool.acquire()
        logger.debug("Connection acquired from pool")
        
        return connection
        
    except cx_Oracle.DatabaseError as e:
        error_obj, = e.args
        logger.error(
            f"Failed to acquire connection: {error_obj.message} "
            f"(Code: {error_obj.code})"
        )
        raise
    except Exception as e:
        logger.error(f"Unexpected error acquiring connection: {str(e)}")
        raise


def close_pool():
    """
    Close the connection pool and release all connections.
    
    This should be called when the application is shutting down to properly
    clean up database resources. All connections in the pool will be closed.
    
    Note:
        After calling this function, get_connection() will reinitialize the pool
        if called again.
    """
    global _connection_pool
    
    if _connection_pool is not None:
        try:
            logger.info("Closing connection pool")
            _connection_pool.close()
            _connection_pool = None
            logger.info("Connection pool closed successfully")
        except Exception as e:
            logger.error(f"Error closing connection pool: {str(e)}")
            raise


def test_connection():
    """
    Test the database connection by executing a simple query.
    
    This function is useful for verifying that the database is accessible
    and the connection configuration is correct.
    
    Returns:
        bool: True if connection test succeeds, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Execute simple test query
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        logger.info("Database connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False
