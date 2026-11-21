"""After the generators have filled the database: is the data what the project promises?

Uses the standard libpq variables (PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE).
Deterministic facts are checked; figures that depend on the random generators are only reported.
"""
import os
import sys

import psycopg2

conn = psycopg2.connect()
cur = conn.cursor()
one = lambda sql: (cur.execute(sql), cur.fetchone()[0])[1]

checks = []  # (name, expected, actual)
for t in ("customers", "orders", "products", "transactions"):
    checks.append((f"{t}: 5,000 rows", 5000, one(f"SELECT COUNT(*) FROM {t}")))
checks.append(("orders without a customer", 0, one("SELECT COUNT(*) FROM orders o LEFT JOIN customers c USING (customer_id) WHERE c.customer_id IS NULL")))
checks.append(("transactions without an order", 0, one("SELECT COUNT(*) FROM transactions t LEFT JOIN orders o USING (order_id) WHERE o.order_id IS NULL")))
checks.append(("duplicate customer emails", 0, one("SELECT COUNT(*) FROM (SELECT email FROM customers GROUP BY email HAVING COUNT(*) > 1) d")))
checks.append(("products with price <= 0", 0, one("SELECT COUNT(*) FROM products WHERE price <= 0")))
checks.append(("products with negative stock", 0, one("SELECT COUNT(*) FROM products WHERE stock_quantity < 0")))
checks.append(("transactions with amount <= 0", 0, one("SELECT COUNT(*) FROM transactions WHERE amount <= 0")))
checks.append(("order statuses outside the allowed four", 0, one("SELECT COUNT(*) FROM orders WHERE status NOT IN ('pending','shipped','delivered','cancelled')")))
checks.append(("payment methods outside the allowed three", 0, one("SELECT COUNT(*) FROM transactions WHERE payment_method NOT IN ('credit_card','paypal','bank_transfer')")))

info = {
    "customers who placed an order": one("SELECT COUNT(DISTINCT customer_id) FROM orders"),
    "total transaction amount": float(one("SELECT SUM(amount) FROM transactions")),
    "average transaction": round(float(one("SELECT AVG(amount) FROM transactions")), 2),
}

failed = [(n, e, a) for n, e, a in checks if e != a]
for n, e, a in checks:
    print(f"{'OK  ' if e == a else 'FAIL'} {n:<45} expected {e:>5}  got {a}")
print("\nFor information (random per run, README quotes one earlier run):")
for k, v in info.items():
    print(f"   {k}: {v:,}")
path = os.environ.get("GITHUB_STEP_SUMMARY")
if path:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("## Generated data checked\n\n| Check | Expected | Got | |\n|---|--:|--:|:-:|\n")
        for n, e, a in checks:
            fh.write(f"| {n} | {e} | {a} | {'✅' if e == a else '❌'} |\n")
        fh.write("\nRandom per run (the README quotes one earlier run): " + ", ".join(f"{k} = {v:,}" for k, v in info.items()) + "\n")
print(f"\n{len(checks) - len(failed)} of {len(checks)} checks passed")
sys.exit(1 if failed else 0)
