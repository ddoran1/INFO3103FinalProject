delimiter //
drop procedure if exists postList//

create procedure postList(in usID varchar(64), title varchar(64), descr varchar(64))
begin
	insert into ToDoLists (UserID, Title, Description) values
		(usID, title, descr);
end//
delimiter ;
