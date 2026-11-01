{% macro remove_missing_order_items() %}
    {% if is_incremental() %}
    delete from {{ this }} as existing
        where not exists (
            select 1
            from {{ ref('stg_shop__order_items') }} as i
            join {{ ref('int_orders_with_payments') }} as o
                on i.order_id = o.order_id
            where not o.is_test_order
                and i.order_item_id = existing.order_item_id
        )

    {% else %}
        select 1
    {% endif %}
{% endmacro %}