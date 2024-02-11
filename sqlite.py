import sqlite3


def get_saved_listings(db_name, table_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    cur.execute("SELECT id FROM {table_name}".format(table_name=table_name))
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


con = sqlite3.connect("jam.sqlite")
cur = con.cursor()
cur.execute(
    "CREATE TABLE jam(id, id_hash, category, address, zip, city, price, epc, picture_url, listing_url, chat_id)"
)
