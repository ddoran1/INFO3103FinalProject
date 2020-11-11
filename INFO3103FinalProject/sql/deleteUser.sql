DELIMITER //
DROP PROCEDURE IF EXISTS deleteUser//

CREATE PROCEDURE deleteUser (in usName varchar(64))
begin

	DELETE from Users
		WHERE UserName = usName;

end//
DELIMITER ;
