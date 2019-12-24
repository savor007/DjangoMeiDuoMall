create table StudentBasicData (
	id int unsigned not null auto_increment primary key,
	name varchar(70) not null default "",
	gender enum("male","female","unknown") default "unknown",
	height decimal(5,2) not null, 
  birthday datetime not null,
	class int unsigned not null default 1
);

create table ClassName (
	id int unsigned not null auto_increment primary key,
	class_name varchar(45) not null default ""
)

insert into StudentBasicData values (0,"hongxiaopi","female",1.69,'1989-07-01',1);

	insert into StudentBasicData values (0,"gegewu","male",1.78,"1951-06-06",1,"dalian");

	alter table StudentBasicData modify birthday date not null;
	alter table StudentBasicData add place varchar(40) not null default "";
	alter table StudentBasicData modify class varchar(40) not null;
insert into ClassName values (0,"1");
	-----+
| id       | int(10) unsigned                | NO   | PRI | NULL    | auto_increment |
| name     | varchar(70)                     | NO   |     |         |                |
| gender   | enum('male','female','unknown') | YES  |     | unknown |                |
| height   | decimal(5,2)                    | NO   |     | NULL    |                |
| birthday | date                            | NO   |     | NULL    |                |
| class    | varchar(40)                     | NO   |     | NULL    |                |
| place    | varchar(40)                     | NO   |     |         |                |
+----------+---------------------------------+------+-----+---------+----------------+
alter table StudentBasicData modify class int unsigned not null default 1

insert into StudentBasicData (name,gender,height,birthday) values ("少臣",1,1.65,"1999-07-01"),("大侠",1,1.91,"1991-07-11"),("女神",2,1.75,"1968-07-01")

select name as 姓名,birthday as 出生日期,gender as 性别 from StudentBasicData where height>1.8

alter table StudentBasicData add last_login_time datetime not null default '2019-01-28 20:01:41';

alter table StudentBasicData add is_deleted bit not null default 0;

update StudentBasicData set is_deleted=1 where name="gegewu";

create table student (
	id int unsigned not null auto_increment primary key,
	name varchar(62) not null default "",
	age tinyint unsigned not null default 0,
  gender enum("male","female","neutral","unknown") not null default "unknown",
	height decimal(5,2),
	cls_id int unsigned default 0,
	is_delete bit(1) default 0
);

create table classes (id int unsigned primary key auto_increment not null, name varchar(45) default "");
insert into student values (
	null,"zhangfei",25,"male",1.85,1,0
);
insert into student values 
	(null,"8yuwang",21,"male",null,1,0);

	update student set is_delete=1 where id=3;
		select * from student where (age between 23 and 58) and gender="female" order by age asc;

		select * from student where (age between 23 and 58) and gender="male" order by height desc;

		select * from student where age between 10 and 99 order by height desc, age asc;

		update student set is_delete=1 where id=11;

			
select cls_id, count(*) from student group by cls_id;

select cls_id, group_concat(name) from student group by cls_id;
select gender,group_concat(name),round(avg(age),1) from student group by gender having avg(age)>30;

select gender,group_concat(id),round(avg(age),1) from student group by gender having avg(age)<30;

select * from student where gender=2 order by height desc limit 2;