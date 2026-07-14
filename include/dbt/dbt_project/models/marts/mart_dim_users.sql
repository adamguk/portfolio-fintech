select distinct
    user_id
from {{ref('stg_fintech__transactions')}}