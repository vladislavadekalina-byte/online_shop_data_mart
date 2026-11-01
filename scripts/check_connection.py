from db import connect_to_shop


def main():
    with connect_to_shop() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            database_name = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM public.orders")
            orders_count = cursor.fetchone()[0]

    print(f"Подключение успешно. База: {database_name}")
    print(f"Количество заказов: {orders_count}")


if __name__ == "__main__":
    main()