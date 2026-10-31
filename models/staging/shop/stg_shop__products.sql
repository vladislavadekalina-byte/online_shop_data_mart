with source as (
    select * from {{source('shop', 'products')}}
)

select
       product_id,
       category,
       brand,
       product_name
from source