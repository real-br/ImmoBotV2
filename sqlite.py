import sqlite3


def get_saved_listings(db_name, table_name, user_id):
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    cur.execute(
        "SELECT id FROM {table_name} WHERE user_id='{user_id}'".format(
            table_name=table_name, user_id=user_id
        )
    )
    ids = cur.fetchall()

    con.close()

    return [id[0] for id in ids]


def get_listing_info_for_message(listing_id, db_name, table_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    cur.execute(
        "SELECT price, address, zip,listing_url, picture_url FROM {table_name} WHERE id='{listing_id}'".format(
            table_name=table_name,
            listing_id=listing_id,
        )
    )
    column_names = [description[0] for description in cur.description]
    listing_info = cur.fetchone()
    listing_dict = dict(zip(column_names, listing_info))

    con.close()

    return listing_dict


def store_data(user_id, column_name, column_value):
    conn = sqlite3.connect("databases/user_data.sqlite")
    cursor = conn.cursor()

    # Check if the user_id already exists
    cursor.execute("SELECT user_id FROM user_data WHERE user_id = ?", (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        # Update the specified column for the existing user
        update_query = f"UPDATE user_data SET {column_name} = ? WHERE user_id = ?"
        cursor.execute(update_query, (column_value, user_id))
    else:
        # If the user_id doesn't exist, insert a new row
        insert_query = f"INSERT INTO user_data (user_id, {column_name}) VALUES (?, ?)"
        cursor.execute(insert_query, (user_id, column_value))

    conn.commit()
    conn.close()


def get_table_data(db_name, table_name, user_id):
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    cur.execute(
        "SELECT * FROM {table_name} WHERE user_id='{user_id}'".format(
            table_name=table_name,
            user_id=user_id,
        )
    )
    column_names = [description[0] for description in cur.description]
    listing_info = cur.fetchone()
    listing_dict = dict(zip(column_names, listing_info))

    con.close()

    return listing_dict


def get_user_ids(db_name, table_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    cur.execute(
        "SELECT user_id FROM {table_name}".format(
            table_name=table_name,
        )
    )
    ids = cur.fetchall()

    con.close()

    return [id[0] for id in ids]
