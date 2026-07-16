COPY INTO FINTECH.RAW.RAW_TRANSACTIONS
    FROM @MY_S3_STAGE/generated_transactions_{{ ds }}.csv
    PATTERN = '.*transactions_.*\.csv'
    FILE_FORMAT = (FORMAT_NAME = 'CSV_FILE_FORMAT')
    FORCE = FALSE; 
