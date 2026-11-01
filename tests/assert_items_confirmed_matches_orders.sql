select
    i.order_item_id,
    i.order_id,
    i.is_confirmed as confirmed_in_items,
    o.is_confirmed as confirmed_in_orders
from {{ ref('fct_order_items') }} as i
join {{ ref('fct_orders') }} as o
    on i.order_id = o.order_id
where i.is_confirmed is distinct from o.is_confirmed