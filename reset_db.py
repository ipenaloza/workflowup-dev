#!/usr/bin/env python
"""
Script to reset the MySQL database for custom user model migration.
This is necessary when switching to a custom user model after Django's
default migrations have already been applied.
"""
import MySQLdb

# Database connection settings
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USER = 'admindb'
DB_PASSWORD = 'admindb'
DB_NAME = 'workflowup2'

try:
    # Connect to MySQL server (not to specific database)
    connection = MySQLdb.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        passwd=DB_PASSWORD
    )
    cursor = connection.cursor()

    # Drop database if exists
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    print(f"Database '{DB_NAME}' dropped successfully")

    # Create database with UTF-8 support
    cursor.execute(
        f"CREATE DATABASE {DB_NAME} "
        f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    print(f"Database '{DB_NAME}' created successfully")

    cursor.close()
    connection.close()
    print("\nDatabase reset complete. You can now run:")
    print("  python workflowup/manage.py migrate")

except MySQLdb.Error as e:
    print(f"Error: {e}")
    exit(1)
