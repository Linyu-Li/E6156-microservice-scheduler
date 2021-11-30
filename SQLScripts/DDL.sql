drop schema if exists schedule;
create schema schedule;
use schedule;

create table if not exists timeSlot
(
	Id int not null
		primary key,
	Year varchar(4) null,
	Month varchar(2) null,
	Day varchar(2) null,
	StartTime time null,
	EndTime time null
);
alter table timeSlot modify Id int auto_increment;

create table if not exists availability
(
	Id int not null
		primary key,
	userId int not null,
	timeId int not null
);
alter table availability modify Id int auto_increment;
