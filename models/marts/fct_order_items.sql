{{ config(materialized='incremental', incremental_strategy='append',
    unique_key='order_item_id', distributed_by='order_id',
    appendoptimized=true, orientation='column') }}

with order_items as (
    select
       order_id,
       product_id,
       quantity,
       unit_price,
       discount_amount,
       line_amount
    from {{ ref('stg_shop__order_items') }}
),
  orders as (
    select
        order_id,
        customer_id,
        order_date,
        is_confirmed,
        is_test_order
    from {{ ref('int_orders_with_payments') }}
)

select
       i.order_id::text || '-' || i.product_id::text as order_item_id,
       i.order_id,
       i.product_id,
       o.customer_id,
       o.order_date,
       i.quantity,
       i.unit_price,
       i.discount_amount,
       i.line_amount,
       o.is_confirmed
from order_items as i
join orders as o
on i.order_id = o.order_id
where not o.is_test_order

{% if is_incremental() %}
    and not exists (
        select 1
        from {{ this }} as existing
        where existing.order_item_id = i.order_id::text || '-' || i.product_id::text
 )
{% endif %}