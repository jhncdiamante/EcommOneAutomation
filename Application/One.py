from Application.Shipments import Shipment
from Application.Search import SearchBar
from Application.WebDriverManager import Driver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
import time
TIMEOUT = 30

class EcommOne:
    def __init__(self, driver: WebDriver, base_url: str):
        self._driver = driver
        self._base_url = base_url
        self.search_bar = None
        self.shipments: list[Shipment] = []
        
    def goto_search_bar(self):
        self.search_bar = SearchBar(self._driver)

    def goto_main_page(self):
        iframe = WebDriverWait(self._driver, TIMEOUT).until(
                EC.visibility_of_element_located((By.ID, "IframeCurrentEcom"))
            )
        self._driver.switch_to.frame(iframe)

    def close(self):
        self._driver.close()

    def start(self, tracking_numbers: list[str]):
        self._driver.get(self._base_url)
        self._driver.maximize_window()
        self.remove_popup()
        self.goto_main_page()
        self.goto_search_bar()
        
        for tracking_number in tracking_numbers:
            try:
                self.search_bar.type_keyword(tracking_number)
                self.search_bar.click_search_button()
                time.sleep(2)

                self.shipments.append(Shipment((str(tracking_number) if not isinstance(tracking_number, str) else tracking_number), self._driver))
            except Exception as e:
                print(f"Error: {e}")
                raise e
            finally:
                self._driver.refresh()
                self.goto_main_page()
                self.goto_search_bar()
    
        

    def remove_popup(self):
        try:
            skip_button = WebDriverWait(self._driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Skip']"))
            )
            skip_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"Error: {e}")


    def close(self):
        self._driver.close()

    
if __name__ == "__main__":  
    One = EcommOne(Driver().driver, "https://ecomm.one-line.com/one-ecom/manage-shipment/cargo-tracking")
    
    print("Opening...")
    One.run(["SGNF62462500", "GESF00388800"])

    for shipment in One.shipments:
        print(f"Shipment: {shipment.booking_number}")
        print(f"Containers: {len(shipment.containers)}")
        for container in shipment.containers:
            print(f"Container: {container.id}")
            print(f"Milestones: {len(container.milestones)}")
            for milestone in container.milestones:
                print(f"Milestone: {milestone.event} - {milestone.date} - {milestone.location}")
                if milestone.vessel_name and milestone.vessel_id:
                    print(f"Vessel: {milestone.vessel_name} - {milestone.vessel_id}")

            print("-"*100)

    One.close()
            
        
