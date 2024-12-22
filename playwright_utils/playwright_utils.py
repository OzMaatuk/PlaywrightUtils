# src/playwright_utils.py

import logging
from typing import Optional, List
from playwright.sync_api import Page, Locator

logger = logging.getLogger(__name__)

def wait_for_element(page: Page, selector: str, timeout: int = 10000) -> Locator:
    logger.debug(f"wait_for_element: {selector}")
    return page.wait_for_selector(selector, timeout=timeout)

def wait_for_all_elements(page: Page, selector: str, timeout: int = 10000) -> List[Locator]:
    logger.debug(f"wait_for_all_elements: {selector}")
    return page.query_selector_all(selector)

def wait_for_element_to_be_clickable(page: Page, selector: str, timeout: int = 10000) -> Locator:
    logger.debug(f"wait_for_element_to_be_clickable: {selector}")
    element = wait_for_element(page, selector, timeout)
    page.wait_for_function("element => element.click()", element)
    return element

def wait_for_url_change(page: Page, current_url: str, timeout: int = 10000) -> None:
    logger.debug(f"wait_for_url_change: {current_url}")
    page.wait_for_url(lambda url: url != current_url, timeout=timeout)

def click_element_safely(page: Page, selector: str, timeout: int = 10000) -> None:
    logger.debug(f"click_element_safely: {selector}")
    element = wait_for_element_to_be_clickable(page, selector, timeout)
    element.click()

def send_keys_safely(page: Page, selector: str, text: str, timeout: int = 10000) -> None:
    logger.debug(f"send_keys_safely: {selector}, {text}")
    element = wait_for_element(page, selector, timeout)
    element.fill(text)

def get_element_text(page: Page, selector: str) -> Optional[str]:
    logger.debug(f"get_element_text: {selector}")
    element = wait_for_element(page, selector)
    return element.inner_text().strip() if element else None

def get_element_attribute(page: Page, selector: str, attribute: str) -> Optional[str]:
    logger.debug(f"get_element_attribute: {selector}, {attribute}")
    element = wait_for_element(page, selector)
    return element.get_attribute(attribute) if element else None

def check_element_exist(page: Page, selector: str) -> bool:
    logger.debug(f"check_element_exist: {selector}")
    try:
        wait_for_element_to_be_clickable(page, selector)
        return True
    except Exception:
        return False

def scroll_to_bottom(page: Page) -> None:
    logger.debug("scroll_to_bottom")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
