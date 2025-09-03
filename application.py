while True:
    try:
        # Get user input and convert to integer
        user_input = int(input("How much amount you want to save: "))
        if user_input <= 0 or user_input >= 10000:
            print("Error: Please enter a valid number between 0 and 10000 only!")
            print("Try again...")
            continue            # Continue the loop
        # If successful, break out of the loop
        break
    except ValueError:
        # Handle the case when user enters non-numeric input
        print("Error: Please enter a valid number only!")
        print("Try again...")


print(f"So you want to save, {user_input} dollars")


bank = {
    "Bank A": {"rate": 0.05, "minimum_deposit": 1000},
    "Bank B": {"rate": 0.04, "minimum_deposit": 1500},
    "Bank C": {"rate": 0.03, "minimum_deposit": 2000},
}

print("\n Available banks:")
for bank_name, bank_info in bank.items():
    print(f"- {bank_name}: {bank_info['rate']*100}% interest rate, minimum deposit: {bank_info['minimum_deposit']}")

eligible_banks = {}
for bank_name, bank_info in bank.items():
    if user_input >= bank_info['minimum_deposit']:
        eligible_banks[bank_name] = bank_info

if eligible_banks:
    best_bank = None
    best_rate = 0

    for bank_name, bank_info in eligible_banks.items():
        if bank_info['rate'] > best_rate:
            best_rate = bank_info['rate']
            best_bank = bank_name
    
    print(f"\n The best bank for you is {best_bank} with {best_rate*100}% interest rate.")
    
    annual_interest = user_input * best_rate

else:
    print("No eligible banks found.")

import requests
from bs4 import BeautifulSoup
import re

def scrape_real_bank_data():
    url = "https://www.nerdwallet.com/best/banking/savings-accounts"
    response = requests.get(url)

    if requests.status_codes == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        bank = {}

        








