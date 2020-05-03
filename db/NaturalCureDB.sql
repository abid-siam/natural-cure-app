DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user`(
    username VARCHAR(20),
    password CHAR(64),
    fname VARCHAR(20),
    lname VARCHAR(20),
    gender VARCHAR(6), -- needed for API algorithm 
    addr_street VARCHAR(50),
    addr_city VARCHAR(25),
    addr_state CHAR(2),
    addr_zip CHAR(5),
    email VARCHAR(320),
    dob DATE,
    period_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- time subscription is made or renewed 
    subscribed Boolean,
    mfaEnabled Boolean,
    PRIMARY KEY (username)
);

-- login /admin to manage users and subscriptions 
DROP TABLE IF EXISTS `administrator`;
CREATE TABLE IF NOT EXISTS `administrator`( 
    username VARCHAR(20),
    password CHAR(64),
    fname CHAR(20),
    lname CHAR(20),
    title VARCHAR(20),
    PRIMARY KEY(username)
);

-- row created after a diagnosis session
DROP TABLE IF EXISTS `diagnosis`;
CREATE TABLE IF NOT EXISTS `diagnosis`(
    recordID int NOT NULL AUTO_INCREMENT,
    username VARCHAR(20), -- user that initiates the diagnosis 
    symptoms VARCHAR(1024), -- comma seperated string containing symptom_ids provided by the user 
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(recordID)
);

-- row created after api returns diagnosis and treatment is chosen
DROP TABLE IF EXISTS `condition`;
CREATE TABLE IF NOT EXISTS `condition`(
    recordID int, -- corresponds to a diagnosis made 
    conditionID VARCHAR(10), -- corresponds to the output condition id from the api 
    username VARCHAR(20),
    probability DECIMAL(9,8),
    treatment VARCHAR(1024), -- may need to be reorganized (maybe a seperate table for treatments?)
    PRIMARY KEY (recordID, conditionID),
    FOREIGN KEY (recordID) REFERENCES `diagnosis`(recordID),
    FOREIGN KEY (username) REFERENCES `user`(username)
);