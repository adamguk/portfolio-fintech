-- Quarterly metrics based on merchant


    with merchant_summary_grain as(
        select
            merchant,
            extract('quarter',transaction_date) as transaction_quarter,
            extract('year',transaction_date) as transaction_year,
            sum(amount) as quarter_total_amount
        from {{ref('int_fintech__transactions')}}
        group by 1,2,3
    ),

    rank_stats_part_one as(
        select
            merchant,
            transaction_quarter,
            transaction_year,
            quarter_total_amount,

            rank() over(
                partition by transaction_year,transaction_quarter
                order by quarter_total_amount desc
            ) as current_qtr_merchant_rank
        from merchant_summary_grain
    ),

    rank_stats_part_two as(
        select
            merchant,
            transaction_quarter,
            transaction_year,
            quarter_total_amount,
            current_qtr_merchant_rank,
    
            lag(current_qtr_merchant_rank) over(
                partition by merchant
                order by transaction_year, transaction_quarter
            ) as previous_qtr_merchant_rank,
    
            lag(quarter_total_amount) over(
                partition by merchant
                order by transaction_year, transaction_quarter
            ) as previous_qtr_total_amount   
        from rank_stats_part_one
    ),

    deltas as(
        select
            merchant,
            transaction_quarter,
            transaction_year,
            quarter_total_amount,
            previous_qtr_total_amount,
            current_qtr_merchant_rank,
            previous_qtr_merchant_rank,
            previous_qtr_merchant_rank - nullif(current_qtr_merchant_rank,0) as rank_change,
            quarter_total_amount - nullif(previous_qtr_total_amount,0) as amount_change   
        from rank_stats_part_two       
    )

    select
        merchant,
        transaction_quarter,
        transaction_year,
        quarter_total_amount,
        previous_qtr_total_amount,
        current_qtr_merchant_rank,
        previous_qtr_merchant_rank,
        rank_change,
        amount_change,

        case
            when rank_change is null then 'Insufficient Data'
            when rank_change = 0 then 'No Change'
            when rank_change > 0 then 'Rank Improved'
            when rank_change < 0 then 'Rank Declined'
            else 'No Change'
        end as rank_change__label,

        case
            when amount_change is null then 'Insufficient Data'
            when amount_change = 0 then 'No Change'
            when amount_change < 0 then 'Quarter Total Amount Decreased'
            when amount_change > 0 then 'Quarter Total Amount Increased'
            else 'No Change'
        end as amount_change__label
    from deltas

        


            
    

    

