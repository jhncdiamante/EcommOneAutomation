import random
from One import OneEcomm
from WebDriverManager import Driver
from datetime import datetime
import pandas as pd

import time
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

datalist = []  # extracted data storage
columnsA = ['gate in to outbound terminal', 'departure from port of loading'] # first occurence
columnsB = ['arrival at port of discharging', 'discharging', 'gate out']  # last occurence


One = OneEcomm(driver, base_url)


for booking_number in booking_numbers:
    One.open_page()
    One.search_cargo_tracking(booking_number)
    One.click_search_button()
   
    containers_table = One.get_containers_info_table()
    containers = One.get_containers(containers_table)

    for container in containers:
        c_num = One.head_to_container_data(container)  # get container number and click to show table
        container_data = {}
        container_data['booking number'] = booking_number
        container_data['container number'] = c_num

        shipment_process_data = One.get_container_info()  # dict with status and date key-pairs

        def find_match(columns_list, status_list):
            for column in columns_list:
                for status in status_list:
                    if column in status:
                        print(f"Founded data for {column}")
                        container_data[column] = shipment_process_data[status]
                        if column in ('departure from port of loading', 'arrival at port of discharging'):
                            vessel_and_number = status.split("' ")[0][1:].upper()
                            words = vessel_and_number.split()
                            container_data[f'{column} vessel number'] = words[-1]
                            container_data[f'{column} vessel name'] = ' '.join(words[:-1])
                        break         
        
        status_list = shipment_process_data.keys()
        find_match(columnsA, status_list)
        find_match(columnsB, list(status_list)[::-1])     

        
        container_data['scrape date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        datalist.append(container_data)

    One.clear_search_bar()
    time.sleep(random.randint(5, 10))

df = pd.DataFrame(datalist)
df.to_csv(OUTPUT_FILE_PATH, index=False)