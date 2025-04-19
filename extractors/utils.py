from psycopg2.extensions import AsIs
from psycopg2 import connect
from psycopg2.errors import UniqueViolation
from datetime import datetime


def get_table(html, name_tag):
    tag = html.find("a", name_tag)
    return tag and tag.find_next_sibling("table")


def get_text_next_tag(table, string, tag):
    tag_search = table.find(string=string)
    return tag_search and tag_search.find_next(tag).contents[0]


def get_href(table, string):
    a = table.find("a", text=string)
    return a and a["href"]


def delete_data(cod_rh, connection):
    try:
        cursor = connection.cursor()
        cursor.execute(
            "delete from identificacion where cvlac_id = '{}'".format(cod_rh)
        )
        connection.commit()
    except:
        connection.rollback()


def insert_data(table, dictionary, connection):
    try:
        columns = dictionary.keys()
        values = dictionary.values()

        insert_statement = "insert into {} ({}) values {}".format(
            table, ",".join(columns), tuple(values)
        )
        cursor = connection.cursor()
        cursor.execute(insert_statement)
        connection.commit()
    except Exception as ex:
        connection.rollback()
        f = open("logs.txt", "a")
        if "cvlac_id" in dictionary:
            f.write(
                " -- ".join(
                    [dictionary["cvlac_id"], str(datetime.now()), str(ex), table + "\n"]
                )
            )
