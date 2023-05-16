# site_preview.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.actions.interaction import KEY
from selenium.webdriver.common.actions.key_input import KeyInput
from uuid import uuid4
import os

class SitePreview:
    def __init__(self, site_generator, screenshot_dir="screenshots"):
        self.site_generator = site_generator
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)  # Ensure the directory exists
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def generate_screenshot(self, site):
        try:
            # Navigate to the site
            self.driver.get(site.url)
        except Exception as e:
            print(f"An error occurred while loading the site: {str(e)}")
            return None

        # Create a unique filename for the screenshot
        screenshot_path = os.path.join(self.screenshot_dir, f"{uuid4()}.png")
        try:
            # Take a screenshot and save it
            self.driver.save_screenshot(screenshot_path)
        except Exception as e:
            print(f"An error occurred while saving the screenshot: {str(e)}")
            return None

        return screenshot_path

    def generate_preview(self, template_name, text, category):
        site = self.site_generator.generate(template_name, text, category)
        # Generate and return a screenshot of the site
        preview = self.generate_screenshot(site)
        return preview

    def __del__(self):
        # Make sure to quit the driver when we're done with it
        self.driver.quit()

