import requests
from models.customer import Customer
from datetime import datetime
from decimal import Decimal

FLASK_URL = "http://mock-server:5000/api/customers"

def ingest_data(db):
    page = 1
    total = 0

    while True:
        # 🔹 Flask API call
        try:
            res = requests.get(FLASK_URL, params={"page": page, "limit": 5})
        except Exception as e:
            print("Request failed:", e)
            break

        # 🔹 Check status
        if res.status_code != 200:
            print("Flask API error:", res.text)
            break

        # 🔹 Parse JSON safely
        try:
            json_data = res.json()
            data = json_data.get("data", [])
        except Exception as e:
            print("Invalid JSON from Flask:", res.text)
            break

        # 🔹 Stop if no data
        if not data:
            break

        # 🔹 Process each record
        for item in data:
            try:
                # ✅ Fix data types
                item["account_balance"] = Decimal(str(item.get("account_balance", 0)))

                if item.get("date_of_birth"):
                    item["date_of_birth"] = datetime.strptime(
                        item["date_of_birth"], "%Y-%m-%d"
                    ).date()

                if item.get("created_at"):
                    item["created_at"] = datetime.fromisoformat(
                        item["created_at"]
                    )

                # 🔹 Upsert logic
                existing = db.query(Customer).filter_by(
                    customer_id=item["customer_id"]
                ).first()

                if existing:
                    for key, value in item.items():
                        setattr(existing, key, value)
                else:
                    db.add(Customer(**item))

                total += 1

            except Exception as e:
                print("Error processing record:", e)

        db.commit()
        page += 1

    return total