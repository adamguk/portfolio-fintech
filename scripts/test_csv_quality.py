import pandas as pd

def csv_quality_check(file_path:str) -> bool:
    df = pd.read_csv(file_path)  

    # ==========================================================================
    # STRUCTURAL & SCHEMA CHECKS (Columns, Nulls, Empty Files)
    # ==========================================================================

    if df.empty:
        raise ValueError(f"Data validation failed: File {file_path} is empty") 
    
    expected_columns = ["transaction_id", "user_id", "timestamp", "amount", "currency", "merchant", "merchant_category", "card_type"]
    if list(df.columns) != expected_columns:
        raise ValueError(f"Data validation failed: File {file_path} columns mismatch to expected columns")

    mandatory_fields = ["transaction_id", "user_id", "timestamp", "amount", "currency", "merchant"]
    for field in mandatory_fields:
        if df[field].isnull().any():
            raise ValueError (f"Data validation failed: File {file_path} column {field} contains empty or missing values")
        
    # ==========================================================================
    # 2. DATA CONTENT & FIELD-LEVEL TYPE VALIDATION
    # ==========================================================================

    try:
        pd.to_numeric(df["amount"], errors="raise")
    except ValueError:
        raise TypeError("Validation failed: Non-numeric values found in 'amount' column.")
        
    try:
        pd.to_datetime(df["timestamp"], errors="raise")
    except ValueError:
        raise TypeError("Validation failed: Invalid datetime strings found in 'timestamp' column.")
    
    if (df["amount"] == 0).any():
        raise ValueError (f"Data validation failed: File {file_path} column 'amount' contains zero number values")

    accepted_card_types = ["Visa", "Mastercard", "Amex"]
    if (~df["card_type"].isin(accepted_card_types)).any():
        raise ValueError (f"Data validation failed: File {file_path} column 'card_type' contains unrecognised card_type")
    
    
    return True 
