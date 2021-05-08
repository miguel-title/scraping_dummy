import selenium
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup

from selenium.common.exceptions import TimeoutException
import datetime

import csv
import sys
import os
import random
import time

if sys.version_info >= (3, 0):
    import configparser as ConfigParser
else:
    import ConfigParser

output_header = [
    'No',
    'scrapedate',
    'company',
    'age_range',
    'name',
    'monthly_price',
    'service',
    'massimale'
]


str_date = datetime.datetime.now().strftime('%Y-%m-%d')

def load_config():
    defaults = {
        'input_path': '',
        'output_path': '',
        'suffix_excelfile_name': ''
    }
    _settings_dir = "."
    config_file = os.path.join(_settings_dir, "config.ini")
    if os.path.exists(config_file):
        try:
            # config = ConfigParser.SafeConfigParser()
            config = ConfigParser.ConfigParser()
            config.read(config_file)
            if config.has_section("global"):
                config_items = dict(config.items("global"))
                defaults['input_path'] = config_items['input_path']
                defaults['output_path'] = config_items['output_path']
                defaults['suffix_excelfile_name'] = config_items['suffix_excelfile_name']
                defaults['output_path'] = '{}/{}_{}.csv'.format(defaults['output_path'], str_date, defaults['suffix_excelfile_name'])



        except ConfigParser.Error as e:
            print("\nError parsing config file: " + config_file)
            print(str(e))
            exit(1)

    return defaults


def get_seleniumdriver(url, count=0):
    options = Options()
    if os.name == "nt":
        #options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        #options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
    else:
        #options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        #options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options, executable_path='./chromedriver')
    driver.get(url)
    driver.implicitly_wait(10)
    time_sleep(1)

    return driver


def time_sleep(type):
    if type == 1:
        sleeptime = random.randrange(10,100)/100
    elif type == 2:
        sleeptime = random.randrange(70, 200)/100
    elif type == 3:
        sleeptime = random.randrange(100, 300)/100
    elif type == 4:
        sleeptime = random.randrange(150, 400)/100
    elif type == 5:
        sleeptime = random.randrange(400, 500)/100
    elif type == 401:
        sleeptime = random.randrange(60, 100)
    time.sleep(sleeptime)

def get_query(input_path):
    lst_query = []

    with open(input_path) as csv_file:
        records = csv.reader(csv_file, delimiter=';')
        for row in records:
            if row == []:
                continue
            rowtmp = []
            for data in row:
                rowtmp.append(data.replace(' ', ''))

            if rowtmp == []:
                continue
            lst_query.append(rowtmp)

    return lst_query

def get_data(driver, query, writer):
    #Il contraente è una persona fisica o una persona giuridica?
    if query[2].replace(' ', '').upper() == 'PERSONAFISICA':
        personachild_elem = driver.find_element_by_xpath("//span[text()='Persona fisica']")
    else:
        personachild_elem = driver.find_element_by_xpath("//span[text()='Persona giuridica']")
    
    personaitem = personachild_elem.find_element_by_xpath('..//a')

    driver.execute_script("arguments[0].click();", personaitem)
    time_sleep(3)

    #Sesso dell’Assicurato
    if query[3].replace(' ', '').upper() == 'M':
        #sessoitem = driver.find_element_by_xpath("//a[text()='M']")
        sessoitem = WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.XPATH, "//a[text()='M']")))
    else:
        #sessoitem = driver.find_element_by_xpath("//a[text()='F']")
        sessoitem = WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.XPATH, "//a[text()='F']")))
    time_sleep(3)
    driver.execute_script("arguments[0].click();", sessoitem)
    time_sleep(3)

    #Data di nascita dell’Assicurato
    dateinput = WebDriverWait(driver, 30).until(ec.visibility_of_element_located((By.ID, "date")))
    dateinput.clear()
    dateinput.send_keys(query[4])
    time_sleep(3)
    dateinput.send_keys(Keys.ENTER)
    time_sleep(3)

    #La provincia di residenza dell’Assicurato
    cityinput = WebDriverWait(driver, 30).until(ec.visibility_of_element_located((By.ID, "answer-R9_1")))
    cityinput.clear()
    cityinput.send_keys(query[5])
    time_sleep(3)
    cityinput.send_keys(Keys.ENTER)
    time_sleep(4)

    #Reddito lordo annuo del Contraente
    priceinput = WebDriverWait(driver, 30).until(ec.visibility_of_element_located((By.ID, "lordo")))
    priceinput.send_keys(query[6])
    time_sleep(3)
    priceinput.send_keys(Keys.ENTER)
    time_sleep(3)

    #Quale tipologia di copertura Salute ti interessa tra le seguenti?
    _ID = ''
    if query[7].upper() == 'INDENNITARIA':
        _ID = 'R18_1'
    elif query[7].upper() == 'RSMCOMPLETA':
        _ID = 'R18_2'
    elif query[7].upper() == 'RSMMODULARE':
        _ID = 'R18_3'
    elif query[7].upper() == 'RSMODONTOIATRICA':
        _ID = 'R18_4'
    elif query[7].upper() == 'RICOVERI':
        _ID = 'R18_5'
    elif query[7].upper() == 'COPERTURABENESSERE':
        _ID = 'R18_6'

    try:
        qualeselect = WebDriverWait(driver, 30).until(ec.visibility_of_element_located((By.ID, _ID)))
        qualeselect.click()
        time_sleep(3)
    except:
        return False

    #Sei già beneficiario di una copertura Salute per la tipologia prescelta?
    if query[3].replace(' ', '').upper() == 'Si':
        #seiitem = driver.find_element_by_xpath("//a[text()='Si']")
        seiitem = WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.XPATH, "//a[text()='Si']")))
    else:
        #seiitem = driver.find_element_by_xpath("//a[text()='No']")
        seiitem = WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.XPATH, "//a[text()='No']")))
    

    driver.execute_script("arguments[0].click();", seiitem)
    time_sleep(5)


    try:
        faibuttons = driver.find_elements_by_xpath("//div[@class='container']//div[@class='col-3']//a")
    except:
        return False

    count = len(faibuttons)
    for buttonindex in range(count):
        print('buttonindex:', buttonindex)
        try:
            faibuttons = driver.find_elements_by_xpath("//div[@class='container']//div[@class='col-3']//a")
        except:
            return False
        faibuttons[buttonindex].click()
        time_sleep(5)

        driver.switch_to.window(driver.window_handles[1])
        
        #time.sleep(20)
        time_sleep(5)

        if query[9] == 'ALTA':
            nextbutton = WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.CLASS_NAME, 'configuratore--nextChoice')))
            driver.execute_script("arguments[0].click();", nextbutton)
            #nextbutton.click()
        elif query[9] == 'TOTALE':
            nextbutton = WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.CLASS_NAME, 'configuratore--nextChoice')))
            driver.execute_script("arguments[0].click();", nextbutton)
            time_sleep(2)
            driver.execute_script("arguments[0].click();", nextbutton)
        
        time_sleep(3)

        #okbuttons = driver.find_elements_by_class_name('configuratore--ok')
        try:
            okbuttons = WebDriverWait(driver, 30).until(ec.presence_of_all_elements_located((By.CLASS_NAME, "configuratore--ok")))
        except:
            driver.execute_script("window.close('');")
            driver.switch_to.window(driver.window_handles[0])
            time_sleep(3)
            continue

        if len(okbuttons) < 2:
            return False
        #okbuttons[0].click()
        driver.execute_script("arguments[0].click();", okbuttons[0])

        if query[10] == '1':
            #previousbutton = driver.find_element_by_class_name('configuratore--previousChoice')
            try:
                previousbutton = WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.CLASS_NAME, 'configuratore--previousChoice')))
            except:
                continue            
            driver.execute_script("arguments[0].click();", previousbutton)
            #previousbutton.click()
        elif query[10] == '5':
            #nextbutton = driver.find_element_by_class_name('configuratore--nextChoice')
            try:
                nextbutton = WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.CLASS_NAME, 'configuratore--nextChoice')))
            except:
                continue
            driver.execute_script("arguments[0].click();", nextbutton)
            #nextbutton.click()

        time_sleep(5)

        driver.execute_script("arguments[0].click();", okbuttons[1])
        #okbuttons[1].click()

        time_sleep(5)

        btnclasslist = ['infoModal--lowLabel', 'infoModal--midLabel', 'infoModal--highLabel']
            
        #output data
        for index in range(3):
            output = {
                'No':'',
                'scrapedate':'',
                'company':'',
                'age_range':'',
                'name':'',
                'monthly_price':'',
                'service':'',
                'massimale':''
            }

            output['scrapedate'] = str_date
            output['company'] = query[0]
            output['age_range'] = query[1]
            if index == 0:
                output['name'] = 'Salute Sorriso Plus Base'
            elif index == 1:
                output['name'] = 'Salute Sorriso Plus Alta'
            elif index == 2:
                output['name'] = 'Salute Sorriso Plus Totale'

            btnclass = btnclasslist[index]

            print('index:', index)
            print('btnclass:', btnclass)
            
            classbutton = driver.find_elements_by_class_name(btnclass)[-1]
            driver.execute_script("arguments[0].click();", classbutton)
            #classbutton.click()

            time_sleep(3)
            output['monthly_price'] = driver.find_elements_by_id('infoModal--prezzoMeseVal')[-1].text


            #serviceitems = WebDriverWait(driver, 10).until(ec.presence_of_all_elements_located((By.CLASS_NAME, "infoModal--boldTitle")))
            servicetritems = WebDriverWait(driver, 30).until(ec.presence_of_all_elements_located((By.XPATH, "//table//tr")))            
            serviceitems = WebDriverWait(driver, 30).until(ec.presence_of_all_elements_located((By.XPATH, "//table//tr//td[2]")))            

            for serviceitem in serviceitems:
                parentitem = serviceitem.find_element_by_xpath('..')
                if serviceitem.get_attribute('class') != 'infoModal--boldTitle':
                    continue
                currentindex = servicetritems.index(parentitem)

                output['service'] = serviceitem.text
                try:            
                    price = servicetritems[currentindex + 1].find_element_by_xpath(".//td[3]").text
                    titleprice = servicetritems[currentindex + 1].find_element_by_xpath(".//td[2]").text
                    if '€' in price and 'Massimale' in titleprice:
                        output['massimale'] = price
                except:
                    print(output)
                    writer.writerow(output)
                    continue

                print(output)
                writer.writerow(output)

        driver.execute_script("window.close('');")

        driver.switch_to.window(driver.window_handles[0])
        time_sleep(3)

    return []

if __name__ == '__main__':
    config_option = load_config()

    lst_query = get_query(config_option['input_path'])

    out_file = config_option['output_path']
    csvfile = open(out_file, 'w')
    writer = csv.DictWriter(csvfile, delimiter=";", fieldnames=output_header)
    writer.writeheader()

    results = []

    itemindex = 1
    for one_query in lst_query:
        driver = get_seleniumdriver('https://webab.rbmsalute.it/rbm-stijl/#/questionnaire')
        time_sleep(5)

        print("---------{}----------".format(itemindex))
        print(one_query)
        time_sleep(5)

        one_result = get_data(driver, one_query, writer)
        if one_result == False:
            itemindex = itemindex + 1
            driver.quit()
            continue
        driver.quit()
        results.extend(one_result)
        itemindex = itemindex + 1


    driver.close()
    csvfile.close()



    print("\n~ ~ ~ F i n i s h e d ~ ~ ~ ")
