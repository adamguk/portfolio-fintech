import csv
import random
import uuid
from datetime import datetime, timedelta

def generate_fintech_data(filename="mock_transactions.csv", num_rows=1000):
    merchants = {
        "Groceries": ["Tesco", "Sainsburys", "Asda", "Aldi"],
        "Entertainment": ["Netflix", "Spotify", "Cineworld", "Steam"],
        "Transport": ["Uber", "TfL", "Trainline", "Shell"],
        "Shopping": ["Amazon", "ASOS", "Argos", "Currys"],
        "Dining": ["Deliveroo", "JustEast", "Starbucks", "Nandos"]
    }
    
    headers = ["transaction_id", "user_id", "timestamp", "amount", "currency", "merchant", "merchant_category", "card_type"]
    
    start_time = datetime.now() - timedelta(days=7)
    
    # Generate a pool of 50 unique user IDs
    user_pool = [str(uuid.uuid4())[:8] for _ in range(50)]
    
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        
        for i in range(num_rows):
            tx_id = str(uuid.uuid4())
            user_id = random.choice(user_pool)
            
            # Increment time slightly for each transaction
            timestamp = start_time + timedelta(minutes=random.randint(1, 60) * i)
            
            category = random.choice(list(merchants.keys()))
            merchant = random.choice(merchants[category])
            
            card_type = random.choice(["Visa", "Mastercard", "Amex"])
            
            # 1. Normal transaction generation
            amount = round(random.uniform(2.50, 150.00), 2)
            
            # 2. Inject deliberate fraud pattern A: Extremely high value (0.5% chance)
            if random.random() < 0.005:
                amount = round(random.uniform(5000.00, 10000.00), 2)
                
            writer.writerow([tx_id, user_id, timestamp.strftime("%Y-%m-%d %H:%M:%S"), amount, "GBP", merchant, category, card_type])
            
            # 3. Inject deliberate fraud pattern B: Rapid retry/smurfing (1% chance)
            if random.random() < 0.01:
                duplicate_tx_id = str(uuid.uuid4())
                duplicate_time = timestamp + timedelta(seconds=random.randint(5, 30))
                # Same user, same amount, same merchant, moments later
                writer.writerow([duplicate_tx_id, user_id, duplicate_time.strftime("%Y-%m-%d %H:%M:%S"), amount, "GBP", merchant, category, card_type])

if __name__ == "__main__":
    generate_fintech_data("mock_transactions.csv", 2000)
    print("Dataset generation complete. saved as mock_transactions.csv")