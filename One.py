
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time, logging
from logging_config import setup_logger
setup_logger()

MAX_ATTEMPTS = 5

class OneEcomm:
    def __init__(self, Driver, base_url):
        self._base_url = base_url
        self._driver = Driver.driver
        

    def retry_until_success(self, func, max_retries=MAX_ATTEMPTS, delay=2, exceptions=(Exception,), on_fail_message=None, on_fail_execute_message=None):
    
        for attempt in range(max_retries):
            try:
                return func()
            except exceptions as e:
                print(f"{on_fail_message or 'Attempt failed'}, retrying... ({attempt + 1}/{max_retries}) {e}")
                time.sleep(delay)
        raise Exception(on_fail_execute_message or "Max retries exceeded")
    
    def clear_search_bar(self):
        def try_clear_search_bar():
            search_box = WebDriverWait(self._driver, 20).until(
                EC.visibility_of_element_located((By.ID, 'searchName'))
            )
            search_box.clear()
            logging.info(f"Cleared search bar.")


        self.retry_until_success(
            try_clear_search_bar,
            max_retries=MAX_ATTEMPTS,
            delay=2,
            on_fail_message="Failed to clear search bar",
            on_fail_execute_message="Failed to clear search bar after multiple attempts"
        )
    
    def open_page(self):

        def try_open_page():
            
            self._driver.get(self._base_url)
            logging.info(f"Page opened successfully: {self._base_url}")
            self._driver.maximize_window()
            iframe = WebDriverWait(self._driver, 20).until(
                EC.visibility_of_element_located((By.ID, "IframeCurrentEcom"))
            )
            self._driver.switch_to.frame(iframe)


        self.retry_until_success(
            try_open_page,
            max_retries=MAX_ATTEMPTS,
            delay=2,
            on_fail_message="Failed to open page",
            on_fail_execute_message="Failed to open page after multiple attempts"
        )


    def search_cargo_tracking(self, tracking_number):
        def try_search_cargo_tracking():
            search_box = WebDriverWait(self._driver, 20).until(
                EC.visibility_of_element_located((By.ID, 'searchName'))
            )
            search_box.send_keys(tracking_number)
            logging.info(f"Tracking number entered: {tracking_number}")


        self.retry_until_success(
            try_search_cargo_tracking,
            max_retries=MAX_ATTEMPTS,
            delay=2,
            on_fail_message="Failed to search cargo tracking",
            on_fail_execute_message="Failed to search cargo tracking after multiple attempts"
        )

    def click_search_button(self):
        def try_click_search_button():
            search_button = WebDriverWait(self._driver, 20).until(
                EC.element_to_be_clickable((By.ID, 'main-control-btn2'))
            )
            search_button.click()
            logging.info("Search button clicked successfully")

        self.retry_until_success(
            try_click_search_button,
            max_retries=MAX_ATTEMPTS,
            delay=2,
            on_fail_message="Failed to click search button",
            on_fail_execute_message="Failed to click search button after multiple attempts"
        )

    def get_containers_info_table(self):
        def try_get_table():
            table = WebDriverWait(self._driver, 20).until(
                EC.visibility_of_element_located((By.ID, 'main-grid'))
            )
            logging.info("Table retrieved successfully")
            return table

        return self.retry_until_success(
            try_get_table,
            max_retries=MAX_ATTEMPTS,
            delay=2,
            on_fail_message="Failed to get table",
            on_fail_execute_message="Failed to get table after multiple attempts"
        )

    def get_containers(self, table):
        def try_get_table_rows():
            rows = WebDriverWait(table, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, './/tbody/tr[@id]'))
            )
            logging.info(f"Number of rows retrieved: {len(rows)}")
            return rows

        return self.retry_until_success(
            try_get_table_rows,
            max_retries=MAX_ATTEMPTS,
            delay=2,
            on_fail_message="Failed to get table rows",
            on_fail_execute_message="Failed to get table rows after multiple attempts"
        )
       
    def head_to_container_data(self, row):
        def try_process_row():
            container_number = WebDriverWait(row, 20).until(
                EC.visibility_of_element_located((By.TAG_NAME, 'a'))
            )
            container_number.click()
            container_number_text = container_number.text
            logging.info(f"Container number clicked: {container_number_text}")
            return container_number_text
        return self.retry_until_success(
            try_process_row,
            max_retries=MAX_ATTEMPTS,
            delay=2,
            on_fail_message="Failed to process row",
            on_fail_execute_message="Failed to process row after multiple attempts"
        )
    
    def get_container_info(self):
        def try_get_container_info():
            container_info = WebDriverWait(self._driver, 20).until(
                EC.visibility_of_element_located((By.ID, 'detail'))
            )
            logging.info("Container info retrieved successfully")
            body = container_info.find_element(By.TAG_NAME, 'tbody')
            rows = body.find_elements(By.TAG_NAME, 'tr')
            table_data = {}
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                status = cells[1].text.lower()
                date = cells[3].text

                if date.startswith("Actual") or date.startswith("Estimate"):
                    date = ' '.join(date.split()[1:])
               
                table_data[status] = date
            return table_data

        return self.retry_until_success(
            try_get_container_info,
            max_retries=MAX_ATTEMPTS,
            delay=2,
            on_fail_message="Failed to get container info",
            on_fail_execute_message="Failed to get container info after multiple attempts"
        )
    
    

