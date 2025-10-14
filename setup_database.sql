-- PostgreSQL Database Setup for Food Delivery App

-- Create database
CREATE DATABASE food_delivery_db;

-- Create user
CREATE USER fooddelivery_user WITH PASSWORD 'fooddelivery_pass';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE food_delivery_db TO fooddelivery_user;

-- Connect to the database
\c food_delivery_db;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO fooddelivery_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fooddelivery_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fooddelivery_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO fooddelivery_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO fooddelivery_user;
