import requests,db
import config as c
from datetime import datetime

headers = {
    "x-api-key": c.actual_api_key,
    "Content-Type": "application/json"
}

def get_balance(accId):
    try:
        url = f"{c.actual_api_url}/v1/budgets/{c.actual_sync_id}/accounts/{accId}/balance"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # Отримуємо основний словник
        json_response = response.json()
        return int(json_response['data'])
    except Exception as e:
        print(f"❌ Помилка : {e}")

def get_curr_rate(cc):
    url = c.cur_rate_url
    response = requests.get(url)
    data = response.json()
    value = next((item for item in data if item["cc"] == cc), None)
    result = value['rate']
    return result

def push_recalc():
    all_responses = []
    try:
        con = db.get_connection()
        cursor = con.cursor()
        cursor.execute("select * from cur_recalc where env = %s ",[c.secret_env])
        data =  cursor.fetchall()
        cursor.close()
        con.commit()
        for row in data:
            cur_rate = get_curr_rate(row['cc'])
            oper_value = int(
                get_balance(row['accid_uah_ca']) - (get_balance(row['accid_cur_ci'])*cur_rate)
                             )
            if oper_value != 0:
                print(f"---{row['id']}---{row['cc']}---")
                url = f"{c.actual_api_url}/v1/budgets/{c.actual_sync_id}/accounts/{row['accid_uah_ai']}/transactions"
                body = {
                    "learnCategories": False,
                    "runTransfers": True,
                    "transaction": {
                        "account": row['accid_uah_ai'],
                        "date": datetime.now().date().isoformat(),
                        "amount": oper_value,
                        "payee": row['payeeid'],
                        "category": row['categoryid'],
                        "notes": f"Валютна позиція {row['cc']} (курс {cur_rate})"
                    }
                }
                response = requests.post(url, headers=headers, json=body)
                response.raise_for_status()
                if response.status_code == 200:
                    print(f"Транзакція на {oper_value / 100} успішно додана, переказ згенеровано!")
                else:
                    print(f"Помилка {response.status_code}: {response.text}")
                # json_response = response.json()
                all_responses.append(response.json())
            else:
                print(f"ℹ️ {row['cc']} в нормі, пропущено")
        return all_responses
    except Exception as e:
        print(f"❌ Помилка : {e}")


print(push_recalc())



