from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time
import os

class LoginTest:
    def __init__(self, headless=False):
        # Setup logging
        self.setup_logging()

        # Configure Chrome options
        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 10)
            logging.info("WebDriver initialized successfully")
        except WebDriverException as e:
            logging.error(f"Failed to initialize WebDriver: {str(e)}")
            raise

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('login_automation.log'),
                logging.StreamHandler()
            ]
        )

    def wait_and_find_element(self, by, value, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logging.error(f"Element not found: {value}")
            self.take_screenshot(f"element_not_found_{value}")
            raise

    def take_screenshot(self, name):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshots/{name}_{timestamp}.png"
        try:
            self.driver.save_screenshot(filename)
            logging.info(f"Screenshot saved: {filename}")
        except Exception as e:
            logging.error(f"Failed to take screenshot: {str(e)}")

    def login(self, email, password):
        try:
            # Navigate to login page
            logging.info("Navigating to login page...")
            self.driver.get("https://dev-app.yirifi.ai/auth/login")

            # Find and fill email field
            username_field = self.wait_and_find_element(
                By.CSS_SELECTOR, "input[type='email']"
            )
            username_field.clear()
            username_field.send_keys(email)
            logging.info("Email entered successfully")

            # Find and fill password field
            password_field = self.wait_and_find_element(
                By.CSS_SELECTOR, "input[type='password']"
            )
            password_field.clear()
            password_field.send_keys(password)
            logging.info("Password entered successfully")

            # Click login button
            login_button = self.wait_and_find_element(
                By.CSS_SELECTOR, "button[type='submit']"
            )
            login_button.click()
            logging.info("Login button clicked")

            # Verify successful login
            try:
                # Wait for dashboard element or any element that confirms successful login
                self.wait_and_find_element(By.CSS_SELECTOR, ".dashboard-element")
                logging.info("Login successful - Dashboard loaded")
                return True
            except TimeoutException:
                logging.error("Login failed - Dashboard not loaded")
                self.take_screenshot("login_failed")
                return False

        except Exception as e:
            logging.error(f"Login failed with error: {str(e)}")
            self.take_screenshot("login_error")
            raise

    def verify_login_status(self):
        try:
            # Add verification logic here
            current_url = self.driver.current_url
            logging.info(f"Current URL after login: {current_url}")
            return "dashboard" in current_url.lower()
        except Exception as e:
            logging.error(f"Failed to verify login status: {str(e)}")
            return False

    def teardown(self):
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
                logging.info("WebDriver closed successfully")
            except Exception as e:
                logging.error(f"Failed to close WebDriver: {str(e)}")


def main():
    test = None
    try:
        test = LoginTest(headless=False)
        if test.login(os.getenv("EMAIL"),os.getenv("PASSWORD")):
            time.sleep(2)
            if test.verify_login_status():
                logging.info("Login verification successful")
            else:
                logging.warning("Login verification failed")
    except Exception as e:
        logging.error(f"Test failed: {str(e)}")
    finally:
        if test:
            test.teardown()


if __name__ == "__main__":
    main()