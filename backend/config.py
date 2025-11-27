"""
Configuration management for the Ride & Pickup DBMS application.

This module handles loading and managing configuration settings from environment
variables, providing a centralized configuration object for the application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Application configuration class.
    
    Loads database credentials and other settings from environment variables.
    Provides default values for development if environment variables are not set.
    """
    
    # Database configuration
    DB_USER = os.getenv('DB_USER', 'default_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'default_password')
    DB_DSN = os.getenv('DB_DSN', 'localhost:1521/XE')
    
    # Connection pool configuration
    # min: Minimum number of connections in the pool
    # max: Maximum number of connections in the pool
    # increment: Number of connections to create when pool needs to grow
    DB_POOL_MIN = int(os.getenv('DB_POOL_MIN', '2'))
    DB_POOL_MAX = int(os.getenv('DB_POOL_MAX', '10'))
    DB_POOL_INCREMENT = int(os.getenv('DB_POOL_INCREMENT', '1'))
    
    # Flask configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    @staticmethod
    def validate():
        """
        Validate that required configuration values are set.
        
        Raises:
            ValueError: If required configuration is missing
        """
        required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_DSN']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
