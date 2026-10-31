{{ config(distributed_replicated=true) }}

with products as (
    select
        product_id,
        category,
        brand,
        product_name
    from {{ ref('stg_shop__products') }}
),
   categories as (
   select
        category_id,
        parent_category_id,
        category_name,
        parent_category_name,
        root_category_name
   from {{ ref('int_category_tree') }}
)
select
    p.product_id,
    p.product_name,
    p.brand,
    p.category as category_name,
    c.category_id,
    c.parent_category_id,
    c.parent_category_name,
    c.root_category_name
from products as p
left join categories as c
on p.category = c.category_name
