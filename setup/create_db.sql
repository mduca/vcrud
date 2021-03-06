CREATE TABLE CONTACT (
  [id] INTEGER PRIMARY KEY, 
  [name] text, 
  [number] integer, 
  [date] TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE STATE (
  [id] INTEGER PRIMARY KEY, 
  [key] text, 
  [value] text, 
  [saved_at] TEXT DEFAULT CURRENT_TIMESTAMP
);

-- CREATE TABLE CONTACTS ([id] INTEGER PRIMARY KEY,[Name] text, [Number] integer, [created_at] TEXT DEFAULT CURRENT_TIMESTAMP, [updated_at] TEXT DEFAULT CURRENT_TIMESTAMP)
