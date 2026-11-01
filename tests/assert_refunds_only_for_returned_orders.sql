select
    p.payment_id,
    p.order_id,
    o.order_status
from {{ ref('stg_shop__payments') }} as p
join {{ ref('stg_shop__orders') }} as o
    on p.order_id = o.order_id
where p.is_refund
    and (
        o.order_status is null
        or o.order_status not in ('paid', 'returned')
    )
