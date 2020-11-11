DELIMITER //
DROP PROCEDURE IF EXISTS getTasksByListID //

CREATE PROCEDURE getTasksByListID(in lstID int)
begin
	select * from Tasks where ListID = lstID;
end//
DELIMITER ;
