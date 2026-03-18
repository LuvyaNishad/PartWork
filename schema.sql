CREATE DATABASE IF NOT EXISTS jobdb;
USE jobdb;

DROP TABLE IF EXISTS Transaction_Ledger;
DROP TABLE IF EXISTS Student_Payout_Method;
DROP TABLE IF EXISTS Employer_Payment_Method;
DROP TABLE IF EXISTS ProjWallet;
DROP TABLE IF EXISTS MilestoneLedger;
DROP TABLE IF EXISTS PerformanceLedger;
DROP TABLE IF EXISTS Interview;
DROP TABLE IF EXISTS Job_application;
DROP TABLE IF EXISTS Assigned_to;
DROP TABLE IF EXISTS Posts;
DROP TABLE IF EXISTS RequiredSkills;
DROP TABLE IF EXISTS SkillTags;
DROP TABLE IF EXISTS Opportunity;
DROP TABLE IF EXISTS Application;
DROP TABLE IF EXISTS Employer;
DROP TABLE IF EXISTS Student;

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
    TrustScore NUMERIC(3, 2),
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
    CHECK (ApprovalStatus IN ('Pending', 'Approved', 'Rejected', 'Paid'))
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

CREATE INDEX idx_student_lastname ON Student(LastName);
CREATE INDEX idx_student_Zipcode ON Student(Zipcode);
CREATE INDEX idx_employer_name ON Employer(BusinessName);
CREATE INDEX idx_opp_roletitle ON Opportunity(RoleTitle);
CREATE INDEX idx_app_status ON Application(Status);

/* ========================================================================= */
/* PART 4: COMPREHENSIVE DUMMY DATA INSERTION                                */
/* ========================================================================= */

-- 1. Insert Students (The Gig Workers)
INSERT INTO Student (StudentID, FirstName, LastName, AcademicAffiliation, ReliabilityScore, Street, City, State, Zipcode) VALUES
                                                                                                                              (2024111, 'Arsh', 'Ahluwalia', 'IIIT Delhi', 4.90, 'Okhla Phase III', 'New Delhi', 'Delhi', '110020'),
                                                                                                                              (2024321, 'Luvya', 'Nishad', 'IIIT Delhi', 4.85, 'Govind Puri', 'New Delhi', 'Delhi', '110019'),
                                                                                                                              (2024322, 'Madhav', 'Gautam', 'IIIT Delhi', 4.80, 'Kalkaji', 'New Delhi', 'Delhi', '110019'),
                                                                                                                              (2024500, 'Aisha', 'Sharma', 'IIT Delhi', 4.95, 'Hauz Khas', 'New Delhi', 'Delhi', '110016'),
                                                                                                                              (2024501, 'Rohan', 'Verma', 'DTU', 4.20, 'Rohini', 'New Delhi', 'Delhi', '110085');

-- 2. Insert Employers (The Tech Giants & Startups)
INSERT INTO Employer (EmployerID, BusinessName, VerifiedIdentity, TrustScore) VALUES
                                                                                  (1, 'Zomato Ltd', 'Y', 4.80),
                                                                                  (2, 'Swiggy Instamart', 'N', 4.20),
                                                                                  (3, 'Google India', 'Y', 5.00),
                                                                                  (4, 'Insomniac Games', 'Y', 4.90),
                                                                                  (5, 'LocalByte Tech', 'N', 3.50);

-- 3. Insert Opportunities (The Job Board)
INSERT INTO Opportunity (OppID, RequiredStudents, Type, RoleTitle, Description, Status, City, State, Zipcode) VALUES
                                                                                                                  (1, 2, 'Internship', 'React Developer', 'Build the new driver dashboard interface.', 'Active', 'New Delhi', 'Delhi', '110020'),
                                                                                                                  (2, 1, 'Freelance', 'UI/UX Designer', 'Redesign checkout flow and user journey.', 'Active', 'Remote', 'NA', '000000'),
                                                                                                                  (3, 1, 'Internship', 'Backend API Engineer', 'Optimize search algorithms for maps.', 'Active', 'Bengaluru', 'Karnataka', '560001'),
                                                                                                                  (4, 3, 'Part-time', 'Game Engine Scripter', 'Write C++ scripts for NPC behaviors.', 'Active', 'Remote', 'NA', '000000'),
                                                                                                                  (5, 1, 'Freelance', 'Database Administrator', 'Normalize local startup SQL schema.', 'Assigned', 'Gurugram', 'Haryana', '122018');

-- 4. Insert Skills Portfolio
INSERT INTO SkillTags (StudentID, Skill) VALUES
                                             (2024111, 'React'), (2024111, 'Java'), (2024111, 'Node.js'),
                                             (2024321, 'SQL'), (2024321, 'Python'), (2024321, 'UI/UX'), (2024321, 'Figma'),
                                             (2024322, 'Figma'), (2024322, 'Illustrator'), (2024322, 'CSS'),
                                             (2024500, 'C++'), (2024500, 'Java'), (2024500, 'Algorithms'),
                                             (2024501, 'SQL'), (2024501, 'MongoDB');

-- 5. Insert Required Skills for Jobs
INSERT INTO RequiredSkills (OppID, Skill) VALUES
                                              (1, 'React'), (1, 'Node.js'),
                                              (2, 'Figma'), (2, 'UI/UX'),
                                              (3, 'Java'), (3, 'Algorithms'),
                                              (4, 'C++'),
                                              (5, 'SQL');

-- 6. Link Posts (Who posted what?)
INSERT INTO Posts (EmployerID, OppID) VALUES
                                          (1, 1), (2, 2), (3, 3), (4, 4), (5, 5);

-- 7. Insert Applications (The Pipeline)
INSERT INTO Application (ApplicationID, ApplicationDate, Status) VALUES
                                                                     (1, '2026-03-01', 'Accepted'),
                                                                     (2, '2026-03-02', 'Pending'),
                                                                     (3, '2026-03-05', 'Pending'),
                                                                     (4, '2026-03-10', 'Rejected'),
                                                                     (5, '2026-03-12', 'Accepted'),
                                                                     (6, '2026-03-15', 'Pending');

-- 8. Link Job Applications (Student -> App -> Job)
INSERT INTO Job_application (StudentID, ApplicationID, OppID) VALUES
                                                                  (2024111, 1, 1), -- Arsh got the Zomato gig
                                                                  (2024321, 2, 2), -- Luvya applied for Swiggy Design
                                                                  (2024322, 3, 2), -- Madhav also applied for Swiggy Design
                                                                  (2024501, 4, 3), -- Rohan rejected from Google
                                                                  (2024321, 5, 5), -- Luvya accepted for LocalByte DB tuning
                                                                  (2024500, 6, 4); -- Aisha pending for Insomniac

-- 9. Assigned To (The Official Hires)
INSERT INTO Assigned_to (StudentID, OppID) VALUES
                                               (2024111, 1),
                                               (2024321, 5);

-- 10. Financials: Escrow Wallets
INSERT INTO ProjWallet (OppID, TotalAmount, Status) VALUES
                                                        (1, 25000.00, 'Escrow'),
                                                        (5, 8000.00, 'Released');

-- 11. Financials: Milestones
INSERT INTO MilestoneLedger (OppID, MilestoneID, Payout, Deadline, Description, ApprovalStatus, SubmissionDate) VALUES
                                                                                                                    (1, 1, 10000.00, '2026-03-20', 'Frontend Login Screen', 'Pending', NULL),
                                                                                                                    (1, 2, 15000.00, '2026-04-10', 'Dashboard Integration', 'Pending', NULL),
                                                                                                                    (5, 3, 8000.00, '2026-03-15', 'Schema Normalization to 3NF', 'Paid', '2026-03-14');

-- 12. Financials: Payment Methods
INSERT INTO Employer_Payment_Method (employer_id, method_type, payment_token) VALUES
                                                                                  (1, 'Corporate Card', 'CC_ZOMATO_9999'),
                                                                                  (5, 'UPI', 'UPI_LOCALBYTE_1111');

INSERT INTO Student_Payout_Method (student_id, method_type, payout_token) VALUES
                                                                              (2024111, 'Bank Transfer', 'BANK_ARSH_0001'),
                                                                              (2024321, 'Google Pay', 'GPAY_LUVYA_0002');

-- 13. Financials: The Transactions
INSERT INTO Transaction_Ledger (wallet_id, amount, transaction_type, transaction_hash, payment_method_id, payout_method_id, milestone_id) VALUES
                                                                                                                                              (1, 25000.00, 'Deposit', '0xDEP_ZOMATO_1122', 1, NULL, NULL),
                                                                                                                                              (5, 8000.00, 'Payout', '0xPAY_LUVYA_5566', NULL, 2, 3);                                                                                                                                        (5, 8000.00, 'Payout', '0xPAY_LUVYA_5566', NULL, 2, 3);