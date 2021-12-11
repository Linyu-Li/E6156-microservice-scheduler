create table if not exists schedule.timeSlot
(
	Id int not null
		primary key,
	Year varchar(4) null,
	Month varchar(2) null,
	Day varchar(2) null,
	StartTime time null,
	EndTime time null
);

create table if not exists schedule.availability
(
	Id int not null
		primary key,
	userId int not null,
	timeId int not null
);

create unique index timeSlot_Year_Month_Day_StartTime_EndTime_uindex
   on schedule.timeSlot (Year, Month, Day, StartTime, EndTime);
