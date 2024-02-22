import sqlite3

db_file = "databases/immoweb.sqlite"
connection = sqlite3.connect(db_file)

cursor = connection.cursor()


cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS immoweb (
    id INTEGER,
    id_hash TEXT,
    category TEXT,
    address TEXT,
    zip TEXT,
    city TEXT,
    price TEXT,
    epc TEXT,
    picture_url TEXT,
    listing_url TEXT,
    nr_rooms INTEGER,
    listing_type TEXT,
    user_id INTEGER,
    PRIMARY KEY (id, user_id)
);
"""
)

connection.commit()
connection.close()

print(f"Table 'immoweb' created in the file '{db_file}'.")
