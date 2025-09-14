import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()
#print(f"API key loaded: {os.getenv('ANTHROPIC_API_KEY')[:10] if os.getenv('ANTHROPIC_API_KEY') else 'None'}.....")

def get_smart_recommendation(user_amount, eligible_banks, all_banks):
    # Get API key from environment variable
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        return "No API key found. Please set ANTHROPIC_API_KEY in your .env file"
    
    # Prepare bank data for the LLM
    eligible_info = ""
    for name, info in eligible_banks.items():
        eligible_info += f"- {name}: {info['rate']*100:.2f}% APY, ${info['minimum_deposit']} minimum\n"
    
    ineligible_info = ""
    for name, info in all_banks.items():
        if name not in eligible_banks:
            needed = info['minimum_deposit'] - user_amount
            ineligible_info += f"- {name}: {info['rate']*100:.2f}% APY, ${info['minimum_deposit']} minimum (need ${needed} more)\n"
    
    prompt = f"""You are a financial advisor helping someone choose a savings account for ${user_amount}.

ELIGIBLE OPTIONS:
{eligible_info}

INELIGIBLE OPTIONS (for reference):
{ineligible_info}

Provide a specific recommendation including:
1. Which bank to choose and why
2. Key benefits of this choice
3. Any trade-offs to consider
4. One sentence about what they'd earn annually

Be concise but helpful. Focus on their specific situation."""

    try:
        print("Making API call.......") #Debug
        response = requests.post("https://api.anthropic.com/v1/messages", 
                               headers={"Content-Type": "application/json",
                               "x-api-key": api_key,
                               "anthropic-version":"2023-06-01"
                               },
                               json={
                                   "model": "claude-3-haiku-20240307",
                                   "max_tokens": 300,
                                   "messages": [{"role": "user", "content": prompt}]
                               })
        
        if response.status_code == 200:
            data = response.json()
            return data['content'][0]['text']
        else:
            return f"API Error: Status {response.status_code}, Response: {response.text[:100]}"
            
    except Exception as e:
        return f"Error: {str(e)}"

# Main application code
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

banks = {
    "Axos Bank": {"rate": 0.0446, "minimum_deposit": 1500},
    "Bask Bank": {"rate": 0.0415, "minimum_deposit": 0},
    "Openbank": {"rate": 0.0420, "minimum_deposit": 500},
    "CIT Bank": {"rate": 0.0400, "minimum_deposit": 5000},
    "E*TRADE": {"rate": 0.0400, "minimum_deposit": 0},
    "UFB Direct": {"rate": 0.0401, "minimum_deposit": 0},
    "Barclays": {"rate": 0.0390, "minimum_deposit": 0},
    "Synchrony Bank": {"rate": 0.0380, "minimum_deposit": 0},
}

print("\n Available banks:")
for bank_name, bank_info in banks.items():
    print(f"- {bank_name}: {bank_info['rate']*100}% interest rate, minimum deposit: {bank_info['minimum_deposit']}")

eligible_banks = {}
for bank_name, bank_info in banks.items():
    if user_input >= bank_info['minimum_deposit']:
        eligible_banks[bank_name] = bank_info

if eligible_banks:
    recommendation = get_smart_recommendation(user_input, eligible_banks, banks)
    print(f"\nAI Recommendation:\n{recommendation}")
else:
    print("No eligible banks found.")