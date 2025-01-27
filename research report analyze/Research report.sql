drop database if exists report;
create database report;
use report;
ALTER DATABASE report CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;




create table if not exists USER(
                                   User_id int auto_increment PRIMARY KEY ,
                                   Name VARCHAR(100),
                                   Pass_word VARCHAR(100)

);

create table if not exists RECORD(
                                     Record_id int auto_increment primary key,
                                     User_id int not null ,
                                     Generate_data DATE,
                                     Company_name VARCHAR(100),
                                     News_number INT not null,
                                     foreign key (User_id) references USER(user_id)
                                         ON DELETE cascade On update CASCADE
);


create table if not exists RESULT(
                                     Result_id int auto_increment primary key,
                                     Record_id int unique not null,
                                     report_content LONGTEXT NOT NULL,
                                     FOREIGN KEY (Record_id) REFERENCES RECORD(Record_id)
                                         ON DELETE CASCADE ON UPDATE CASCADE

);
create table if not exists NEWS(
                                   News_id INT primary key AUTO_INCREMENT,
                                   Record_id int  not null,
                                   News_link VARCHAR(200),
                                   content LONGTEXT NOT NULL,
                                   FOREIGN KEY (Record_id) REFERENCES RECORD(Record_id)
                                       ON UPDATE CASCADE ON DELETE CASCADE

);


INSERT INTO USER(User_id, Name, Pass_word)
VALUE
(1,'Warren Edward Buffett','1234');

INSERT INTO RECORD (User_id, Generate_data, Company_name, News_number)
VALUES (1, '2024-12-24', 'GS', 1);




