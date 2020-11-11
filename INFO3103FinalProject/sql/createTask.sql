DELIMITER //
DROP PROCEDURE IF EXISTS createTask//

CREATE PROCEDURE createTask(in usID int, in lID int, in taskIn varchar(64))
BEGIN
	INSERT INTO Tasks (Task, ListID) values (taskIn,
		(SELECT ListID FROM ToDoLists WHERE (UserID = usID AND ListID = lID))
	);

END //
DELIMITER ;
