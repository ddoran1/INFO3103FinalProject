delimiter //

drop procedure if exists changeUserName //

create procedure changeUserName(
	in
	oldName varchar(64),
	newName varchar(64)
)
	begin
		if(select count(*) from ToDoLists where UserID = oldName) > 0 then
			update ToDoLists set UserID = newName where UserID = oldName;
		 
		end if;
		if ( not exists(select 1 from Users where (UserID = newName))) then
			update Users set UserID = newName where UserID = oldName;
			select * from Users;
		end if;
		
	end //
delimiter ;
