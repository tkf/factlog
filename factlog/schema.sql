drop table if exists access_log;
create table access_log (
  id integer primary key autoincrement,
  file_path string not null,
  file_point integer,
  file_exists integer not null default 1,
  recorded timestamp default current_timestamp,
  access_type string not null
);

drop table if exists factlog_info;
create table factlog_info (
  factlog_version string not null,
  schema_version string not null,
  updated timestamp default current_timestamp
);
