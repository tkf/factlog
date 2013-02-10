-- Copyright (c) 2013- Takafumi Arakaki

-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU Lesser General Public License as
-- published by the Free Software Foundation, either version 3 of the
-- License.

-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU Lesser General Public License for more details.

-- You should have received a copy of the GNU Lesser General Public License
-- along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
