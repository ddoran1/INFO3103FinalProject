delimiter //

drop procedure if exists updateTaskCompleteness //

create procedure updateTaskCompleteness(in usID int,in lID int, in tID int, in cIn int)
	begin
	if(select ListID from ToDoLists where (UserID = usID and ListID = lID)) then
		 UPDATE Tasks set Complete = cIn where TaskID = tID;
		 END IF;
	end //
delimiter ;
