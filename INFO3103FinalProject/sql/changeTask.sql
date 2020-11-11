delimiter //

drop procedure if exists changeTask//

create procedure changeTask(
	in
	newName varchar(64),
	usID varchar(64),
	lID int,
	tID int
)
	begin
		if (select ListID from ToDoLists where (UserID = usID and ListID = lID)) then
			UPDATE Tasks SET Task = newName where (ListID = lID and TaskID = tID);
		end if;
	end //
delimiter ;
