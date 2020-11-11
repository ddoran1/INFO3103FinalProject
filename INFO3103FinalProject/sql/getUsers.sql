delimiter //
DROP PROCEDURE IF EXISTS getUsers//

CREATE PROCEDURE getUsers()
BEGIN
	select * from Users;
END//

delimiter ;
