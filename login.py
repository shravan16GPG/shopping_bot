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
        # 🔽 Disable pop-up blocking 🔽
        options.add_argument("--disable-popup-blocking")

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

def manual_login_setup(profile_name):
    """Sets up the driver and allows the user to manually log in."""
    driver = create_driver(profile_name=profile_name)
    if driver is not None:
        print("Please log in manually in the opened browser window.")
        print("Once logged in, you can close the browser or leave it open.")
        print("After login, press Enter in the console to continue or just close the browser if only login is needed.")
        input("Press Enter to continue after login (or just close browser for login only)...")
        print("Login process completed or skipped.")
        return driver
    else:
        print("Failed to create driver instance for manual login.")
        return None


def marketplace_scraper(driver, product_name="used iphone"): # Changed default to "used iphone" as in original code
    """Scrapes Facebook Marketplace for the given product name using the provided driver."""
    if driver is None:
        print("Driver is not initialized. Please ensure manual login setup is done correctly.")
        return

    try:
        # Convert product name to URL-friendly format
        search_query = product_name.replace(" ", "%20")
        marketplace_url = f"https://www.facebook.com/marketplace/search/?query={search_query}"

        driver.get("https://www.facebook.com/marketplace")
        time.sleep(5)  # Wait for the page to load

        # 🔹 Search for product
        search_box = driver.find_element(By.XPATH, '//input[@placeholder="Search Marketplace"]')
        search_box.send_keys(product_name) # Use product_name parameter here
        search_box.send_keys(Keys.RETURN)

        time.sleep(5)  # Wait for search results to load
        print("✅ Search completed!")

        # 🔹 Open first 5 listings -  STRUCTURE BASED FINDING (CONTAINING max-width and min-width in style)
        listings = driver.find_elements(By.XPATH, '//div[contains(@style, "max-width") and contains(@style, "min-width")]//a[contains(@href, "/marketplace/item/")]')[:5]  # First 5 listings
        print(f"Found {len(listings)} listings based on structure (containing max-width and min-width in style).") # Debug print
        if not listings:
            print("No listings found using structure-based XPath (containing max-width and min-width in style). Check HTML structure for changes.")
            return  # Exit if no listings found
        print(listings)
        for listing in listings:
            print("doing this", listing.get_attribute("href"))
            driver.execute_script("window.open(arguments[0]);", listing.get_attribute("href"))
            # 🔽 Increased sleep time 🔽
            time.sleep(5)

        # Switch to each tab and message the seller
        for handle in driver.window_handles[1:]:
            driver.switch_to.window(handle)
            try:
                # 1. Click "Send" button - Structure and aria-label based
                
                # find the sen button normally
                time.sleep(3)
                send_message_button = driver.find_element(By.XPATH, '//div[@aria-label="Send" and @role="button"]')
                print(send_message_button)
                if send_message_button:
                    print("Clicked 'Send' button on listing page.")
                    driver.execute_script("arguments[0].click();", send_message_button)
                    
                    # send_message_button.click()
                
                time.sleep(2) # Delay after clicking Send button

                # # 2. Wait for chat box to appear (Reusing existing chat box wait logic)
                # chat_box = WebDriverWait(driver, 10).until(
                #     EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Message']"))
                # )

                # # 3. Send an initial message (Reusing existing message sending logic)
                # chat_box.send_keys("Hi! I'm interested in your item. Is it still available? 😊")
                # chat_box.send_keys("\n")  # Simulate pressing Enter
                # print("Message sent successfully!")


            except Exception as e:
                print(f"Error interacting with seller in listing tab: {e}")
                raise e

            # Close the current tab and switch back
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print("Error during Marketplace search:", e)
        raise e


def main():
    """Main function to orchestrate user choice, manual login, and marketplace scraping."""

    while True: # Loop to allow user to choose again if needed
        print("\nChoose an option:")
        print("1. Manual Login Only")
        print("2. Marketplace Scraping (Assume already logged in)")
        print("3. Login then Scrape")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            print("\n--- Manual Login Only ---")
            driver = manual_login_setup(profile_name=profile)
            if driver:
                input("Press Enter to exit after manual login setup...")
                driver.quit()
            else:
                print("Manual login setup failed.")
            break # Exit loop after this option

        elif choice == '2':
            print("\n--- Marketplace Scraping (Assuming Logged In) ---")
            driver = create_driver(profile_name=profile) # Create driver assuming logged in session
            if driver:
                marketplace_scraper(driver)
                input("Press Enter to exit after scraping...")
                driver.quit()
            else:
                print("Failed to create driver for scraping (logged in session may not exist).")
            break # Exit loop after this option

        elif choice == '3':
            print("\n--- Login then Scrape ---")
            driver = manual_login_setup(profile_name=profile)
            if driver:
                marketplace_scraper(driver)
                input("Press Enter to exit after login and scraping...")
                driver.quit()
            else:
                print("Login then scrape failed.")
            break # Exit loop after this option

        elif choice == '4':
            print("Exiting program.")
            break # Exit loop and program

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main()