import sqlite3

# Connect to the SQLite database (create it if it doesn't exist)
db_file = 'user_data.sqlite'
connection = sqlite3.connect(db_file)
cursor = connection.cursor()

# Create the specified table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_data (
        user_id INTEGER NOT NULL PRIMARY KEY,
        full_name TEXT,
        search_type TEXT,
        budget INTEGER,
        location TEXT,
        nr_rooms INTEGER
    )
''')

# Commit changes and close the connection
connection.commit()
connection.close()

print(f"Table 'your_table_name' created in the file '{db_file}'.")

