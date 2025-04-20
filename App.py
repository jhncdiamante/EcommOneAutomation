from One import OneEcomm
from WebDriverManager import Driver
from datetime import datetime
import pandas as pd

INPUT_FILE_PATH = "input.csv" # <<<< INPUT FILE TYPE MUST MATCH THE OUTPUT FILE TYPE
OUTPUT_FILE_PATH = "output.csv"
if INPUT_FILE_PATH.endswith(".csv") and OUTPUT_FILE_PATH.endswith(".csv"):
    input_file = pd.read_csv(INPUT_FILE_PATH)
elif INPUT_FILE_PATH.endswith(".xlsx") and OUTPUT_FILE_PATH.endswith(".xlsx"):
    input_file = pd.read_excel(INPUT_FILE_PATH)
else:
    raise ValueError("Incorrect file format.")



booking_numbers = input_file.iloc[:, 0].dropna().unique().tolist()

driver = Driver()
base_url = "https://ecomm.one-line.com/one-ecom/manage-shipment/cargo-tracking"

#booking_number = "DVOF00401402"
datalist = []
MATCH_RULES = {
        "gate in": 0,
        "departure": 0,
        "arrival": 1,
        "discharging": 1,
        "gate out": 1
    }
table_data = {key: None for key in MATCH_RULES}
print(table_data)
exit()

One = OneEcomm(driver, base_url)

for booking_number in booking_numbers:
    One.open_page()
    
    One.search_cargo_tracking(booking_number)
    One.click_search_button()
    table = One.get_table()
    rows = One.get_table_rows(table)

    for row in rows:
        c_num = One.process_row(row)  # get container number and click to show table
        table_data = {key: None for key in MATCH_RULES}
        table_data['booking number'] = booking_number
        table_data['container number'] = c_num

        data = One.get_container_info()
        for status, date in data.items():
            for column_name, rule in MATCH_RULES.items():
                if column_name in status:
                    if rule == 0 and table_data[column_name] is None:
                        table_data[column_name] = date
                        
                        if column_name == 'departure':
                            vessel_and_number = status.split("' ")[0]
                            table_data['departure vessel and number'] = vessel_and_number[1:].upper()
                    elif rule == 1:
                        table_data[column_name] = date
                        if column_name == 'arrival':
                            vessel_and_number = status.split("' ")[0]
                            table_data['arrival vessel and number'] = vessel_and_number[1:].upper()
        
        table_data['scrape date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        datalist.append(table_data)

    One.clear_search_bar()
    #One._driver.refresh()

df = pd.DataFrame(datalist)
df.to_csv(OUTPUT_FILE_PATH, index=False)
print("Done.")





