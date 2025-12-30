from api_handlers import get_balance_for_account

# Networth calculation
def calculate_networth(db, user_id):
    # Get all accounts
    accounts = db.execute("SELECT * FROM accounts WHERE user_id = ?", user_id)

    for acct in accounts:
        if acct["source_type"] == "api":
            latest = get_balance_for_account(acct)

            if latest is not None:
                db.execute("UPDATE accounts SET balance = ? WHERE id = ? AND user_id = ?", latest, acct["id"], user_id)

    # After updating balances, recompute totals
    assets = db.execute("SELECT name, balance FROM accounts WHERE type = ? AND user_id = ?", 'asset', user_id)
    liabilities = db.execute("SELECT name, balance FROM accounts WHERE type = ? AND user_id = ?", 'liability', user_id)

    asset_total = sum(float(a["balance"]) or 0 for a in assets)
    liability_total = sum(float(l["balance"]) or 0 for l in liabilities)

    networth = asset_total - abs(liability_total)

    # update history 
    db.execute("INSERT INTO balances (user_id, value, assets, liabilities) VALUES (?, ?, ?, ?)", user_id, networth, asset_total, liability_total)

    return networth