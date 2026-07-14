--Table of statistics per user, per month
--Used for overall statistical trends

with user_summary_grain as(
    select
        t.user_id,
        date_trunc('month',t.transaction_date) as transaction_month,
        sum(amount) as month_total_amount
    from {{ref('int_fintech__transactions')}} as t
    group by 1,2
),

aggregation_stats as (
    select
        user_id,
        transaction_month,
        month_total_amount,
        
        sum(month_total_amount) over(
            partition by user_id
            order by transaction_month
        ) as rolling_total_amount,
    
        avg(month_total_amount) over(
            partition by user_id
            order by transaction_month
            rows between 2 preceding and current row
        ) as rolling_average_3_months,
    
        dense_rank() over(
            partition by user_id
            order by month_total_amount desc
        ) as month_amount_rank,

        stddev(month_total_amount) over(
            partition by user_id
            order by transaction_month
            rows between 2 preceding and current row
        ) as rolling_amount_volatility_3_months
        
    from user_summary_grain
),

deltas as (
    select
        user_id,
        transaction_month,
        month_total_amount,
        rolling_total_amount,
        rolling_average_3_months,
        rolling_amount_volatility_3_months,
        month_amount_rank,
        month_total_amount - nullif(rolling_average_3_months,0) as delta_month_vs_avg__value,
        rolling_amount_volatility_3_months / nullif(rolling_average_3_months,0) as coefficient_of_variation
from aggregation_stats)

select
    user_id,
    transaction_month,
    month_total_amount,
    rolling_total_amount,
    rolling_average_3_months,
    rolling_amount_volatility_3_months,
    month_amount_rank,
    
    delta_month_vs_avg__value,
    case 
        when delta_month_vs_avg__value > 0 then 'Above Average'
        when delta_month_vs_avg__value = 0 then 'On Average'
        else 'Below Average'
    end as delta_month_vs_avg__label,

    coefficient_of_variation,
    case 
        when coefficient_of_variation is null then 'Insufficient Data'
        when coefficient_of_variation = 0 then 'No Volatility'
        when coefficient_of_variation <= 0.15 then 'Low Volatility'
        when coefficient_of_variation > 0.15 and coefficient_of_variation < 0.50 then 'Med Volatility'
        when coefficient_of_variation >= 0.50 then 'High Volatility'
        else 'No Volatility'
    end as coefficient_of_variation__label
from deltas