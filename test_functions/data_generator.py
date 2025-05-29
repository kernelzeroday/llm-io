import random
import json
import string
from typing import List
from datetime import datetime, timedelta

def generate_data(data_type: str, count: int = 10, **kwargs) -> str:
    """
    Generate various types of test data.
    
    Supports generating:
    - users: Random user profiles
    - products: E-commerce product data
    - transactions: Financial transaction records
    - logs: System log entries
    - emails: Email addresses
    - passwords: Secure passwords
    
    Args:
        data_type (str): Type of data to generate
        count (int): Number of records to generate (default: 10)
        **kwargs: Additional parameters for specific data types
        
    Returns:
        str: JSON string with generated data
    """
    generators = {
        'users': _generate_users,
        'products': _generate_products,
        'transactions': _generate_transactions,
        'logs': _generate_logs,
        'emails': _generate_emails,
        'passwords': _generate_passwords
    }
    
    if data_type not in generators:
        available_types = list(generators.keys())
        return json.dumps({
            "error": f"Unknown data type '{data_type}'",
            "available_types": available_types
        })
    
    try:
        data = generators[data_type](count, **kwargs)
        return json.dumps({
            "data_type": data_type,
            "count": len(data),
            "generated_at": datetime.now().isoformat(),
            "data": data
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Generation failed: {str(e)}"})

def _generate_users(count, **kwargs):
    first_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'company.com']
    
    users = []
    for i in range(count):
        first = random.choice(first_names)
        last = random.choice(last_names)
        users.append({
            "id": i + 1,
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}@{random.choice(domains)}",
            "age": random.randint(18, 80),
            "city": random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
            "signup_date": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
        })
    return users

def _generate_products(count, **kwargs):
    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Toys']
    adjectives = ['Premium', 'Deluxe', 'Standard', 'Basic', 'Pro', 'Ultra']
    nouns = ['Widget', 'Gadget', 'Device', 'Tool', 'Kit', 'Set']
    
    products = []
    for i in range(count):
        products.append({
            "id": f"PROD-{i+1:04d}",
            "name": f"{random.choice(adjectives)} {random.choice(nouns)}",
            "category": random.choice(categories),
            "price": round(random.uniform(9.99, 999.99), 2),
            "stock": random.randint(0, 100),
            "rating": round(random.uniform(1.0, 5.0), 1),
            "reviews": random.randint(0, 500)
        })
    return products

def _generate_transactions(count, **kwargs):
    transaction_types = ['purchase', 'refund', 'transfer', 'deposit', 'withdrawal']
    statuses = ['completed', 'pending', 'failed', 'cancelled']
    
    transactions = []
    for i in range(count):
        transactions.append({
            "id": f"TXN-{random.randint(100000, 999999)}",
            "type": random.choice(transaction_types),
            "amount": round(random.uniform(1.00, 5000.00), 2),
            "currency": random.choice(['USD', 'EUR', 'GBP', 'JPY']),
            "status": random.choice(statuses),
            "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 168))).isoformat(),
            "user_id": random.randint(1, 1000)
        })
    return transactions

def _generate_logs(count, **kwargs):
    levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    services = ['auth-service', 'payment-service', 'user-service', 'notification-service']
    messages = [
        'User login successful',
        'Payment processed',
        'Database connection timeout',
        'Invalid API key',
        'Service started',
        'Memory usage high',
        'Request rate limit exceeded'
    ]
    
    logs = []
    for i in range(count):
        logs.append({
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 1440))).isoformat(),
            "level": random.choice(levels),
            "service": random.choice(services),
            "message": random.choice(messages),
            "request_id": f"req-{random.randint(10000, 99999)}",
            "user_id": random.randint(1, 1000) if random.random() > 0.3 else None
        })
    return logs

def _generate_emails(count, **kwargs):
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'company.com', 'university.edu']
    emails = []
    for i in range(count):
        username = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 12)))
        domain = random.choice(domains)
        emails.append(f"{username}@{domain}")
    return emails

def _generate_passwords(count: int, length: int = 12, **kwargs) -> List[str]:
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    passwords = []
    for i in range(count):
        password = ''.join(random.choices(chars, k=length))
        passwords.append(password)
    return passwords 