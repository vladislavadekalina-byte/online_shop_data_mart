with expected as (
    select
        i.order_item_id,
        i.order_id,
        i.product_id,
        i.quantity,
        i.unit_price,
        i.discount_amount,
        i.line_amount
    from {{ ref('stg_shop__order_items') }} as i
    join {{ ref('stg_shop__orders') }} as o
        on i.order_id = o.order_id
    where not o.is_test_order
),
actual as (
    select
        order_item_id,
        order_id,
        product_id,
        quantity,
        unit_price,
        discount_amount,
        line_amount
    from {{ ref('fct_order_items') }}
)
select
    coalesce(
        expected.order_item_id,
        actual.order_item_id
    ) as order_item_id,
    expected.line_amount as expected_amount,
    actual.line_amount as actual_amount
from expected
full outer join actual
    on expected.order_item_id = actual.order_item_id
where expected.order_item_id is null
    or actual.order_item_id is null
    or expected.order_id is distinct from actual.order_id
    or expected.product_id is distinct from actual.product_id
    or expected.quantity is distinct from actual.quantity
    or expected.unit_price is distinct from actual.unit_price
    or expected.discount_amount is distinct from actual.discount_amount
    or expected.line_amount is distinct from actual.line_amount