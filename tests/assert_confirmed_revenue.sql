with orders_revenue_from_marts as (
    select sum(order_amount) as sum_from_marts
    from {{ ref('fct_orders') }}
    where is_confirmed = true
),
    orders_revenue_from_source as (
        select sum(o.total_amount) as sum_from_source
        from {{ source('shop', 'orders') }} as o
        where status = 'paid'
            and exists (
                select 1
                from {{ source('shop', 'payments') }} as p
                where p.payment_status = 'success' and p.order_id = o.order_id and p.amount >= 0
            )
)

select
    m.sum_from_marts,
    s.sum_from_source
from orders_revenue_from_marts as m
cross join orders_revenue_from_source as s
where m.sum_from_marts is distinct from s.sum_from_source