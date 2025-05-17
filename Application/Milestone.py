from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from typing import Optional, Tuple

import logging
from Application.logging_config import setup_logger
setup_logger()

# Constants for event mapping
EVENTS = [
    ('gate in', 'Gate In'),
    ('departure from port of loading', 'Departure'),
    ('arrival at port of discharging', 'Arrival'),
    ('gate out', 'Gate Out')
]

# XPath/selectors
EVENT_CELL_XPATH = "./td[2]"
DATE_CELL_XPATH = "./td[4]"
LOCATION_CELL_XPATH = "./td[3]"
VESSEL_LINK_XPATH = "./a"


class Milestone:
    """
    Represents a shipping milestone with event, date, location, and vessel information.
    
    Attributes:
        milestone (WebElement): The Selenium WebElement containing milestone data
        event (str): The normalized event name
        date (str): The milestone date
        location (str): The milestone location
        vessel_name (Optional[str]): The name of the vessel if available
        vessel_id (Optional[str]): The ID of the vessel if available
        voyage_id (Optional[str]): The voyage ID if available
    """
    
    def __init__(self, milestone: WebElement) -> None:
        """
        Initialize a Milestone instance.
        
        Args:
            milestone (WebElement): The Selenium WebElement containing milestone data
     
        """
            
        self.milestone = milestone
        self.event: str = self.get_event()
        self.date: str = self.get_date()
        self.location: str = self.get_location()
        self.vessel_name: Optional[str] = None
        self.vessel_id: Optional[str] = None

    def get_event(self) -> str:
        """
        Extract and normalize the event name from the milestone element.
        
        Returns:
            str: The normalized event name
            
        Raises:
            NoSuchElementException: If the event cell cannot be found
        """
        try:
            logging.info(f"Getting event...")
            event = self.milestone.find_element(By.XPATH, EVENT_CELL_XPATH)
            self._extract_vessel_info(event)
            return self.normalize_event(event.text.split('\n')[0])
        except NoSuchElementException as e:
            raise NoSuchElementException("Failed to find event cell in milestone") from e
    
    def _extract_vessel_info(self, event_element: WebElement) -> None:
        """
        Extract vessel information from the event element if available.
        
        Args:
            event_element (WebElement): The event cell WebElement
        """
        try:
            vessel = event_element.find_element(By.XPATH, VESSEL_LINK_XPATH)
            self.vessel_name = vessel.get_attribute("title")
            self.vessel_id = vessel.text.split()[-1]
            logging.info(f'Extracted vessel info: {self.vessel_name} - {self.vessel_id}')
        except NoSuchElementException:
            logging.info("No vessel info found..")
            pass
    
    def normalize_event(self, event: str) -> str:
        """
        Normalize the event name based on predefined patterns.
        
        Args:
            event (str): The raw event name to normalize
            
        Returns:
            str: The normalized event name
        """
        match_string = event.lower().strip()
        
        if match_string.startswith('unloaded') and match_string.endswith('discharging'):
            return 'Discharge'

        for event_pattern, event_name in EVENTS:
            if event_pattern in match_string:
                return event_name
        logging.info(f"No match found for event: {event}")
        return event

    def get_date(self) -> str:
        """
        Extract the date from the milestone element.
        
        Returns:
            str: The milestone date
            
        Raises:
            NoSuchElementException: If the date cell cannot be found
        """
        try:
            logging.info(f"Getting date...")
            date = self.milestone.find_element(By.XPATH, DATE_CELL_XPATH).text
            return " ".join(date.split()[1:]) if date else 'No Date Available'
        
        except NoSuchElementException as e:
            raise NoSuchElementException("Failed to find date cell in milestone") from e
    
    def get_location(self) -> str:
        """
        Extract the location from the milestone element.
        
        Returns:
            str: The milestone location
            
        Raises:
            NoSuchElementException: If the location cell cannot be found
        """
        try:
            logging.info(f"Getting location...")
            return self.milestone.find_element(By.XPATH, LOCATION_CELL_XPATH).text
        except NoSuchElementException as e:
            raise NoSuchElementException("Failed to find location cell in milestone") from e

