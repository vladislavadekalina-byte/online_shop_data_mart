{{ config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key='order_item_id',
    distributed_by='order_id',
    appendoptimized=true,
    orientation='column',
    post_hook="{{ remove_missing_order_items() }}"
) }}

with current_items as (
    select
        i.order_item_id,
        i.order_id,
        i.product_id,
        o.customer_id,
        o.order_date,
        i.quantity,
        i.unit_price,
        i.discount_amount,
        i.line_amount,
        o.is_confirmed
    from {{ ref('stg_shop__order_items') }} as i
    join {{ ref('int_orders_with_payments') }} as o
        on i.order_id = o.order_id
    where not o.is_test_order
)

select current_items.*
from current_items

{% if is_incremental() %}
left join {{ this }} as existing
    on current_items.order_item_id = existing.order_item_id
where existing.order_item_id is null
    or current_items.order_id is distinct from existing.order_id
    or current_items.product_id is distinct from existing.product_id
    or current_items.customer_id is distinct from existing.customer_id
    or current_items.order_date is distinct from existing.order_date
    or current_items.quantity is distinct from existing.quantity
    or current_items.unit_price is distinct from existing.unit_price
    or current_items.discount_amount is distinct from existing.discount_amount
    or current_items.line_amount is distinct from existing.line_amount
    or current_items.is_confirmed is distinct from existing.is_confirmed
{% endif %}