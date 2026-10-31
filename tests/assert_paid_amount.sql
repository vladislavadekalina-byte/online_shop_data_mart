{{ config(severity='warn') }}

select
    order_id,
    order_amount,
    paid_amount,
    is_confirmed
from {{ ref('fct_orders') }}
where is_confirmed = true and paid_amount > order_amount