delimiter //
DROP PROCEDURE IF EXISTS getUserByName//

CREATE PROCEDURE getUserByName(IN name VARCHAR(64))
BEGIN
	select UserID from Users
		where UserName = name;
END//

delimiter ;
