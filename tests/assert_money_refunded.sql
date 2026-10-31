select
    order_id,
    order_status,
    net_paid_amount
from {{ ref('fct_orders') }}
where order_status = 'returned' and net_paid_amount is distinct from 0