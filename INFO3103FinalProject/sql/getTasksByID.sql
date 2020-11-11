DELIMITER //
DROP PROCEDURE IF EXISTS getTasksByID //

CREATE PROCEDURE getTasksByID(in lstID int, in tskID int)
begin
	select * from Tasks where ListID = lstID AND TaskID = tskID;
end//
DELIMITER ;
