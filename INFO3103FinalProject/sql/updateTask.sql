DELIMITER //
DROP PROCEDURE IF EXISTS updateTask //

CREATE PROCEDURE updateTask(in usID int, in lID int, in tskID int, in taskIn varchar(64) )
BEGIN
		if(select ListID from ToDoLists where (UserID = usID and ListID = lID)) then
			 UPDATE Tasks set Task = taskIn where TaskID = tskID;
		END IF;
END//
DELIMITER ;
