from CloudflareBypasser import CloudflareBypasser
from DrissionPage import ChromiumPage, ChromiumOptions
import csv
import time
import random

def extract_keywordsList_from_csv(file_path):
    keywordsList = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in csvreader:
            for cell in row:
                cleaned_cell = cell.strip()
                if cleaned_cell:
                    keywordsList.append(cleaned_cell)
    return keywordsList

def extract_card_info(driver):
    cards_info = []
    cards = driver.eles('.df-card')
    
    for card in cards:
        try:
            href = card.ele('css:a.df-card__main').attr('href') if card.ele('css:a.df-card__main') else 'N/A'
            title = card.ele('css:div.df-card__title').text.strip() if card.ele('css:div.df-card__title') else 'N/A'
            brand_alt = card.ele('css:div.df-card__brand img').attr('alt') if card.ele('css:div.df-card__brand img') else 'N/A'
            code = 'N/A'
            price = 'N/A'
            old_price = 'N/A'

            code_element = card.ele('css:div.df-card__title.altColor')
            if code_element:
                code_text = code_element.text.strip()
                if ':' in code_text:
                    code = code_text.split(':')[1].strip()

            new_price_element = card.ele('css:span.df-card__price--new')
            if new_price_element:
                price = new_price_element.text.strip()

            old_price_element = card.ele('css:span.df-card__price--old')
            if old_price_element:
                old_price = old_price_element.text.strip()

            if price == 'N/A':
                regular_price_element = card.ele('css:span.df-card__price')
                if regular_price_element:
                    price = regular_price_element.text.strip()

            card_info = {
                'Desc': title,
                'URL': href,
                'Brand_name': brand_alt,
                'Code': code,
                'Price_current': price,
                'Old_price': old_price
            }
            cards_info.append(card_info)
        except Exception as e:
            print(f"Error extracting card info: {str(e)}")
    
    return cards_info

def append_to_csv(data, file_path, write_header=False):
    mode = 'w' if write_header else 'a'
    with open(file_path, mode, newline='', encoding='utf-8') as csvfile:
        fieldnames = ['SearchPart', 'Desc', 'URL', 'Brand_name', 'Code', 'Price_current', 'Old_price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if write_header:
            writer.writeheader()
        for row in data:
            writer.writerow(row)

if __name__ == '__main__':
    file_path = 'porsche_oe.csv'
    keywords_array = extract_keywordsList_from_csv(file_path)
    print("Successfully created an array containing the numbers")

    browser_path = "/usr/bin/google-chrome"
    options = ChromiumOptions()
    options.set_paths(browser_path=browser_path)

    arguments = [
        "-no-first-run", "-force-color-profile=srgb", "-metrics-recording-only",
        "-password-store=basic", "-use-mock-keychain", "-export-tagged-pdf",
        "-no-default-browser-check", "-disable-background-mode",
        "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
        "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
        "-deny-permission-prompts", "-disable-gpu", "-accept-lang=en-US",
    ]

    for argument in arguments:
        options.set_argument(argument)

    driver = ChromiumPage(addr_or_opts=options)
    driver.get('https://www.design911.com/masthead/setchosenvehicle/6/94528/-1')
    cf_bypasser = CloudflareBypasser(driver)
    cf_bypasser.bypass()

    print("Enjoy the content!")
    print("Title of the page: ", driver.title)
    time.sleep(5)

    try:
        button = driver.ele('#CybotCookiebotDialogBodyButtonDecline', timeout=10)
        if button:
            button.click()
            print("Button clicked successfully!")
            time.sleep(random.uniform(1, 2))
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    try:
        a_tag = driver.ele('xpath://a[@class="diagrams" and @href="/diagrams/"]', timeout=10)
        if a_tag:
            a_tag.click()
            print("Link clicked successfully!")
            time.sleep(2)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    output_file = 'output.csv'
    first_write = True

    for keyword in keywords_array:
        try:
            search_input = driver.ele('xpath://div[@id="searchbox"]/input', timeout=10)
            if search_input:
                search_input.clear()
                search_input.input(keyword)
                print(f"Text '{keyword}' entered successfully!")
                time.sleep(2)
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        cards_info = extract_card_info(driver)
        
        for card in cards_info:
            card['SearchPart'] = keyword
        
        append_to_csv(cards_info, output_file, write_header=first_write)
        first_write = False

        print(f"Total cards extracted for '{keyword}': {len(cards_info)}")
        print(f"Data appended to {output_file}")

    input("Press Enter to close the browser...")
    driver.quit()
