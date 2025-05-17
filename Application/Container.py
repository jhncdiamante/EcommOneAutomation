import time
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from typing import List
from Application.Milestone import Milestone
import logging

from Application.logging_config import setup_logger
setup_logger()

# Constants
TIMEOUT = 30
DETAIL_INFO_ID = "//*[@id='detail']"
CONTAINER_LINK_XPATH = "./a"
MILESTONE_ROW_XPATH = "./tr"


class Container:
    """
    Represents a shipping container with its tracking information and milestones.
    
    Attributes:
        shipment_page (WebDriver): The Selenium WebDriver instance for the shipment page
        container (WebElement): The container element
        id (str): The unique identifier for this container
        milestones (List[Milestone]): List of milestones associated with this container
    """
    
    def __init__(self, container: WebElement, shipment_page: WebDriver) -> None:
        """
        Initialize a Container instance.
        
        Args:
            container (WebElement): The container element
            shipment_page (WebDriver): The Selenium WebDriver instance for the shipment page
            
        Raises:
            ValueError: If container or shipment_page is invalid
            TimeoutException: If milestone table cannot be found within timeout period
            NoSuchElementException: If required elements cannot be found
            ElementClickInterceptedException: If container link cannot be clicked
        """
            
        self.shipment_page = shipment_page
        self.container = container
        self.id: str = self.get_container_id()

        self.open()
        self.milestones: List[Milestone] = self.get_milestones()
        self.is_complete: bool = self.is_complete()
        
    def is_complete(self) -> bool:
        """
        Check if the container is complete.
        
        Returns:
            bool: True if the container is complete, False otherwise
        """
        try:
            return self.milestones[-1].event.lower().startswith("empty")
        except IndexError:
            raise IndexError("No milestones found yet for container")
    

    def get_container_id(self) -> str:
        """
        Get the container's unique identifier.
        
        Returns:
            str: The container's ID from its title attribute
            
        Raises:
            NoSuchElementException: If the title attribute cannot be found
        """
        try:
            container_id = self.container.get_attribute("title")
            logging.info(f'Processing container {container_id}...')
            if not container_id:
                raise NoSuchElementException("Container title attribute is empty")
            return container_id
        except NoSuchElementException as e:
            raise NoSuchElementException("Failed to get container ID") from e
        finally:
            logging.info(f"Container ID Founded: {container_id}")

    def open(self) -> None:
        """
        Open the container details by clicking its link.
        
        Raises:
            NoSuchElementException: If the container link cannot be found
            ElementClickInterceptedException: If the container link cannot be clicked
        """
        try:
            container_link = WebDriverWait(self.container, TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, CONTAINER_LINK_XPATH))
            )
            container_link.click()
            time.sleep(2)
        except ElementClickInterceptedException as e:
            raise ElementClickInterceptedException(
                "Container link click was intercepted"
            ) from e
        except TimeoutException as e:
            raise TimeoutException("Container link not found within timeout period") from e
        
    def get_milestone_table(self) -> WebElement:
        """
        Get the milestone table element.
        
        Returns:
            WebElement: The table body element containing milestone information
            
        Raises:
            TimeoutException: If the milestone table cannot be found within timeout period
            NoSuchElementException: If the table body cannot be found
        """
        try:
            logging.info(f"Getting milestone table...")
            milestone_table = WebDriverWait(self.shipment_page, TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, DETAIL_INFO_ID))
            )
            return milestone_table.find_element(By.XPATH, "./tbody")
        except TimeoutException as e:
            raise TimeoutException(
                f"Milestone table not found within {TIMEOUT} seconds"
            ) from e
        except NoSuchElementException as e:
            raise NoSuchElementException(
                "Table body element not found in milestone table"
            ) from e
    
    def get_milestones(self) -> List[Milestone]:
        """
        Get all milestones associated with this container.
        
        Returns:
            List[Milestone]: List of Milestone objects for this container
            
        Raises:
            TimeoutException: If milestone rows cannot be found within timeout period
        """
        try:
            logging.info(f"Getting milestones...")
            milestones = WebDriverWait(self.get_milestone_table(), TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, MILESTONE_ROW_XPATH))
            )
            logging.info(f"Found {len(milestones)} milestones...")
            return [Milestone(milestone) for milestone in milestones]
        except TimeoutException as e:
            raise TimeoutException(
                f"Milestone rows not found within {TIMEOUT} seconds"
            ) from e
