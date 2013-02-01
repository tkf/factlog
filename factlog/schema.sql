drop table if exists access_log;
create table access_log (
  id integer primary key autoincrement,
  file_path text not null,
  file_point integer,
  file_exists integer not null default 1,
  program text,
  recorded timestamp default current_timestamp,
  access_type integer not null
);

drop table if exists factlog_info;
create table factlog_info (
  factlog_version text not null,
  schema_version text not null,
  updated timestamp default current_timestamp
);
