select
    t.amount,
    t.card_type,
    t.currency,
    t.merchant,
    t.merchant_category,
    t.transaction_timestamp, 
    t.transaction_date,
    d.uk_tax_year,
    t.transaction_id,
    t.user_id,
    case
        when t.amount >= 10000 then 'Reportable: On or Above Threshold'
        when t.amount >= 9000 and t.amount <10000 then 'Potential Structuring'
        else 'Non Reportable: Below Threshold'
    end as reportability_status
from {{ref('stg_fintech__transactions')}} as t
left join {{ref('mart_dim_date')}} as d
on t.transaction_date = d.date_day