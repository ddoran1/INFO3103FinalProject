delimiter //

drop procedure if exists changeListDescription//

create procedure changeListDescription(in descr varchar(64), in usID int, lID int)
	begin
		UPDATE ToDoLists SET Description = descr where (ListID = lID and UserID = usID);
	end //
delimiter ;
