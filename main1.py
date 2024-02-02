import argparse
from database import Database
from save import save
import requests
import re
# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import time
'''
Idea: 
By getting the number of pages in the websites, a loop can be used to iterate each of the page. 
For every iteration (page), it stores all the button that directs to the detailed page.
For every button, it direct into its detailed page and extract the information.
'''
na_count = 0
URL = ""
PAGE = 0

def extract_data(url, database, pg, state):
    print(f"Current: {url}")
    print(f"Current page: {pg}")

    isTitle = False

    # Check if the state_code input is list or not
    isList = isinstance(state, list)
    if not isList:
        state = [state]


    # print(driver)    
    # try:
    #     _ = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[6]/div/table/tbody')))
    #     print("Data available, continue to scraping data...")
    # except:
    #     print("Something went wrong, data not found or not available.")
    #     driver.quit()
    #     return
    for i, s in enumerate(state):
        # Format of url: https://teduh.kpkt.gov.my/project-swasta?search_type=pemaju&page=1&state=01
        if i == 0:
            current_state = None
            url = url.replace("state=01", f"state={s}")
        else:
            url = url.replace(f"state={current_state}", f"state={s}")

        driver = connect(url)        
        # url = url.replace(f"state=01")

        # total_pages = extract_pages(driver) + 1
        print("here221")
        # print(f"{pg}, {page}")
        while True:
        # for page in range(pg, total_pages):
            print("here1")
            URL = url
            # PAGE = pg
            print("here2")
            if pg == PAGE:
                current_page = None
                if pg == 1:
                    pass
                else:
                    url = url.replace('page=1', f'page={pg}')
            else:
                print("here")
                print(current_page)
                # print(page)
                url = url.replace(f'page={current_page}', f'page={pg}')
            print(f"The next page url: {url}")
            driver = connect(url)

            buttons = extract_buttons(driver)
            for i, button in enumerate(buttons):
                print(f"The {i+1} link out of {len(buttons)} in page {pg}")
                print(f"button: {button.get_attribute('href')}")
                driver.implicitly_wait(5)
                driver = connect(button.get_attribute('href'))
                soup = BeautifulSoup(driver.page_source, 'lxml')

                if not isTitle:
                    print("Storing title...")
                    extract_information_title(soup, database)
                    isTitle = True
                website_location = f"{i+1}, {pg}, {s}"
                extract_information(soup, database, str(driver.current_url), website_location)
                print("Information extraction complete. Proceed to the next link...")
            current_page = pg
            pg += 1
            driver.implicitly_wait(10)
        current_state = s
        driver.implicitly_wait(10)

def extract_pages(driver):
    '''
    This function get the number of pages in the website
    
    Output: the amount of pages in the website
    '''
    pages = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.page-link")))
    # print(pages)
    print(f'\nPages to be scraped: {pages[-2].text}\n')
    pages_number = int(pages[-2].text)
    return 1

def extract_buttons(driver):
    '''
    As the websites contains a number of lists where its detail can be viewed by click on the button, 
    so the location of the buttons is find and store in a lists

    Output: a lists of buttons that present in the PARTICULAR page and directs to details page .
    '''
    try:
        button = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.btn.btn-primary")))
        print("All the link gathered. Iterating each link...") 
        # print(button)
        return button[:5] 
    except:
        print("There is no button available.")
        return

def extract_information_title(soup, db):
    '''
    The information title on every lists is extract and store in the key of dictionary.

    Output: the key of dictionary of information on every lists in EACH page.

    Note:
    1. p.font-bold.text-xs.md:text-sm (CSS Selector) - Lists of 'Maklumat Pemaju' title
    2. p.font-bold.text-sm (CSS Selector) - Lists of 'Ringkasan Projek' title
    3. thead.bg-teduh-mid.bg-opacity-80.py-4 (CSS Selector) - Lists of 'Pembangunan Projek' title
    '''
    maklumat_pemaju_list = []
    ringkasan_projek_list = []
    pembangunan_projek_list = []
    location_list = ["Location", "Address"]
    
    try:
        maklumat_pemaju = soup.find_all("p", class_="font-bold text-xs md:text-sm")
        ringkasan_projek = soup.find_all("p", class_="font-bold text-sm")
        pembangunan_projek = soup.find_all("th")

        for m in maklumat_pemaju:
            maklumat_pemaju_list.append(m.text)
        for r in ringkasan_projek:
            ringkasan_projek_list.append(r.text)
        for p in pembangunan_projek:
            pembangunan_projek_list.append(p.text)
    except:
        print("Warning: Title not found, but this will not crush the progress.")
        pass

    title = [maklumat_pemaju_list, ringkasan_projek_list, pembangunan_projek_list, location_list]
    db.store_information_titles(title)
    # print(title)

def extract_information(soup, db, url, website_location):
    '''
    The information on every lists is extract and store in a dictionary.

    Output: Information stored in databse forr EACH page detail.

    Note:
    1. p.font-medium.text-xs.md:text-sm (CSS Selector) - Lists of 'Maklumat Pemaju' information (the last index is not relevant and ned to be excluded)
    2. p.font-medium.text-sm (CSS Selector) - Lists of 'Ringkasan Project' information
    3. tbody.bg-teduh-mid.bg-opacity-25 (CSS Selector) - All 'Pembangunan Projek' information
    4. 3 -> tr - Lists of 'Pembangunan Projek' information in 'Pembangunan Projek' row
    5. 5 -> td.text-center - Elements in 'Pembangunan Projek' row
    6. div.place-name (CSSS Selector) - Location 
    7. div.address (CSS Selector) - Address
    8. p.text-center.font-semibold.text-white (CSS Selector) - The project title
    9. p.font-medium.text-sm (CSS Selector) - The unique project code
    '''
    proj_url = url
    maklumat_pemaju_info_list = []
    ringkasan_projek_info_list = []
    pembangunan_projek_info_list = []
    location_list = []

    # Project title
    try:
        proj_id = soup.find("p", class_="font-medium text-sm")
        project_id = " ".join((proj_id.text.replace("\n", "").strip()).strip())
        
        proj_name = soup.find("p", class_="text-center font-semibold text-white")
        project_name = " ".join((proj_name.text.replace("\n", "").strip()).strip())

        project_title = f"{project_id} - {project_name}"
    except:
        print("Warning: Project title not found, a blank will be returned instead")
        na_count += 1
        project_title = f"N/A - {na_count}"

    # Maklumat Pemaju
    try:
        maklumat_pemaju_info = soup.find_all("p", class_="font-medium text-xs md:text-sm")
        maklumat_pemaju_info = maklumat_pemaju_info[:-1]
        ringkasan_projek_info = soup.find_all("p", class_="font-medium text-sm")

        for m in maklumat_pemaju_info:
            maklumat_pemaju_info_list.append(" ".join((m.text.replace("\n", "").strip()).split()))
        for r in ringkasan_projek_info:
            ringkasan_projek_info_list.append(" ".join((r.text.replace("\n", "").strip()).split()))

    except Exception as e:
        print("Warning: Failed to retreive project information, the information for this project will leave blank.")
        print(f"Error: {e}")

    # Pembangunan Projek
    try:
        all_pembangunan_projek_info = soup.find("tbody", class_="bg-teduh-mid bg-opacity-25").find_all("tr")
        print(f"all pembangunan projek is {all_pembangunan_projek_info}")
        if all_pembangunan_projek_info is None:
            pass
        else:
            for project_row in all_pembangunan_projek_info:
                pembangunan_projek_detail = project_row.find_all("td", class_="text-center")

                temp = []
                for element in pembangunan_projek_detail:
                    temp.append(" ".join((element.text.replace("\n", "").strip()).split()))
                pembangunan_projek_info_list.append(temp.copy())
        print(f"check {pembangunan_projek_info_list}")
        # Location
        iframe_tag = soup.find('iframe')

        if iframe_tag:
            iframe_src = iframe_tag.get('src')

            # Now, you can make a new request to the iframe URL and parse its content
            iframe_response = requests.get(iframe_src)
            iframe_soup = BeautifulSoup(iframe_response.text, 'html.parser')
            iframe_script = iframe_soup.find("script").text

            # Extract the coordinates using a regular expression
            coordinates_match = re.search(r'\["(-?\d+\.\d+), (-?\d+\.\d+)"\]', iframe_script)
            coordinates = coordinates_match.group(0) if coordinates_match else None

            # Extract the location name using a different regular expression
            location_match = re.search(r'[^,]*,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*null,\s*"([^"]*)"', iframe_script)
            location = location_match if location_match else None

        coordinates = None if coordinates == '["1.000000, 1.000000"]' else coordinates
        location_list = [coordinates, location]

    except Exception as e:
        print("Soft Warning: Some of the information are not available or failed to achieved. Please refer the error: ")
        print(f"Error: {e}")


    data = (maklumat_pemaju_info_list, ringkasan_projek_info_list, pembangunan_projek_info_list, location_list)

    print("All the info gathered. Updating database...")

    db.add_project(project_title, proj_url, data, website_location)

def connect(url):
    driver = webdriver.Chrome()
    driver.get(url)
    # lists = EC.presence_of_element_located((By.XPATH, '//h3[@class="listing-name"]'))
    return driver

def run(url, db, save_count, state, pg, attempt=10):
    if attempt == 0:
        return
    try:
        extract_data(url, db, pg, state)
    except:
        print("Unexpected error occurred, saving the progress")
        dicts = db.get_project_data()
        # print(dicts)
        sc = save(dicts, save_count)
        print("Data saved")

        times = 60
        
        print(f"New attempt retry in {times/60} minutes")
        print(f"Attempt left {attempt}")

        time.sleep(times)   

        # Rerun again with previous final progress, the previous one is saved and have to be cleared
        attempt -= 1
        save_count = sc
        url = URL
        pg = PAGE
        db = Database()
        run(url, db, save_count, state, pg, attempt)

def get_state(state):
    if state == '0':
        return ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '14', '16']
    else:
        return state

def opt():
    state_code = "01 - Johor\n02 - Kedah\n03 - Kelantan\n04 - Melaka\n05 - Negeri Sembilan\n06 - Pahang\n07 - Pulau Pinang\n08 - Perak\n09 - Perlis\n10 - Selangor\n11 - Terengganu\n14 - Wilayah KL\n16 - Wilayah Putrajaya\n"

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", type=str, default="https://teduh.kpkt.gov.my/project-swasta?search_type=pemaju&page=1&state=01")
    parser.add_argument("-p", "--page", type=int, default=1)
    parser.add_argument("-s", "--state", type=str, default=0, help=state_code)

    return parser.parse_args()

def main(args):
    save_count = 2
    URL = args.url
    PAGE = args.page
    state = get_state(args.state)
    # print(state)
    # return
    database = Database()

    run(args.url, database, save_count, state, args.page)

    # print("heressss")    
    dicts = database.get_project_data()
    # print(dicts)
    save(dicts, save_count)
    return 0

if __name__ == "__main__":
    args = opt()
    print(args)
    # print("s")
    main(args)