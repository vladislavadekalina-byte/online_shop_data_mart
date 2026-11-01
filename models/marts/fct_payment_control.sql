{{ config(
    materialized='table',
    distributed_by='order_id'
) }}
with orders as (
    select
        order_id,
        customer_id,
        order_date,
        order_status,
        order_amount,
        paid_amount,
        refunded_amount,
        net_paid_amount,
        successful_payments_count,
        is_confirmed
    from {{ ref('fct_orders') }}
)
select
    *,
    greatest(
        paid_amount - order_amount,
        0
    ) as overpaid_before_refunds,
    paid_amount > order_amount as has_overpayment,
    refunded_amount > paid_amount as has_excess_refund,
    case
        when successful_payments_count = 0 then 'unpaid'
        when paid_amount < order_amount then 'partially_paid'
        when paid_amount = order_amount then 'paid'
        else 'overpaid'
    end as payment_state,
    case
        when refunded_amount = 0 then 'no_refund'
        when refunded_amount > paid_amount then 'excess_refund'
        when refunded_amount = paid_amount then 'full_refund'
        else 'partial_refund'
    end as refund_state
from orders