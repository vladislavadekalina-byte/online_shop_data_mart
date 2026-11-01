import argparse
from datetime import datetime
from decimal import Decimal
from db import connect_to_shop

order_ids = tuple(range(910001, 910007))
ordered_at = datetime(2026, 7, 13, 10, 0)
paid_at = datetime(2026, 7, 13, 10, 5)
changed_at = datetime(2026, 7, 14, 10, 0)

def lock_orders(cursor):
    cursor.execute(
        """
        select order_id, customer_id, order_created_at
        from public.orders
        where order_id = any(%s)
        order by order_id
        for update
        """,
        (list(order_ids),),
    )
    expected = [
        (order_id, 1, ordered_at)
        for order_id in order_ids
    ]
    if cursor.fetchall() != expected:
        raise ValueError(
            "Сначала выполни prepare. "
            "Проверь, что номера демонстрационных заказов не заняты."
        )
def put_payment(cursor, payment_id, order_id, amount, payment_date):
    amount = Decimal(amount)
    cursor.execute(
        """
        insert into public.payments (
            payment_id,
            order_id,
            paid_at,
            payment_status,
            amount
        )
        values (%s, %s, %s, %s, %s)
        on conflict (payment_id) do nothing
        """,
        (
            payment_id,
            order_id,
            payment_date,
            "success",
            amount,
        ),
    )
    cursor.execute(
        """
        select order_id, paid_at, payment_status, amount
        from public.payments
        where payment_id = %s
        """,
        (payment_id,),
    )
    expected = (
        order_id,
        payment_date,
        "success",
        amount,
    )
    if cursor.fetchone() != expected:
        raise ValueError(
            f"Платёж {payment_id} уже существует с другими данными."
        )
def prepare():
    with connect_to_shop() as connection:
        with connection.cursor() as cursor:
            for order_id in order_ids:
                cursor.execute(
                    """
                    insert into public.orders (
                        order_id,
                        customer_id,
                        order_created_at,
                        status,
                        total_amount
                    )
                    values (%s, %s, %s, %s, %s)
                    on conflict (order_id) do nothing
                    """,
                    (
                        order_id,
                        1,
                        ordered_at,
                        "pending",
                        Decimal("2000"),
                    ),
                )
            lock_orders(cursor)

            for order_id in order_ids:
                cursor.execute(
                    """
                    insert into public.order_items (
                        order_id,
                        product_id,
                        quantity,
                        unit_price,
                        discount_amount
                    )
                    values (%s, %s, %s, %s, %s)
                    on conflict (order_id, product_id) do nothing
                    """,
                    (
                        order_id,
                        1,
                        2,
                        Decimal("1000"),
                        Decimal("0"),
                    ),
                )
    print("Демонстрационные заказы подготовлены.")
def pay():
    payments = [
        (9100011, 910001, "2000"),
        (9100021, 910002, "1200"),
        (9100022, 910002, "800"),
        (9100031, 910003, "2000"),
        (9100032, 910003, "2000"),
        (9100041, 910004, "2000"),
        (9100051, 910005, "2000"),
    ]
    with connect_to_shop() as connection:
        with connection.cursor() as cursor:
            lock_orders(cursor)
            for payment_id, order_id, amount in payments:
                put_payment(
                    cursor,
                    payment_id,
                    order_id,
                    amount,
                    paid_at,
                )

            cursor.execute(
                """
                update public.orders
                set status = 'paid'
                where order_id = any(%s)
                    and status = 'pending'
                """,
                (list(order_ids[:5]),),
            )

    print("Оплаты записаны.")
def changes():
    with connect_to_shop() as connection:
        with connection.cursor() as cursor:
            lock_orders(cursor)
            for payment_id, order_id in [
                (9100041, 910004),
                (9100051, 910005),
            ]:
                cursor.execute(
                    """
                    select order_id, payment_status, amount
                    from public.payments
                    where payment_id = %s
                    """,
                    (payment_id,),
                )
                expected = (
                    order_id,
                    "success",
                    Decimal("2000"),
                )
                if cursor.fetchone() != expected:
                    raise ValueError(
                        "Перед возвратами выполни фазу pay."
                    )
            put_payment(
                cursor, 9100042, 910004, "-2000", changed_at
            )
            cursor.execute(
                """
                update public.orders
                set status = 'returned'
                where order_id = %s
                """,
                (910004,),
            )
            put_payment(
                cursor, 9100052, 910005, "-500", changed_at
            )
            cursor.execute(
                """
                update public.order_items
                set quantity = 3,
                    unit_price = 800,
                    discount_amount = 100
                where order_id = %s
                    and product_id = %s
                """,
                (910006, 1),
            )
            if cursor.rowcount != 1:
                raise ValueError("Позиция заказа 910006 не найдена.")
            cursor.execute(
                """
                update public.orders
                set total_amount = 2300
                where order_id = %s
                """,
                (910006,),
            )
            put_payment(
                cursor, 9100061, 910006, "2300", changed_at
            )
            cursor.execute(
                """
                update public.orders
                set status = 'paid'
                where order_id = %s
                """,
                (910006,),
            )
    print("Возвраты и исправление позиции записаны.")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "phase",
        choices=["prepare", "pay", "changes"],
    )
    args = parser.parse_args()
    actions = {
        "prepare": prepare,
        "pay": pay,
        "changes": changes,
    }
    actions[args.phase]()


if __name__ == "__main__":
    main()