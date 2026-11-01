select
    order_id,
    order_status,
    paid_amount,
    refunded_amount
from {{ ref('fct_orders') }}
where refunded_amount > paid_amount
    or (
        order_status = 'paid'
        and refunded_amount > 0
        and refunded_amount >= paid_amount
    )