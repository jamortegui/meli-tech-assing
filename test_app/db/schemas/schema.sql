DROP TABLE IF EXISTS items;

CREATE TABLE items (
  pk SERIAL PRIMARY KEY,
  site VARCHAR NOT NULL,
  id INTEGER NOT NULL,
  price INTEGER,
  start_time VARCHAR,
  name VARCHAR,
  description VARCHAR,
  nickname VARCHAR
);