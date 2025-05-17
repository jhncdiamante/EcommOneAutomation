from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List
from Application.Container import Container
from selenium.webdriver.remote.webelement import WebElement
from Application.helpers import retry_until_success

import logging
from Application.logging_config import setup_logger
setup_logger()

# Constants
TIMEOUT = 60
CONTAINER_TABLE_ID = "//*[@id='main-grid']/tbody"
CONTAINER_ROW_XPATH = "./tr[@id]"
CONTAINER_CELL_XPATH = "./td[4]"


class Shipment:
    """
    Represents a shipping shipment with its containers and tracking information.
    
    Attributes:
        booking_number (str): The unique booking number for this shipment
        shipment_page (WebDriver): The Selenium WebDriver instance for the shipment page
        containers (List[Container]): List of containers associated with this shipment
        container_table (WebElement): The table element containing container information
    """
    
    def __init__(self, booking_number: str, driver: WebDriver) -> None:
        """
        Initialize a Shipment instance.
        
        Args:
            booking_number (str): The unique booking number for this shipment
            driver (WebDriver): The Selenium WebDriver instance for the shipment page
            
        Raises:
            ValueError: If booking_number is empty or driver is invalid
            TimeoutException: If the container table cannot be found within the timeout period
        """
        if not booking_number or not isinstance(booking_number, str):
            raise ValueError("Invalid booking number provided")
            
        self.booking_number = booking_number
        self.shipment_page = driver
        self.containers: List[Container] = []
        self.containers = self.get_containers()

    def get_container_table(self) -> WebElement:
        """
        Get the container table element from the shipment page.
        
        Returns:
            WebElement: The table body element containing container information
            
        Raises:
            TimeoutException: If the container table cannot be found within the timeout period
            NoSuchElementException: If the table body cannot be found
        """
        def func():
            container_table = WebDriverWait(self.shipment_page, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, CONTAINER_TABLE_ID))
            )
            logging.info(f"Container table found: {container_table}...")
            return container_table
        
        return retry_until_success(func,
                                   max_retries=3,
                                   delay=2,
                                   exceptions=(TimeoutException),
                                   on_fail_message="Container table not found",
                                   on_fail_execute_message="Container table not found")    
    
    def get_containers(self) -> List[Container]:
        """
        Get all containers associated with this shipment.
        
        Returns:
            List[Container]: List of Container objects for this shipment
            
        Raises:
            TimeoutException: If container rows cannot be found within the timeout period
        """
        def func():
            containers = WebDriverWait(self.get_container_table(), TIMEOUT).until(
                EC.presence_of_all_elements_located((By.XPATH, CONTAINER_ROW_XPATH))
            )
            logging.info(f"Found {len(containers)} containers...")

            return [
                Container(
                    container.find_element(By.XPATH, CONTAINER_CELL_XPATH),
                    self.shipment_page
                ) for container in containers
            ]
        
        return retry_until_success(func,
                                   max_retries=3,
                                   delay=2,
                                   exceptions=(TimeoutException),
                                   on_fail_message="Container rows not found",
                                   on_fail_execute_message="Container rows not found")      


