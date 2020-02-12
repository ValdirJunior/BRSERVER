CREATE USER IF NOT EXISTS 'app'@'localhost' IDENTIFIED BY 'pass';
GRANT SELECT, INSERT, UPDATE, DELETE ON brazilian_cities.* TO 'app'@'localhost';
