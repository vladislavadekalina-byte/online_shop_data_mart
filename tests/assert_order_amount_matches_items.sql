with order_items as (
    select
        order_id,
        sum(line_amount) as line_amount
    from {{ ref('fct_order_items') }}
    group by order_id
)
select
    o.order_id,
    i.line_amount,
    o.order_amount
from {{ ref('fct_orders') }} as o
left join order_items as i
    on o.order_id = i.order_id
where o.order_amount is distinct from i.line_amount