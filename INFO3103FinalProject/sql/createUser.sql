DELIMITER //
DROP PROCEDURE IF EXISTS createUser //

CREATE PROCEDURE createUser( in	userNameIn VARCHAR(64),	userEmailIn varchar(64)	)
	begin
		insert into Users (UserName, email) 
			values (userNameIn, userEmailIn);
	end//
DELIMITER ;
	
