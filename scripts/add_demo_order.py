from datetime import datetime
from decimal import Decimal
from db import connect_to_shop


order_id = 900001
customer_id = 1
product_id = 1
ordered_at = datetime(2026, 7, 12, 10, 0)
quantity = 2
unit_price = Decimal("1000.00")
discount_amount = Decimal("0.00")

total_amount = quantity * unit_price - discount_amount

def main():
    with connect_to_shop() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT order_id, status, total_amount
                FROM public.orders
                WHERE order_id = %s
                """,
                (order_id,),
            )
            existing_order = cursor.fetchone()
            if existing_order is not None:
                print(
                    f"Заказ {order_id} уже существует: "
                    f"статус {existing_order[1]}, "
                    f"сумма {existing_order[2]}. "
                    "Данные не изменены."
                )
                return
            cursor.execute(
                """
                INSERT INTO public.orders (
                    order_id,
                    customer_id,
                    order_created_at,
                    status,
                    total_amount
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    order_id,
                    customer_id,
                    ordered_at,
                    "pending",
                    total_amount,
                ),
            )
            cursor.execute(
                """
                INSERT INTO public.order_items (
                    order_id,
                    product_id,
                    quantity,
                    unit_price,
                    discount_amount
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    order_id,
                    product_id,
                    quantity,
                    unit_price,
                    discount_amount,
                ),
            )
    print(f"Создан заказ {order_id} на {total_amount} рублей.")
    print("Добавлена одна товарная позиция. Платежей пока нет.")


if __name__ == "__main__":
    main()