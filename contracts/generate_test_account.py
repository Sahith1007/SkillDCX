"""
Generate Algorand Test Account

This script generates a new Algorand account for testing purposes.
Use this to create accounts for:
- Contract deployer
- Issuers
- Recipients
"""

from algosdk import account, mnemonic

def generate_account():
    """Generate a new Algorand account"""
    private_key, address = account.generate_account()
    mnemonic_phrase = mnemonic.from_private_key(private_key)
    
    return {
        "address": address,
        "private_key": private_key,
        "mnemonic": mnemonic_phrase
    }


def main():
    print("=" * 70)
    print("ALGORAND TEST ACCOUNT GENERATOR")
    print("=" * 70)
    
    print("\nGenerating new account...\n")
    
    account_info = generate_account()
    
    print("✓ Account Generated Successfully!")
    print("\n" + "=" * 70)
    print("ACCOUNT DETAILS")
    print("=" * 70)
    print(f"\nAddress:\n{account_info['address']}")
    print(f"\nMnemonic (25 words - KEEP SECURE!):\n{account_info['mnemonic']}")
    print(f"\nPrivate Key:\n{account_info['private_key']}")
    
    print("\n" + "=" * 70)
    print("IMPORTANT SECURITY NOTES")
    print("=" * 70)
    print("1. Never share your mnemonic or private key")
    print("2. Store mnemonic securely (offline backup)")
    print("3. This is a TestNet account - fund it with test ALGO")
    print("4. Get test ALGO from: https://testnet.algoexplorer.io/dispenser")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Fund this account with test ALGO (min 0.5 ALGO)")
    print("2. Use mnemonic for contract deployment:")
    print(f"   python deploy_unified_contract.py \"{account_info['mnemonic']}\"")
    print("\n3. Or set as environment variable:")
    print(f"   $env:DEPLOYER_MNEMONIC=\"{account_info['mnemonic']}\"")
    print("   python deploy_unified_contract.py --use-env")
    
    # Save to file option
    save = input("\n\nSave account details to file? (y/n): ").lower()
    if save == 'y':
        filename = "test_account.txt"
        with open(filename, "w") as f:
            f.write("ALGORAND TEST ACCOUNT\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {account_info['address']}\n\n")
            f.write(f"Address:\n{account_info['address']}\n\n")
            f.write(f"Mnemonic:\n{account_info['mnemonic']}\n\n")
            f.write(f"Private Key:\n{account_info['private_key']}\n\n")
            f.write("=" * 70 + "\n")
            f.write("SECURITY WARNING: Keep this file secure and delete after use!\n")
        
        print(f"\n✓ Account details saved to: {filename}")
        print("⚠️  Remember to delete this file after copying the details!")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
