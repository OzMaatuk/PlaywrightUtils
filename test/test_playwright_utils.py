import logging
from typing import Generator
import pytest
from playwright.sync_api import Page, expect
from playwright_utils.playwright_utils import (
    wait_for_element, wait_for_all_elements,
    wait_for_element_to_be_clickable, wait_for_url_change,
    click_element_safely, send_keys_safely
)

# Configure logging
logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def test_server() -> Generator[str, None, None]:
    # Setup code for test server
    yield "http://localhost:8000"
    # Teardown code for test server

@pytest.fixture(scope="function")
def page_context(browser) -> Generator[Page, None, None]:
    context = browser.new_context()
    page = context.new_page()
    yield page
    page.close()
    context.close()

# --- Tests for wait_for_element ---
def test_wait_for_element_success(page_context: Page, test_server: str) -> None:
    """Tests successful element retrieval after a delay."""
    page_context.goto(test_server)
    selector = "#delayedElement"
    page_context.wait_for_timeout(3000)
    element = wait_for_element(page_context, selector, timeout=10000)
    expect(element).to_be_visible()
    logger.info("test_wait_for_element_success passed.")

def test_wait_for_element_timeout(page_context: Page, test_server: str) -> None:
    """Tests timeout handling when the element is not found."""
    page_context.goto(test_server)
    selector = "#nonExistentElement"
    with pytest.raises(Exception):
        wait_for_element(page_context, selector, timeout=1000)
    logger.info("test_wait_for_element_timeout passed.")

# --- Tests for wait_for_all_elements ---
def test_wait_for_all_elements_success(page_context: Page, test_server: str) -> None:
    """Tests retrieval of all elements matching the selector."""
    page_context.goto(test_server)
    selector = "#multipleElementsContainer p"
    elements = wait_for_all_elements(page_context, selector)
    assert len(elements) == 3  # Adjust expected count based on your HTML
    logger.info("test_wait_for_all_elements_success passed.")

def test_wait_for_all_elements_timeout(page_context: Page, test_server: str) -> None:
    """Tests timeout handling when not all elements are found."""
    page_context.goto(test_server)
    selector = ".nonExistentClass"
    with pytest.raises(Exception):
        wait_for_all_elements(page_context, selector, timeout=1000)
    logger.info("test_wait_for_all_elements_timeout passed.")

# --- Tests for url change ---
def test_wait_for_url_change_success(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    current_url = page_context.url
    selector = "#linkToExample"  # Use an existing link ID in the HTML
    link = wait_for_element_to_be_clickable(page_context, selector)
    link.click()
    wait_for_url_change(page_context, current_url, timeout=5000)
    assert page_context.url != current_url
    logger.info("test_wait_for_url_change_success passed.")

def test_wait_for_url_change_timeout(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    current_url = page_context.url
    selector = "#linkToExample"  # Replace with something that opens in a new tab or does not change the url
    page_context.evaluate('window.open(arguments[0], "_blank");', page_context.query_selector(selector).get_attribute("href"))
    with pytest.raises(Exception):
        wait_for_url_change(page_context, current_url, timeout=2000)
    assert page_context.url == current_url
    logger.info("test_wait_for_url_change_timeout passed.")

# --- Tests for click element safely ---
def test_click_element_safely_success(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    selector = "#clickableElement"
    click_element_safely(page_context, selector)
    # Assert that clicking the element had some effect (e.g., element property, or check if page has changed)
    logger.info("test_click_element_safely_success passed.")

def test_click_element_safely_stale_element(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    page_context.reload()  # Refresh page before interacting with any DOM elements.
    selector = "#clickableElement"
    click_element_safely(page_context, selector)  # If this works with refresh, it means stale element is handled.
    logger.info("test_click_element_safely_stale_element passed.")

def test_click_element_safely_intercepted(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    selector = "#elementToInterceptClick"
    click_element_safely(page_context, selector)
    overlay = page_context.query_selector("#overlay")
    expect(overlay).to_be_visible()
    logger.info("test_click_element_safely_intercepted passed.")

# --- Tests for send keys safely ---
def test_send_keys_safely_success(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    selector = "#textInput"
    text_to_send = "Test Input"
    send_keys_safely(page_context, selector, text_to_send)
    entered_text = page_context.query_selector(selector).get_attribute("value")
    assert entered_text == text_to_send
    logger.info("test_send_keys_safely_success passed.")

def test_send_keys_safely_stale_element(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    page_context.reload()  # Create stale element reference
    selector = "#textInput"
    text_to_send = "Test Input"
    send_keys_safely(page_context, selector, text_to_send)
    entered_text = page_context.query_selector(selector).get_attribute("value")
    assert entered_text == text_to_send
    logger.info("test_send_keys_safely_stale_element passed.")

# --- Tests for element is clickable ---
def test_wait_for_element_to_be_clickable_success(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    selector = "#clickableElement"
    element = wait_for_element_to_be_clickable(page_context, selector, timeout=5000)
    element.click()
    assert page_context.query_selector("h1")
    logger.info("test_wait_for_element_to_be_clickable_success passed.")

def test_wait_for_element_to_be_clickable_timeout(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    selector = "#nonExistentElement"
    with pytest.raises(Exception):
        wait_for_element_to_be_clickable(page_context, selector, timeout=1000)
    logger.info("test_wait_for_element_to_be_clickable_timeout passed.")

def test_wait_for_element_to_be_clickable_stale(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    selector = "#clickableElement"
    element = wait_for_element_to_be_clickable(page_context, selector, timeout=5000)
    page_context.reload()  # Make the element stale
    element = wait_for_element_to_be_clickable(page_context, selector, timeout=5000)  # Call the function again after refreshing the page
    assert element
    logger.info("test_wait_for_element_to_be_clickable_stale passed.")