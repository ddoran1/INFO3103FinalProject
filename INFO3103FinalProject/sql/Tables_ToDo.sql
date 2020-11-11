create table Users
(
	UserID int unique not null auto_increment primary key,
	UserName VARCHAR(64) not null unique,
	email varchar(64) not null unique
);

create table ToDoLists
(
	ListID int unique not null AUTO_INCREMENT PRIMARY KEY,
	Title VARCHAR(64),
	Description VARCHAR(64),
	UserID int NOT NULL,
	FOREIGN KEY(UserID) REFERENCES Users(UserID) ON DELETE CASCADE
);

create table Tasks
(
	TaskID int not null auto_increment primary key,
	ListID int not null,
	Task VARCHAR(64),
	Complete boolean DEFAULT 0,
	FOREIGN KEY(ListID) REFERENCES ToDoLists(ListID) ON DELETE CASCADE
);

deleting tables:

drop table Tasks;
drop table ToDoLists;
drop table Users;
