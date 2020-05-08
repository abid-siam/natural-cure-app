
CREATE TABLE IF NOT EXISTS `user`(
    username VARCHAR(20),
    password CHAR(64),
    fname VARCHAR(20),
    lname VARCHAR(20),
    sex VARCHAR(6), -- needed for API algorithm 
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
CREATE TABLE IF NOT EXISTS `administrator`( 
    username VARCHAR(20),
    password CHAR(64),
    fname CHAR(20),
    lname CHAR(20),
    title VARCHAR(20),
    PRIMARY KEY(username)
);

-- row created after a diagnosis session
CREATE TABLE IF NOT EXISTS `treatment`(
    illness VARCHAR(128),
    remedy VARCHAR(1024),
	PRIMARY KEY(illness)
);


CREATE TABLE IF NOT EXISTS `diagnosis`(
    recordID int NOT NULL AUTO_INCREMENT,
    username VARCHAR(20), -- user that initiates the diagnosis 
    symptoms VARCHAR(1024),  
    illness VARCHAR(128),
    illness2 VARCHAR(128),
    illness3 VARCHAR(128),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(recordID)
);


-- row created after a user uploads a document 
CREATE TABLE IF NOT EXISTS `document`(
    documentID int NOT NULL AUTO_INCREMENT,
    documentOwner VARCHAR(20), -- user that uploads the document
    filePath VARCHAR(2048), 
    description VARCHAR(1024),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(documentID),
    FOREIGN KEY (documentOwner) REFERENCES `user`(username)
);

