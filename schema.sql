drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  environment text not null,
  name text not null,
  type text not null,
  format text not null,
  initial text not null,
  delay integer not null,
  next integer not null,
  rule text not null
);