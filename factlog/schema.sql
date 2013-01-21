drop table if exists file_log;
create table file_log (
  id integer primary key autoincrement,
  file_path string not null,
  file_point integer,
  file_exists integer not null default 1,
  recorded timestamp default current_timestamp,
  activity_type string not null
);

drop table if exists system_info;
create table system_info (
  factlog_version string not null,
  schema_version string not null,
  updated timestamp default current_timestamp
);
