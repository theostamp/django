import os
import json

file_path = '/tenants_folders/theo_received_orders/order_table_1_540102.json'

# Ανάγνωση αρχείου
try:
    with open(file_path, 'r') as file:
        data = json.load(file)
    print(f"File read successfully: {data}")
except json.JSONDecodeError as e:
    print(f"JSON decode error: {e}")
except Exception as e:
    print(f"Error reading file: {e}")
