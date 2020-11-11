DELIMITER //
DROP PROCEDURE IF EXISTS getListByID //

CREATE PROCEDURE getListByID(IN listIDIn INT)
begin
	SELECT * from ToDoLists
		where ListID = listIDIn;
end//
DELIMITER ;
