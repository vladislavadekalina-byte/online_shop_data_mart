{{ config(distributed_replicated=true) }}

with customers as (
    select
        customer_id,
        registered_at,
        registration_date,
        city,
        acquisition_channel
    from {{ ref('stg_shop__customers') }}
),
 orders as (
    select
         customer_id,
         count(*) as confirmed_orders_count,
         sum(order_amount) as confirmed_revenue
    from {{ ref('fct_orders') }}
    where is_confirmed = true
    group by customer_id
 ),
  ranked_orders as (
    select
          customer_id,
          order_id,
          ordered_at,
          row_number() over (
                partition by customer_id
                order by ordered_at, order_id
          ) as fo
    from {{ ref('fct_orders') }}
    where is_confirmed = true
),
  first_order as (
    select
        customer_id,
        order_id as first_confirmed_order_id,
        ordered_at as first_confirmed_at
    from ranked_orders
    where fo = 1


  )

select
    c.customer_id,
    c.registered_at,
    c.registration_date,
    c.city,
    c.acquisition_channel,
    f.first_confirmed_order_id,
    f.first_confirmed_at,
    coalesce(o.confirmed_orders_count, 0) as confirmed_orders_count,
    coalesce(o.confirmed_revenue, 0) as confirmed_revenue,
    coalesce(o.confirmed_orders_count, 0) > 0 as is_buyer
from customers as c

left join orders as o
on c.customer_id = o.customer_id

left join first_order as f
on c.customer_id = f.customer_id



