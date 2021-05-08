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
    'ng',
    'age_range',
    'BASE',
    'PIU\'',
    'ORO',
    'AMBULATORIALE',
    'AMBULATORIALEPLUS',
    'RICOVERI',
    'RICOVERIPLUS',
    'ODONTOIATRICA',
    'IGIC-GRANDIINTERVENTICHIRURGICI',
    'PROTEGGOPLUS'
]

#field name and id
fieldids = {
    'BASE':'formulecomplete_1',
    'PIU\'':'formulecomplete_2',
    'PIU\' SMART FAMILY':'formulecomplete_4',
    'ORO':'formulecomplete_3',
    'AMBULATORIALE':'formuleparziali_5',
    'AMBULATORIALEPLUS':'formuleparziali_6',
    'RICOVERI':'formuleparziali_7',
    'RICOVERIPLUS':'formuleparziali_13',
    'ODONTOIATRICA':'formuleaggiuntive_9',
    'IGIC-GRANDIINTERVENTICHIRURGICI':'formuleaggiuntive_8',
    'PROTEGGOPLUS':'formuleaggiuntive_14'
}


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
    #input the name(filed2)
    nameinput = driver.find_element_by_id('titolarenome')
    nameinput.clear()
    nameinput.send_keys(query[2])
    time_sleep(2)

    #input the year(field3)
    yearinput = driver.find_element_by_id('titolareanno')
    yearinput.clear()
    yearinput.send_keys(query[3])
    time_sleep(2)

    #input the base
    keylist = fieldids.keys()

    #validkeylist from input data
    validkeylist = []
    for key in keylist:
        if key in query:
            validkeylist.append(key)
            keyinput = driver.find_element_by_id(fieldids[key])
            driver.execute_script("arguments[0].click();", keyinput)
            #keyinput.click()
            time_sleep(3)

    #get the field16 of the query.
    length = len(query)
    if length == 17:
        field16 = query[16]
        monthselect = driver.find_element_by_id('meseriferimento')
        monthselect.send_keys(field16)
        time_sleep(3)
    
    #click the calculate button.
    calbutton = driver.find_element_by_id('btnNext')
    driver.execute_script("arguments[0].click();", calbutton)
    time_sleep(3)

    try:
        tableitem = driver.find_element_by_class_name('tabRisCoperture')
    except:
        #click the return button
        backbutton = driver.find_element_by_class_name('preventiviButton')
        driver.execute_script("arguments[0].click();", backbutton)
        time_sleep(3)
        return False

    #output data
    for index in range(2):
        output = {
            'No':'',
            'scrapedate':'',
            'company':'',
            'ng':'',
            'age_range':'',
            'BASE':'',
            'PIU\'':'',
            'ORO':'',
            'AMBULATORIALE':'',
            'AMBULATORIALEPLUS':'',
            'RICOVERI':'',
            'RICOVERIPLUS':'',
            'ODONTOIATRICA':'',
            'IGIC-GRANDIINTERVENTICHIRURGICI':'',
            'PROTEGGOPLUS':''
        }

        output['scrapedate'] = str_date
        output['company'] = query[0]
        output['age_range'] = query[1]
        xpath = ''
        if index == 0:
            output['ng'] = 'N'
            xpath = ('.//tbody//tr[3]//td')
        elif index == 1:
            output['ng'] = 'G'
            xpath = ('.//tbody//tr[6]//td')
        else:
            continue

        valueitems = tableitem.find_elements_by_xpath(xpath)
        tdindex = 0
        for valueitem in valueitems:
            if tdindex > 1:
                output[validkeylist[tdindex-2]] = valueitem.text.replace('€', '').strip()
            tdindex += 1

        print(output)
        writer.writerow(output)

    #click the return button
    backbutton = driver.find_element_by_class_name('preventiviButton')
    driver.execute_script("arguments[0].click();", backbutton)
    time_sleep(3)

    return []

if __name__ == '__main__':
    config_option = load_config()

    lst_query = get_query(config_option['input_path'])

    out_file = config_option['output_path']
    csvfile = open(out_file, 'w')
    writer = csv.DictWriter(csvfile, delimiter=";", fieldnames=output_header)
    writer.writeheader()

    driver = get_seleniumdriver('https://www.campa.it/preventivo')

    results = []

    itemindex = 1
    for one_query in lst_query:
        print("---------{}----------".format(itemindex))
        print(one_query)
        time_sleep(5)

        one_result = get_data(driver, one_query, writer)
        if one_result == False:
            itemindex = itemindex + 1
            continue

        results.extend(one_result)
        itemindex = itemindex + 1


    driver.close()
    csvfile.close()



    print("\n~ ~ ~ F i n i s h e d ~ ~ ~ ")
