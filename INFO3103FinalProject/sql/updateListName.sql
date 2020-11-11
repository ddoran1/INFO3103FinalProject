DELIMITER //
DROP PROCEDURE IF EXISTS updateListName //

CREATE PROCEDURE updateListName(in lID int, usID int, in title varchar(64) )
BEGIN
	UPDATE ToDoLists SET Title = title
		WHERE (ListID = lID AND UserID = usID);
END//
DELIMITER ;
