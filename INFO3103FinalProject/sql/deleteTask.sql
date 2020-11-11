DELIMITER //
DROP PROCEDURE if exists deleteTask //

CREATE PROCEDURE deleteTask(in lID int, in tskID int)
BEGIN
	DELETE FROM Tasks WHERE ListID = lID and TaskID = tskID;
END//
DELIMITER ;
