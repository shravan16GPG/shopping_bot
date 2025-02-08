import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pathlib import Path

# Define user data directory for session persistence
USER_DIR = Path("user_data").absolute()
if not USER_DIR.exists():
    USER_DIR.mkdir()

profile = "marketplace"
CHROMEDRIVER_PATH = Path("chromedriver/chromedriver.exe").absolute()

def create_driver(profile_name):
    """Creates a WebDriver instance for a given profile name using absolute paths."""
    try:
        options = uc.ChromeOptions()
        profile_path = USER_DIR / profile_name
        options.add_argument(f"--user-data-dir={str(profile_path)}") # Use saved session
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--dns-prefetch-disable")
        options.add_argument("--disable-gpu")

        driver = uc.Chrome(
            options=options,
            driver_executable_path=str(CHROMEDRIVER_PATH) # Use string format for path
        )
        driver.maximize_window()
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        print(e)
        return None


def search_marketplace(driver, product_name="used lenovo laptops"):
    """Search for a product in Facebook Marketplace, open seller profiles, and start a chat."""
    
    try:
        # Convert product name to URL-friendly format
        search_query = product_name.replace(" ", "%20")
        marketplace_url = f"https://www.facebook.com/marketplace/search/?query={search_query}"

        driver.get("https://www.facebook.com/marketplace")
        time.sleep(5)  # Wait for the page to load

        # 🔹 Search for "Used iPhone"
        search_box = driver.find_element(By.XPATH, '//input[@placeholder="Search Marketplace"]')
        search_box.send_keys("Used iPhone")
        search_box.send_keys(Keys.RETURN)

        time.sleep(5)  # Wait for search results to load
        print("✅ Search completed!")

        # 🔹 Open first 5 listings
        listings = driver.find_elements(By.XPATH, '//a[contains(@href, "/marketplace/item/")]')[:5]  # First 5 listings
        for listing in listings:
            driver.execute_script("window.open(arguments[0]);", listing.get_attribute("href"))
            time.sleep(3)

        # Switch to each tab and message the seller
        for handle in driver.window_handles[1:]:
            driver.switch_to.window(handle)
            try:
                # Click "Message" button
                message_button = driver.find_element(By.XPATH, '//div[contains(text(), "Message")]')
                message_button.click()
                time.sleep(2)

                # Click the "Message" button
                message_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[text()='Message']"))
                )
                message_button.click()
                print("Clicked Message button.")

                # Wait for chat box to appear
                time.sleep(2)

                # Send an initial message
                chat_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Message']"))
                )
                chat_box.send_keys("Hi! I'm interested in your item. Is it still available? 😊")
                chat_box.send_keys("\n")  # Simulate pressing Enter
                
                print("Message sent successfully!")

            except Exception as e:
                print("Error interacting with seller:", e)

            # Close the current tab and switch back
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print("Error during Marketplace search:", e)





def main():
    driver = create_driver(profile_name=profile)
    if driver is not None:
        print("Please log in manually if needed. Waiting for 60 seconds...")
        time.sleep(5)  # Allow time for manual login if required
        
        search_marketplace(driver)

        input("Press Enter to exit...")  # Keeps the browser open until user exits
        driver.quit()
    else:
        print("Some error occurred")

if __name__ == "__main__":
    main()
