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
    
    print(f"\n Recommendation: {best_bank}")
    print(f" Interest rate: {best_rate*100}% APY")
    print(f"Minimum deposit: {eligible_banks[best_bank]['minimum_deposit']}")
    print(f" You'll earn approximately ${user_input * best_rate:.2f} per year.")

    
    annual_interest = user_input * best_rate

else:
    print("No eligible banks found.")

