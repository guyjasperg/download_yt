from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import webbrowser
import time

def get_cookies():
    url = f"https://mydramalist.com"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # Remove this line for headed mode.
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)
    
    # Get all cookies
    cookies = driver.get_cookies()
    
    with open('cookies.json', 'w') as f:
        json.dump(cookies, f)
        
    driver.quit()

def get_kdrama_episodes_selenium(kdrama_slug):
    url = f"https://mydramalist.com/{kdrama_slug}/episodes"

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new") # Remove this line for headed mode.
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(url)

        # Load cookies from file
        with open('cookies.json', 'r') as f:
            cookies = json.load(f)

        for cookie in cookies:
            # Selenium needs the expiry to be an integer.
            if 'expiry' in cookie:
                cookie['expiry'] = int(cookie['expiry'])
            driver.add_cookie(cookie)
            
        driver.get(url)
                
        # Add cookies to the driver
        # for cookie in cookies:
        #     # Selenium needs the expiry to be an integer.
        #     if 'expiry' in cookie:
        #         cookie['expiry'] = int(cookie['expiry'])
        #     driver.add_cookie(cookie)
            
        # Refresh the page to apply cookies
        # driver.get(url)
        
        print(driver.page_source)
        
        try:
            WebDriverWait(driver, 5).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".episodes.clear.m-t .episode")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[id$='_response']"))
                )
            )
        except Exception as e:
            print("Timeout waiting for content or Turnstile challenge.")
            driver.quit()
            return None

        if "challenges.cloudflare.com" in driver.page_source:
            print("Cloudflare Turnstile challenge detected. Please solve the challenge in the browser.")
            
            webbrowser.open(url) #opens the current url in the default browser.
            
            input("Press Enter after solving the challenge in the browser...") #pause the script until the user presses enter.
            
            input("Press Enter after solving the challenge...")

            WebDriverWait(driver, 60).until(lambda driver: driver.find_element(By.CSS_SELECTOR, "[id$='_response']").get_attribute("value"))

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".episodes.clear.m-t .episode"))
            )

        soup = BeautifulSoup(driver.page_source, "html.parser")

        episode_list = []
        episodes = soup.select('.episodes.clear.m-t .episode')
        for episode in episodes:
            title_element = episode.select_one('.title a')
            air_date_element = episode.select_one('.air-date')

            title = title_element.text.strip().replace(u'\xa0', u' ') if title_element else None
            air_date = air_date_element.text.strip().replace(u'\xa0', u' ') if air_date_element else None

            if title and air_date:
                episode_list.append({
                    "title": title,
                    "airDate": air_date,
                })

        driver.quit()
        return episode_list

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# get_cookies()
episodes = get_kdrama_episodes_selenium("765779-undercover-high-school") #replace with your kdrama
if episodes:
    print(episodes)