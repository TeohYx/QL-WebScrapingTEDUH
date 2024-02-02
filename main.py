import argparse
from database import Database
from save import Save
import requests
import re
import openpyxl
import pandas as pd
# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from merge import merge
import json
import time

from memory_profiler import profile
'''
Idea: 
By getting the number of pages in the websites, a loop can be used to iterate each of the page. 
For every iteration (page), it stores all the button that directs to the detailed page.
For every button, it direct into its detailed page and extract the information.

Note: The fact is often dissappointing, as there is no one-size-fits-all solutions. The format of the website will change once the 
      server or anti-scraper bots (just guessing) had detected the scraping action. Therefore, this script contains a number of way 
      to adapt to the changes to be able to scrap the information needed.

    So far there are 2 mains ways in executing this script:
    1. Run by having key-value pairs in the link (ie. usually contains '?' symbol)
        eg: https://teduh.kpkt.gov.my/project-swasta?search_type=pemaju&page=1&state=01
        Note: search_type=pemaju is by default, just leave it there.
    2. Run by not having key-value pairs in the link 
        eg: https://teduh.kpkt.gov.my/project-swasta

    (1) When theres key-value pairs provided:

        Scenarios:
        1. 'Semua Negeri' yields all result and total page is given -> add page=  (https://teduh.kpkt.gov.my/project-swasta?search_type=pemaju&page=1)
            : Scenario = 1
        2. 'Semua Negeri' yields all result but total page is not given -> add pages=  (https://teduh.kpkt.gov.my/project-swasta?search_type=pemaju&page=1)
            : Scenario = 2
        3. 'Semua Negeri' yields no results and total page is given -> add state= (https://teduh.kpkt.gov.my/project-swasta?search_type=pemaju&page=1&state=01)
            : Scenario = 3
        4. 'Semua Negeri' yields no results and total page is not given -> add pages= (https://teduh.kpkt.gov.my/project-swasta?search_type=pemaju&page=1&state=01)
            : Scenario = 4

    (2) When there is no key-value pairs provided due to the website prohibits the input of key-value pairs, the specific code that
        lead to the specific link (place where the information is located) is needed (eg: 1-1, 1024-5, etc).

        The codes is available in PDF provided in the website (https://teduh.kpkt.gov.my/project-swasta). If 'Semua Negeri' is 
        available, the PDF would contains all the lists of codes along with some summary; if 'Semua Negeri' is not availabe, then 
        the state are required to be manually mentioned in the search bar to get the PDF. The PDF is then converted into Excel 
        format (can be found in 'InfoByStateXlsx' folder), and only the codes are extracted into the new excel file.

        However, the process had been done, and the file are named 'Code.xlsx' (Retrieved in the way that state have to be state
        manually). Just specifying valid scenario and the script will handle this case correctly.
        : Scenario = 4
'''
na_count = 0
URL = ""
PAGE = 0
FINAL_PAGE = 0

NAMES = []

def simp_extract_data(driver, database, save, total_pages, s=None):
    """
    A function that act as a continuation of extract_data function.

    total_pages of 0 means the total pages are not available to scrap in the website.
    """
    # Scenario 2/4
    if total_pages == 0:
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
                save.store_info(f"(State {s}) (Page {pg})")
                print("Information extraction complete. Proceed to the next link...")
            current_page = pg
            pg += 1
            driver.implicitly_wait(10)
    # Scenario 1/3
    else:
        for page in range(pg, total_pages):
            print("here1")
            URL = url
            PAGE = page
            print("here2")
            if page == pg:
                current_page = None
                if page == 1:
                    pass
                else:
                    url = url.replace('page=1', f'page={page}')
            else:
                print("here")
                print(current_page)
                print(page)
                url = url.replace(f'page={current_page}', f'page={page}')
            print(f"The next page url: {url}")
            driver = connect(url)

            buttons = extract_buttons(driver)
            for i, button in enumerate(buttons):
                print(f"The {i+1} link out of {len(buttons)} in page {page} out of pages {total_pages-1}")
                print(f"button: {button.get_attribute('href')}")
                driver.implicitly_wait(5)
                driver = connect(button.get_attribute('href'))
                soup = BeautifulSoup(driver.page_source, 'lxml')

                if not isTitle:
                    print("Storing title...")
                    extract_information_title(soup, database)
                    isTitle = True
                website_location = f"{i+1}, {page}, {s}"
                FINAL_PAGE = page
                extract_information(soup, database, str(driver.current_url), website_location)
                save.store_info(f"(State {s}) (Page {pg})")
                print("Information extraction complete. Proceed to the next link...")
            current_page = page
            driver.implicitly_wait(10)
        current_state = s
        driver.implicitly_wait(10)

def extract_data(url, database, save, pg, state=None):
    """
    Scenario 1 - run(url, database, page) - https://teduh.kpkt.gov.my/project-swasta?search_type=pemaju&page=1
    Scenario 2 - run(url, database, page) no tp - https://teduh.kpkt.gov.my/project-swasta?search_type=pemaju&page=1
    Scenario 3 - run(url, database, page, state) - https://teduh.kpkt.gov.my/project-swasta?search_type=pemaju&page=1&state=01
    Scenario 4 - run(url, database, page, state) no tp - https://teduh.kpkt.gov.my/project-swasta?search_type=pemaju&page=1&state=01
    """
    print(f"Current: {url}")
    print(f"Current page: {pg}")

    isTitle = False

    # Check if the state_code input is list or not
    if state:
        isList = isinstance(state, list)
        if not isList:
            state = [state]

        for i, s in enumerate(state):
            # Format of url: https://teduh.kpkt.gov.my/project-swasta?search_type=pemaju&page=1&state=01
            if i == 0:
                current_state = None
                url = url.replace("state=01", f"state={s}")
            else:
                url = url.replace(f"state={current_state}", f"state={s}")

            driver = connect(url)        
            # url = url.replace(f"state=01")
            # driver.delete_all_cookies()
            try:
                total_pages = extract_pages(driver) + 1
            except Exception as e:
                print(f"Error code: {e}")
                print(f"Main reason: 'a.page-link' not found")
                total_pages = 0
            print("here221")
            # print(f"{pg}, {page}")

            simp_extract_data(driver, database, save, total_pages, s)
    else:
        simp_extract_data(driver, database, save, total_pages)

def extract_list(url, save, database, lists):
    # lists is the code in Code.xlsx
    print(lists)
    isTitle = False

    curr_i = save.load_index()
    print(f"The first/current index: {curr_i}")
    for i in range(curr_i, len(lists)):
        if i % 100 == 0 and i != 0:
            print("Checkpoint reached, saving progress and clearing out dict content...")
            dicts = database.get_project_data()
            save.save(dicts)
            database.empty_data()
            print("Done.")
        # Format of url: https://teduh.kpkt.gov.my/project-swasta
        save.save_index(i)
        if i == curr_i:
            current_code = None
            url = f'{url}/{lists[i]}'
            print(f"URL: {url}")
        else:
            url = url.replace(current_code, lists[i])
            print(f"URL: {url}")

        driver = connect(url)        

        URL = url

        soup = BeautifulSoup(driver.page_source, 'lxml')

        if not isTitle:
            print("Storing title...")
            print(f"URL is {url}")
            extract_information_title(soup, database)
            isTitle = True
        website_location = i, lists[i]
        extract_information(soup, database, str(driver.current_url), website_location)
        print("Information extraction complete. Proceed to the next link...")
        print(f"Progress: {i} of {len(lists)}")
        current_code = lists[i]
    save.save_index(0)
        # driver.implicitly_wait(10)

def extract_pages(driver):
    '''
    This function get the number of pages in the website
    
    Output: the amount of pages in the website
    '''
    pages = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.page-link")))
    # print(pages)
    print(f'\nPages to be scraped: {pages[-2].text}\n')
    pages_number = int(pages[-2].text)
    return pages_number

def extract_buttons(driver):
    '''
    As the websites contains a number of lists where its detail can be viewed by click on the button, 
    so the location of the buttons is find and store in a lists

    Output: a lists of buttons that present in the PARTICULAR page and directs to details page .
    '''
    button_code = "a.btn.btn-primary"
    try:
        button = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, button_code)))
        print("All the link gathered. Iterating each link...") 
        # print(button)
        return button
    except Exception as e:
        print(f"Error code: {e}")
        print(f"Main reason: '{button_code}' not found")
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
        print("Possible reason: p.font-medium text-sm or p.text-center font-semibold text-white")
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
        print("Possible reason: p.font-medium text-xs md:text-sm or p.font-medium text-sm")

    # Pembangunan Projek
    try:
        all_pembangunan_projek_info = soup.find("tbody", class_="bg-teduh-mid bg-opacity-25").find_all("tr")
        # print(f"all pembangunan projek is {all_pembangunan_projek_info}")
        if all_pembangunan_projek_info is None:
            pass
        else:
            for project_row in all_pembangunan_projek_info:
                pembangunan_projek_detail = project_row.find_all("td", class_="text-center")

                temp = []
                for element in pembangunan_projek_detail:
                    temp.append(" ".join((element.text.replace("\n", "").strip()).split()))
                pembangunan_projek_info_list.append(temp.copy())
        # print(f"check {pembangunan_projek_info_list}")
        # Location
        iframe_tag = soup.find_all('iframe')

        if iframe_tag:
            iframe_tag = iframe_tag[-1]
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
        print("Possible reason: tbody.bg-teduh-mid bg-opacity-25 or td.text-center or iframe")


    data = (maklumat_pemaju_info_list, ringkasan_projek_info_list, pembangunan_projek_info_list, location_list)

    print("All the info gathered. Updating database...")

    db.add_project(project_title, proj_url, data, website_location)

def connect(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.delete_all_cookies()
    # lists = EC.presence_of_element_located((By.XPATH, '//h3[@class="listing-name"]'))
    return driver

def run(url, database, save, **kwargs):
    url = url
    db = database
    page = kwargs['page'] if kwargs.get('page') is not None else None
    state = kwargs['state'] if kwargs.get('state') is not None else None
    state_column = kwargs['state_column'] if kwargs.get('state_column') is not None else None
    code_file = kwargs['code_file'] if kwargs.get('code_file') is not None else None

    print(page, state, code_file)

    if page is None and state is None and code_file is not None:
        # Scenario 5 - run(url, database, code_file)
        list_of_code, names = get_list(state_column, code_file)
        NAMES = names
        if list_of_code:
            if not isinstance(names, list):
                names = [names]
                list_of_code = [list_of_code]
            curr_state = save.load_state()
            for index in range(curr_state, len(list_of_code)):
                save.store_info(names[index])
                save.save_state(index)
                extract_list(url, save, db, list_of_code[index])
                dicts = database.get_project_data()
                print(dicts)
                # with open('my_dict.json', 'w') as file:
                #     json.dump(dicts, file)
                save.save(dicts)  
                database.empty_data()
    else:
        # Scenario 1-4
        extract_data(url, db, save, page, state)
        save.save(dicts)
        database.empty_data()

def get_state(state):
    if state == '0':
        return ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '14', '16']
    else:
        return state

def opt():
    state_code = "01 - Johor\n02 - Kedah\n03 - Kelantan\n04 - Melaka\n05 - Negeri Sembilan\n06 - Pahang\n07 - Pulau Pinang\n08 - Perak\n09 - Perlis\n10 - Selangor\n11 - Terengganu\n14 - Wilayah KL\n16 - Wilayah Putrajaya\n"

    parser = argparse.ArgumentParser()
    # Alternative: https://teduh.kpkt.gov.my/project-swasta
    parser.add_argument("-u", "--url", type=str, default="https://teduh.kpkt.gov.my/project-swasta?search_type=pemaju&page=1&state=01")
    parser.add_argument("-p", "--page", type=int, default=1)
    parser.add_argument("-s", "--state", type=str, default=0, help=state_code)
    parser.add_argument("-c", "--code_file", type=str, default="Code.xlsx")
    parser.add_argument("-sc", "--state_column", type=int, default=0, help="state to run a state per runtime; 0 to run all")
    parser.add_argument("-t", "--scenario", type=int, default=0)

    return parser.parse_args()

def get_list(state, file):
    df = pd.read_excel(file)
    if state == 0:
        names = df.columns
        df_lists = []

        names = [name for name in names if name != "Code"]

        for name in names:
            df_temp = df[name].copy()
            lists = df_temp.dropna().tolist()
            df_lists.append(lists)

        # df_lists = df_lists[0]
    else:
        names = state
        df_temp = df.iloc[:, names].copy()
        df_lists = df_temp.dropna().tolist()
    # df_code = df['Johor']
    # lists = df_code.dropna().tolist()
    return df_lists, names

@profile
def main(args):
    """
    Input: args 

    Based on given scenario, the script will perform different ways to scrap the website.

    # SCENARIO = 0 -> Auto detection
    SCENARIO = 1 -> 'Semua Negeri' and total pages available
    SCENARIO = 2 -> 'Semua Negeri' available, but not total pages
    SCENARIO = 3 -> total pages available, but not 'Semua Negeri'
    SCENARIO = 4 -> 'Semua Negeri' and total pages not available
    SCENARIO = 5 -> key-value pairs not available

    Normal flow:
    1. Call run() function
    2. In run() function, call corressponding extract_() function
    3. In extract_() function, perform corressponding way of scraping based on given scenario. 
    4. Either way, the project titles will be called, and only after that, the Database is initialized.
    5. Extract data and store in database
    6. Upon finish, save it in a excel file
    7. Finish or continue looping
    """

    url = args.url
    page = args.page
    state = args.state
    code_file = args.code_file
    state_column = args.state_column
    scenario = args.scenario

    database = Database()
    save = Save()

    timer = 10
    count = 100
    while count > 0:
        print("here we go again")
        if scenario == 0:
            pass
        elif scenario == 1 or scenario == 2:
            if not '?' in url:
                print("\nThe provided URL does not contain key-value pairs, please choose different scenario or provide proper URL")
                exit 
            try:
                # run(args.url, database, save_count, state, args.page, list_of_code)
                run(url, database, save, page=page)
                exit()
            except Exception as e: 
                print(f"Some error occured: {e}")  
                print(f"Wait for {timer} second")
                time.sleep(timer)
                count -= 1
        elif scenario == 3 or scenario == 4:
            if not '?' in url:
                print("\nThe provided URL does not contain key-value pairs, please choose different scenario or provide proper URL")
                break 
            try:
                # run(args.url, database, save_count, state, args.page, list_of_code)
                run(url, database, save, page=page, state=state)

                break
            except Exception as e:
                print(f"Some error occured: {e}") 
                print(f"Wait for {timer} second")
                time.sleep(timer)
                count -= 1
        elif scenario == 5:
            if '?' in url:
                print("\nThe provided URL contains key-value pairs, please choose different scenario or provide proper URL")
                exit()
            try:
                run(url, database, save, state_column=state_column, code_file=code_file)
                print("All done")
                print("Before break")
                # merge(NAMES)
                exit()
            except Exception as e: 
                print(f"Some error occured: {e}") 
                print(f"Wait for {timer} second")
                time.sleep(timer)
                count -= 1
        else:
            count -= 1

    print("Last save...")
    dicts = database.get_project_data()
    save.save(dicts)



    return

if __name__ == "__main__":
    args = opt()
    print(args)
    # print("s")
    main(args)