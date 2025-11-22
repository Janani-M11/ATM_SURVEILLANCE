-- Fix PostgreSQL Role Issues
-- Run this as a superuser (or using pg_hba.conf trust method)

-- Check if postgres role exists and can login
SELECT rolname, rolcanlogin, rolsuper 
FROM pg_roles 
WHERE rolname = 'postgres';

-- If postgres role exists but cannot login, fix it:
ALTER ROLE postgres WITH LOGIN;

-- If postgres role doesn't exist or is wrong, create proper one:
-- First, drop the problematic role if it exists:
DROP ROLE IF EXISTS postgres;

-- Create proper postgres role with login capability:
CREATE ROLE postgres WITH
	LOGIN
	SUPERUSER
	CREATEDB
	CREATEROLE
	INHERIT
	REPLICATION
	BYPASSRLS
	CONNECTION LIMIT -1
	PASSWORD 'S@dh551811';

-- Verify the role:
SELECT rolname, rolcanlogin, rolsuper 
FROM pg_roles 
WHERE rolname = 'postgres';



