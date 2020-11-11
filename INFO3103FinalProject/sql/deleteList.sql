DELIMITER //
DROP PROCEDURE if exists deleteList //

CREATE PROCEDURE deleteList(in lID int,usID int)
BEGIN
	DELETE FROM ToDoLists
		WHERE (ListID = lID
		AND UserID = usID);

	DELETE FROM Tasks
		WHERE ListID = lID;
END//
DELIMITER ;
