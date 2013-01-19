drop table if exists file_log;
create table file_log (
  id integer primary key autoincrement,
  file_path string not null,
  recorded timestamp default current_timestamp,
  activity_type string not null
);

drop table if exists system_info;
create table system_info (
  version string primary key,
  updated timestamp default current_timestamp
);
