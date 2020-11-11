DELIMITER //
DROP PROCEDURE IF EXISTS getLastList //

CREATE PROCEDURE getLastList(in usID int)
begin
	select ListID from ToDoLists where UserID = usID order by ListID desc limit 1;
end//
DELIMITER ;
