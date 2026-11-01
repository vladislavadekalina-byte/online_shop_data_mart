import os

import psycopg


def connect_to_shop():
    return psycopg.connect(
        host=os.getenv("SHOP_DB_HOST", "localhost"),
        port=int(os.getenv("SHOP_DB_PORT", "5436")),
        dbname=os.getenv("SHOP_DB_NAME", "shop"),
        user=os.getenv("SHOP_DB_USER", "student"),
        password=os.getenv("SHOP_DB_PASSWORD", "studentpass"),
        connect_timeout=5,
    )