import sqlite3

# Connect to the SQLite database (create it if it doesn't exist)
db_file = "databases/jam.sqlite"
connection = sqlite3.connect(db_file)
cursor = connection.cursor()

# Create the 'jam' table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS jam (
        id INTEGER,
        id_hash TEXT,
        category TEXT,
        address TEXT,
        zip INTEGER,
        city TEXT,
        price TEXT,
        epc TEXT,
        picture_url TEXT,
        listing_url TEXT,
        nr_rooms INTEGER,
        listing_type TEXT,
        user_id INTEGER,
        PRIMARY KEY (id, user_id)
    )
"""
)

# Commit changes and close the connection
connection.commit()
connection.close()

print(f"Table 'jam' created in the file '{db_file}'.")
