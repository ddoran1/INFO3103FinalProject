delimiter //

drop procedure if exists changeListTitle//

create procedure changeListTitle(
	in
	newName varchar(64),
	usID int,
	lID int
)
	begin
		UPDATE ToDoLists SET Title = newName where (ListID = lID and UserID = usID);
	end //
delimiter ;
