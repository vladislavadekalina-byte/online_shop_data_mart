from datetime import datetime
from db import connect_to_shop

order_id = 900001
payment_id = 9000011
paid_at = datetime(2026, 7, 12, 10, 5)

def main():
    with connect_to_shop() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT status, total_amount
                FROM public.orders
                WHERE order_id = %s
                FOR UPDATE
                """,
                (order_id,),
            )
            order = cursor.fetchone()
            if order is None:
                raise ValueError(
                    f"Заказ {order_id} не найден."
                )
            order_status, order_amount = order
            cursor.execute(
                """
                SELECT order_id, payment_status, amount
                FROM public.payments
                WHERE payment_id = %s
                """,
                (payment_id,),
            )
            existing_payment = cursor.fetchone()

            if existing_payment is not None:
                expected_payment = (
                    order_id,
                    "success",
                    order_amount,
                )
                if existing_payment != expected_payment:
                    raise ValueError(
                        "Номер платежа уже занят другими данными."
                    )
                if order_status != "paid":
                    raise ValueError(
                        "Платёж существует, но статус заказа не paid. "
                        "Нужно проверить данные."
                    )
                print("Этот платёж уже записан. Данные не изменены.")
                return

            if order_status != "pending":
                raise ValueError(
                    f"Ожидался статус pending, получен {order_status}."
                )
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM public.payments
                WHERE order_id = %s
                """,
                (order_id,),
            )
            payments_count = cursor.fetchone()[0]

            if payments_count != 0:
                raise ValueError(
                    "У заказа уже есть другие платежи. "
                    "Проверь их перед добавлением полной оплаты."
                )
            cursor.execute(
                """
                INSERT INTO public.payments (
                    payment_id,
                    order_id,
                    paid_at,
                    payment_status,
                    amount
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    payment_id,
                    order_id,
                    paid_at,
                    "success",
                    order_amount,
                ),
            )
            cursor.execute(
                """
                UPDATE public.orders
                SET status = %s
                WHERE order_id = %s
                """,
                ("paid", order_id),
            )

    print(f"Добавлен платёж {payment_id} на {order_amount} рублей.")
    print(f"Статус заказа {order_id} изменён на paid.")


if __name__ == "__main__":
    main()