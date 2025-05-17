from datetime import datetime
from Application.One import EcommOne
from Application.WebDriverManager import Driver
import pandas as pd


INPUT_FILE_PATH = "INPUT.csv" # <<<< INPUT FILE TYPE MUST MATCH THE OUTPUT FILE TYPE
OUTPUT_FILE_PATH = "OUTPUT.csv"
if INPUT_FILE_PATH.endswith(".csv") and OUTPUT_FILE_PATH.endswith(".csv"):
    input_file = pd.read_csv(INPUT_FILE_PATH)
elif INPUT_FILE_PATH.endswith(".xlsx") and OUTPUT_FILE_PATH.endswith(".xlsx"):
    input_file = pd.read_excel(INPUT_FILE_PATH)
else:
    raise ValueError("Incorrect file format.")

booking_numbers = input_file.iloc[:, 0].dropna().unique().tolist()

driver = Driver()
base_url = "https://ecomm.one-line.com/one-ecom/manage-shipment/cargo-tracking"

One = EcommOne(Driver().driver, base_url)
    
One.start(booking_numbers)
milestone_keys = {"Gate in", "Departure", "Arrival", "Discharge", "Gate out for delivery"}

data_list = []

for shipment in One.shipments:

    
    for container in shipment.containers:
        container_data = {
                "Shipment ID": shipment.booking_number,
                "Container ID": container.id,
                "Gate in": None,
                "Departure": None,
                "Arrival": None,
                "Discharge": None,
                "Gate out for delivery": None
            }
       
        for milestone in container.milestones:
            if milestone.event not in milestone_keys:
                continue  # skip unnecessary milestones

            # this control flow records the first occurrence of Gate in and Departure
            # and the last occurrence of Arrival, Discharge, and Gate out for delivery

            if (container_data[milestone.event] is not None and milestone.event not in ["Gate in", "Departure"]) or (milestones_data[milestone.event] is None):
                container_data[milestone.event] = milestone.date
                if milestone.event in ["Arrival", "Departure"]:
                    container_data[f"{milestone.event} Vessel Name"] = milestone.vessel_name
                    container_data[f"{milestone.event} Voyage ID"] = milestone.vessel_id 

        scrape_date = datetime.now().strftime("%m/%d/%y %H:%M %p")
        container_data['Scrape Date'] = scrape_date

        container_data['Status'] = 'Complete' if container.is_complete else 'On-going'
                
        data_list.append(container_data)

df = pd.DataFrame(data_list)
df.to_csv(OUTPUT_FILE_PATH, index=False)

One.close()
            




