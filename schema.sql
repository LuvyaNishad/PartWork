DROP DATABASE IF EXISTS jobdb;
CREATE DATABASE jobdb;
USE jobdb;

CREATE TABLE Student (
    StudentID INT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    AcademicAffiliation VARCHAR(100),
    ReliabilityScore NUMERIC(3, 2) DEFAULT 5.00,
    Street VARCHAR(100),
    City VARCHAR(50),
    State VARCHAR(50),
    Zipcode VARCHAR(10) NOT NULL,
    CHECK (ReliabilityScore BETWEEN 0.00 AND 5.00)
);

CREATE TABLE Employer (
    EmployerID VARCHAR(10) PRIMARY KEY,
    BusinessName VARCHAR(100) NOT NULL,
    VerifiedIdentity CHAR(1) DEFAULT 'N',
    TrustScore NUMERIC(3,2),
    CHECK (VerifiedIdentity IN ('Y', 'N')),
    CHECK (TrustScore BETWEEN 0.00 AND 5.00)
);

CREATE TABLE Application (
    ApplicationID VARCHAR(20) PRIMARY KEY,
    ApplicationDate DATE NOT NULL,
    Status VARCHAR(20),
    CHECK (Status IN ('Pending', 'Accepted', 'Rejected', 'Withdrawn'))
);

CREATE TABLE Opportunity (
    OppID VARCHAR(20) PRIMARY KEY,
    RequiredStudents INT DEFAULT 1,
    Type VARCHAR(20),
    RoleTitle VARCHAR(100) NOT NULL,
    Description VARCHAR(500),
    Status VARCHAR(20) DEFAULT 'Pending',
    City VARCHAR(50),
    State VARCHAR(50),
    Zipcode VARCHAR(10),
    CHECK (Type IN ('Internship', 'Freelance', 'Full-time', 'Part-time')),
    CHECK (Status IN ('Pending', 'Active', 'Assigned', 'Completed', 'Funded'))
);

CREATE TABLE SkillTags (
    StudentID INT, 
    Skill VARCHAR(50),
    PRIMARY KEY (StudentID, Skill),
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID) 
);

CREATE TABLE RequiredSkills (
    OppID VARCHAR(20), 
    Skill VARCHAR(50),
    PRIMARY KEY (OppID, Skill),
    FOREIGN KEY (OppID) REFERENCES Opportunity(OppID)
);

CREATE TABLE Posts (
    EmployerID VARCHAR(10),
    OppID VARCHAR(20) PRIMARY KEY,
    FOREIGN KEY (EmployerID) REFERENCES Employer(EmployerID),
    FOREIGN KEY (OppID) REFERENCES Opportunity(OppID)
);

CREATE TABLE Job_application (
    StudentID INT,
    ApplicationID VARCHAR(20) PRIMARY KEY,
    OppID VARCHAR(20),
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
    FOREIGN KEY (ApplicationID) REFERENCES Application(ApplicationID),
    FOREIGN KEY (OppID) REFERENCES Opportunity(OppID)
);

INSERT INTO Student (StudentID, FirstName, LastName, AcademicAffiliation, ReliabilityScore, Street, City, State, Zipcode)
VALUES
(2024111, 'Arsh', 'Ahluwalia', 'IIIT Delhi', 4.90, 'Okhla Phase III', 'New Delhi', 'Delhi', '110020'),
(2024321, 'Luvya', 'Nishad', 'IIIT Delhi', 4.85, 'Govind Puri', 'New Delhi', 'Delhi', '110019'),
(2024322, 'Madhav', 'Gautam', 'IIIT Delhi', 4.80, 'Kalkaji', 'New Delhi', 'Delhi', '110019');

INSERT INTO Employer (EmployerID, BusinessName, VerifiedIdentity, TrustScore)
VALUES
('E_ZOM', 'Zomato Ltd', 'Y', 4.7),
('E_SWIG', 'Swiggy Instamart', 'N', 4.2);

INSERT INTO Opportunity (OppID, RequiredStudents, Type, RoleTitle, Description, Status, City, State, Zipcode)
VALUES
('OP_WEB', 2, 'Internship', 'React Developer', 'Build dashboard for Zomato delivery partners', 'Active', 'New Delhi', 'Delhi', '110020'),
('OP_DES', 1, 'Freelance', 'UI/UX Designer', 'Redesign checkout flow for Swiggy', 'Pending', 'Remote', 'NA', '000000');

INSERT INTO Application (ApplicationID, ApplicationDate, Status)
VALUES
('APP_001', '2025-02-01', 'Accepted'),
('APP_002', '2025-02-02', 'Pending'),
('APP_003', '2025-02-03', 'Pending');

INSERT INTO Posts (EmployerID, OppID)
VALUES
('E_ZOM', 'OP_WEB'),
('E_SWIG', 'OP_DES');

INSERT INTO Job_application (StudentID, ApplicationID, OppID)
VALUES
(2024111, 'APP_001', 'OP_WEB'),
(2024321, 'APP_002', 'OP_WEB'),
(2024322, 'APP_003', 'OP_DES');

INSERT INTO SkillTags (StudentID, Skill)
VALUES
(2024111, 'React'),
(2024111, 'Java'),
(2024321, 'SQL'),
(2024321, 'Python'),
(2024322, 'Figma'),
(2024322, 'Illustrator');

INSERT INTO RequiredSkills (OppID, Skill)
VALUES
('OP_WEB', 'React'),
('OP_WEB', 'Java'),
('OP_DES', 'Figma');