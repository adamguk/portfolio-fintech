with dbt_dim_date as (
    select *
    from {{ ref('stg_date_dimension') }}
)

select 
    *,
    case 
        when (extract(month from date_day) = 4 and extract(day from date_day) >= 6) 
        or extract(month from date_day) > 4
        then extract(year from date_day)
        else extract(year from date_day) - 1
    end as uk_tax_year
from dbt_dim_date