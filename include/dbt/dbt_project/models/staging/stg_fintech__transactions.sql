select
    amount,
    card_type,
    currency,
    merchant,
    merchant_category,
    timestamp AS transaction_timestamp, 
    cast(timestamp AS Date) AS transaction_date,
    transaction_id,
    user_id
from
    {{ source('snowflake_sources', 'RAW_TRANSACTIONS') }}
