-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Create table: Airlines
CREATE TABLE Airlines (
    AirlineID INTEGER PRIMARY KEY,
    AirlineName TEXT,
    Country TEXT,
    ContactEmail TEXT
);

-- Create table: Airports
CREATE TABLE Airports (
    AirportID INTEGER PRIMARY KEY,
    AirportName TEXT,
    City TEXT,
    Country TEXT,
    IATA_Code TEXT
);

-- Create table: Flights
CREATE TABLE Flights (
    FlightID INTEGER PRIMARY KEY,
    FlightNumber TEXT,
    Source INTEGER,
    Destination INTEGER,
    DepartureTime TEXT,
    ArrivalTime TEXT,
    Airline INTEGER,
    FOREIGN KEY (Source) REFERENCES Airports(AirportID),
    FOREIGN KEY (Destination) REFERENCES Airports(AirportID),
    FOREIGN KEY (Airline) REFERENCES Airlines(AirlineID)
);

-- Create table: Passengers
CREATE TABLE Passengers (
    PassengerID INTEGER PRIMARY KEY,
    FirstName TEXT,
    LastName TEXT,
    DateOfBirth TEXT,
    Email TEXT,
    Phone TEXT
);

-- Create table: Tickets
CREATE TABLE Tickets (
    TicketID INTEGER PRIMARY KEY,
    PassengerID INTEGER,
    FlightID INTEGER,
    BookingDate TEXT,
    SeatNumber TEXT,
    Price REAL,
    FOREIGN KEY (PassengerID) REFERENCES Passengers(PassengerID),
    FOREIGN KEY (FlightID) REFERENCES Flights(FlightID)
);

-- Insert data: Airlines
INSERT INTO Airlines VALUES
(1, 'SkyAir', 'USA', 'contact@skyair.com'),
(2, 'GlobalWings', 'UK', 'support@globalwings.co.uk'),
(3, 'Blue Horizon', 'Canada', 'info@bluehorizon.ca'),
(4, 'AirNova', 'Australia', 'contact@airnova.au'),
(5, 'JetStream', 'India', 'support@jetstream.in');

-- Insert data: Airports
INSERT INTO Airports VALUES
(1, 'John F. Kennedy International Airport', 'New York', 'USA', 'JFK'),
(2, 'Heathrow Airport', 'London', 'UK', 'LHR'),
(3, 'Toronto Pearson International Airport', 'Toronto', 'Canada', 'YYZ'),
(4, 'Sydney Kingsford Smith Airport', 'Sydney', 'Australia', 'SYD'),
(5, 'Chhatrapati Shivaji Maharaj Airport', 'Mumbai', 'India', 'BOM');

-- Insert data: Flights
INSERT INTO Flights VALUES
(1, 'SA101', 1, 2, '2024-01-15 08:00:00', '2024-01-15 20:00:00', 1),
(2, 'GW202', 2, 3, '2024-01-16 09:00:00', '2024-01-16 19:00:00', 2),
(3, 'BH303', 3, 1, '2024-01-17 10:00:00', '2024-01-17 18:00:00', 3),
(4, 'AN404', 4, 5, '2024-01-18 11:00:00', '2024-01-18 21:00:00', 4),
(5, 'JS505', 5, 1, '2024-01-19 12:00:00', '2024-01-19 22:00:00', 5);

-- Insert data: Passengers
INSERT INTO Passengers VALUES
(1, 'Alice', 'Smith', '1985-05-12', 'alice.smith@example.com', '+1234567890'),
(2, 'Bob', 'Jones', '1990-07-20', 'bob.jones@example.com', '+0987654321'),
(3, 'Charlie', 'Brown', '1982-11-02', 'charlie.brown@example.com', '+1122334455'),
(4, 'Diana', 'Prince', '1995-03-14', 'diana.prince@example.com', '+2233445566'),
(5, 'Ethan', 'Hunt', '1988-08-30', 'ethan.hunt@example.com', '+3344556677');

-- Insert data: Tickets
INSERT INTO Tickets VALUES
(1, 1, 1, '2024-01-10 14:30:00', '12A', 350.00),
(2, 1, 2, '2024-01-11 15:00:00', '14B', 400.00),
(3, 1, 3, '2024-01-12 16:00:00', '16C', 450.00),
(4, 2, 1, '2024-01-13 17:00:00', '18D', 500.00),
(5, 2, 4, '2024-01-14 18:00:00', '20E', 550.00),
(6, 2, 5, '2024-01-15 19:00:00', '22F', 600.00),
(7, 3, 1, '2024-01-16 20:00:00', '24G', 650.00),
(8, 3, 2, '2024-01-17 21:00:00', '26H', 700.00),
(9, 3, 3, '2024-01-18 22:00:00', '28I', 750.00),
(10, 4, 4, '2024-01-19 23:00:00', '30J', 800.00),
(11, 4, 5, '2024-01-20 14:00:00', '32K', 850.00),
(12, 5, 1, '2024-01-21 15:00:00', '34L', 900.00),
(13, 5, 2, '2024-01-22 16:00:00', '36M', 950.00),
(14, 5, 3, '2024-01-23 17:00:00', '38N', 1000.00),
(15, 5, 4, '2024-01-24 18:00:00', '40O', 1050.00);
