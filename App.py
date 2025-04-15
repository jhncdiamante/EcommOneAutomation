from One import One
from WebDriverManager import Driver
from datetime import datetime
import pandas as pd
import time

driver = Driver()
base_url = "https://ecomm.one-line.com/one-ecom/manage-shipment/cargo-tracking"
One = One(driver, base_url)
One.open_page()
booking_number = "DVOF00401402"
One.search_cargo_tracking(booking_number)
One.click_search_button()
table = One.get_table()
rows = One.get_table_rows(table)

datalist = []
MATCH_RULES = {
        "gate in": {
            "keyword": "gate in",
            "type": "first"
        },
        "departure": {
            "keyword": "departure",
            "type": "first"
        },
        "arrival": {
            "keyword": "arrival",
            "type": "last"
        },
        "discharging": {
            "keyword": "discharge",
            "type": "last"
        },
        "gate out": {
            "keyword": "gate out",
            "type": "last"
        }
    }

for row in rows:
    c_num = One.process_row(row)  # get container number and click to show table
    table_data = {key: None for key in MATCH_RULES}
    table_data['booking number'] = booking_number
    table_data['container number'] = c_num

    data = One.get_container_info()
    for status, date in data.items():
        for column_name, rule in MATCH_RULES.items():
            if column_name in status:
                if rule["type"] == "first" and table_data[column_name] is None:
                    table_data[column_name] = date
                    if column_name == 'departure':
                        vessel_and_number = status.split("' ")[0]
                        table_data['departure vessel and number'] = vessel_and_number[1:].upper()
                elif rule["type"] == "last":
                    table_data[column_name] = date
                    if column_name == 'arrival':
                        vessel_and_number = status.split("' ")[0]
                        table_data['arrival vessel and number'] = vessel_and_number[1:].upper()
    
    table_data['scrape date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    datalist.append(table_data)

df = pd.DataFrame(datalist)
df.to_csv(r"OUTPUT.csv", index=False)
time.sleep(30)
    




