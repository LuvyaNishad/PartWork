-- =======================================================
-- 1. INITIALIZE DATABASE
-- =======================================================
DROP DATABASE IF EXISTS jobdb;
CREATE DATABASE jobdb;
USE jobdb;

-- =======================================================
-- 2. CREATE TABLES
-- =======================================================

CREATE TABLE Student (
    StudentID INT AUTO_INCREMENT PRIMARY KEY,
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
    EmployerID INT AUTO_INCREMENT PRIMARY KEY,
    BusinessName VARCHAR(100) NOT NULL,
    VerifiedIdentity CHAR(1) DEFAULT 'N',
    TrustScore NUMERIC(3,2),
    CHECK (VerifiedIdentity IN ('Y', 'N')),
    CHECK (TrustScore BETWEEN 0.00 AND 5.00)
);

CREATE TABLE Application (
    ApplicationID INT AUTO_INCREMENT PRIMARY KEY,
    ApplicationDate DATE NOT NULL,
    Status VARCHAR(20),
    CHECK (Status IN ('Pending', 'Accepted', 'Rejected', 'Withdrawn'))
);

CREATE TABLE Opportunity (
    OppID INT AUTO_INCREMENT PRIMARY KEY,
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
    OppID INT, 
    Skill VARCHAR(50),
    PRIMARY KEY (OppID, Skill),
    FOREIGN KEY (OppID) REFERENCES Opportunity(OppID)
);

CREATE TABLE Posts (
    EmployerID INT NOT NULL,
    OppID INT PRIMARY KEY,
    FOREIGN KEY (EmployerID) REFERENCES Employer(EmployerID),
    FOREIGN KEY (OppID) REFERENCES Opportunity(OppID)
);

CREATE TABLE Assigned_to (
    StudentID INT,
    OppID INT,
    PRIMARY KEY (StudentID, OppID),
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
    FOREIGN KEY (OppID) REFERENCES Opportunity(OppID)
);

CREATE TABLE Job_application (
    StudentID INT NOT NULL,
    ApplicationID INT PRIMARY KEY,
    OppID INT NOT NULL,
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
    FOREIGN KEY (ApplicationID) REFERENCES Application(ApplicationID),
    FOREIGN KEY (OppID) REFERENCES Opportunity(OppID),
    UNIQUE (StudentID, OppID)
);

CREATE TABLE MilestoneLedger (
    OppID INT,
    MilestoneID INT AUTO_INCREMENT PRIMARY KEY,
    Payout DECIMAL(10, 2),
    Deadline DATE,
    Description VARCHAR(255),
    ApprovalStatus VARCHAR(20),
    SubmissionDate DATE,
    FOREIGN KEY (OppID) REFERENCES Opportunity(OppID),
    CHECK (ApprovalStatus IN ('Pending', 'Approved', 'Rejected'))
);

CREATE TABLE ProjWallet (
    OppID INT PRIMARY KEY,
    TotalAmount DECIMAL(12, 2) NOT NULL,
    Status VARCHAR(20),
    FOREIGN KEY (OppID) REFERENCES Opportunity(OppID),
    CHECK (Status IN ('Funded', 'Escrow', 'Released'))
);

CREATE TABLE Employer_Payment_Method (
    payment_method_id INT PRIMARY KEY AUTO_INCREMENT, 
    employer_id INT NOT NULL,
    method_type VARCHAR(50) NOT NULL,    
    payment_token VARCHAR(255) NOT NULL, 
    is_default BOOLEAN DEFAULT TRUE,
    card_brand VARCHAR(50) NULL, 
    last_four CHAR(4) NULL,         
    exp_month INT NULL,
    exp_year INT NULL,
    FOREIGN KEY (employer_id) REFERENCES Employer(EmployerID)
);

CREATE TABLE Student_Payout_Method (
    payout_method_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    method_type VARCHAR(50) NOT NULL,
    payout_token VARCHAR(255) NOT NULL,
    is_default BOOLEAN DEFAULT TRUE,
    bank_name VARCHAR(100) NULL,   
    FOREIGN KEY (student_id) REFERENCES Student(StudentID)
);

CREATE TABLE Transaction_Ledger (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    wallet_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL, 
    transaction_type VARCHAR(20) NOT NULL, 
    transaction_hash VARCHAR(255) UNIQUE NOT NULL, 
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method_id INT NULL, 
    payout_method_id INT NULL,  
    milestone_id INT NULL,  
    FOREIGN KEY (wallet_id) REFERENCES ProjWallet(OppID),
    FOREIGN KEY (payment_method_id) REFERENCES Employer_Payment_Method(payment_method_id),
    FOREIGN KEY (payout_method_id) REFERENCES Student_Payout_Method(payout_method_id),
    FOREIGN KEY (milestone_id) REFERENCES MilestoneLedger(MilestoneID),
    CHECK (transaction_type IN ('Payout', 'Deposit', 'Refund'))
);

CREATE TABLE PerformanceLedger (
    ApplicationID INT,
    RecordID INT AUTO_INCREMENT PRIMARY KEY,
    ImpactScore INT,
    ReviewerRole VARCHAR(10),
    MetricType VARCHAR(50),
    ReviewTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FeedbackDescription VARCHAR(255),
    FOREIGN KEY (ApplicationID) REFERENCES Application(ApplicationID),
    CHECK (ReviewerRole IN ('Student', 'Employer', 'System')),
    CHECK (ImpactScore BETWEEN 0 AND 100)
);

CREATE TABLE Interview (
    ApplicationID INT PRIMARY KEY,
    ScheduledTime TIMESTAMP NOT NULL,
    MeetingType VARCHAR(20),
    ApplicationStatus VARCHAR(20),
    FOREIGN KEY (ApplicationID) REFERENCES Application(ApplicationID),
    CHECK (MeetingType IN ('Zoom', 'In-Person', 'Google Meet')),
    CHECK (ApplicationStatus IN ('Scheduled', 'Completed', 'Cancelled'))
);

-- =======================================================
-- 3. CREATE INDEXES
-- =======================================================

CREATE INDEX idx_student_lastname ON Student(LastName);
CREATE INDEX idx_student_Zipcode ON Student(Zipcode);
CREATE INDEX idx_employer_name ON Employer(BusinessName);
CREATE INDEX idx_opp_roletitle ON Opportunity(RoleTitle);
CREATE INDEX idx_app_status ON Application(Status);

-- =======================================================
-- 4. INSERT FRESH DUMMY DATA
-- =======================================================

-- 1. Students
INSERT INTO Student (StudentID, FirstName, LastName, AcademicAffiliation, ReliabilityScore, Street, City, State, Zipcode) VALUES
(101, 'Rohit', 'Sharma', 'Delhi University', 4.80, '12 Main St', 'Delhi', 'DL', '110001'),
(102, 'Aanya', 'Gupta', 'DTU', 4.90, '45 Tech Blvd', 'Delhi', 'DL', '110021');

-- 2. Employers
INSERT INTO Employer (EmployerID, BusinessName, VerifiedIdentity, TrustScore) VALUES
(501, 'TechCorp India', 'Y', 4.50),
(502, 'InnovateTech Solutions', 'Y', 4.80);

-- 3. Applications (Base Table)
INSERT INTO Application (ApplicationID, ApplicationDate, Status) VALUES
(401, CURDATE(), 'Pending'),
(402, CURDATE(), 'Accepted'),
(403, CURDATE(), 'Withdrawn');

-- 4. Opportunities
INSERT INTO Opportunity (OppID, RequiredStudents, Type, RoleTitle, Description, Status, City, State, Zipcode) VALUES
(15, 1, 'Internship', 'Frontend Intern', 'React development', 'Active', 'Delhi', 'DL', '110001'),
(16, 2, 'Full-time', 'Backend Developer', 'Python API dev', 'Active', 'Mumbai', 'MH', '400053'),
(20, 1, 'Part-time', 'Marketing Specialist', 'SEO work', 'Pending', 'Pune', 'MH', '411014');

-- 5. Skill Tags & Required Skills
INSERT INTO SkillTags (StudentID, Skill) VALUES (101, 'React'), (101, 'Python');
INSERT INTO RequiredSkills (OppID, Skill) VALUES (15, 'React'), (16, 'Python');

-- 6. Posts (Linking Employer to Opp)
INSERT INTO Posts (EmployerID, OppID) VALUES (501, 15), (501, 16), (502, 20);

-- 7. Assigned_to (Student assigned to an accepted Opp)
INSERT INTO Assigned_to (StudentID, OppID) VALUES (102, 16);

-- 8. Job_application (Linking Student, Application, and Opp)
INSERT INTO Job_application (StudentID, ApplicationID, OppID) VALUES
(101, 401, 15),
(102, 402, 16),
(101, 403, 20);

-- 9. Milestone Ledger
INSERT INTO MilestoneLedger (OppID, MilestoneID, Payout, Deadline, Description, ApprovalStatus, SubmissionDate) VALUES
(16, 88, 10000.00, '2026-04-01', 'Phase 1 Delivery', 'Approved', '2026-03-15'),
(16, 89, 15000.00, DATE_SUB(CURDATE(), INTERVAL 2 DAY), 'Phase 2', 'Pending', NULL);

-- 10. ProjWallet
INSERT INTO ProjWallet (OppID, TotalAmount, Status) VALUES (16, 50000.00, 'Funded');

-- 11. Performance Ledger (Impact Score is 0-100 here)
INSERT INTO PerformanceLedger (ApplicationID, ImpactScore, ReviewerRole, MetricType) VALUES
(402, 85, 'Employer', 'Code Quality'),
(402, 90, 'Employer', 'Communication');

-- 12. Interview
INSERT INTO Interview (ApplicationID, ScheduledTime, MeetingType, ApplicationStatus) VALUES
(401, DATE_ADD(NOW(), INTERVAL 3 DAY), 'Zoom', 'Scheduled');