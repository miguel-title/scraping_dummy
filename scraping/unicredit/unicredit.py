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

import urllib.request

from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import getopt
import io

import unicodedata

if sys.version_info >= (3, 0):
    import configparser as ConfigParser
else:
    import ConfigParser

from diff_pdf_visually import pdfdiff
import filecmp

output_header = [
    'header1',
    'header2'
]

str_date = datetime.datetime.now().strftime('%Y%m%d')

def load_config():
    defaults = {
        'output_path': '',
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
                defaults['output_default_path'] = config_items['output_path']
                defaults['output_path'] = '{}/{}-UNICREDIT-PRIVATI-***.txt'.format(defaults['output_default_path'], str_date)
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


def get_data(driver, output_file, latest_file_list, output_default_path, latest_download_file_list):
    #Get Link URL
    cookiebutton = driver.find_element_by_xpath("//a[@id='cookieAccepted']")
    driver.execute_script("arguments[0].click();", cookiebutton)

    time_sleep(3)

    parentitems = driver.find_elements_by_xpath("//div[@class='pws_box_list']//ul[@class='list-unstyled']//li")

    parentlinkurls = {}
    for parentitem in parentitems:
        linkUrl = parentitem.find_element_by_tag_name("a").get_attribute("href")
        linkText = parentitem.text
        print(linkText, ':', linkUrl)

        parentlinkurls[linkText] = linkUrl

    driver.close()

    for key in parentlinkurls:
        print('------secondary--------')
        time_sleep(3)
        url = parentlinkurls[key]
        driver = get_seleniumdriver(url)
        time_sleep(5)

        cookiebutton = driver.find_element_by_xpath("//a[@id='cookieAccepted']")
        driver.execute_script("arguments[0].click();", cookiebutton)
        
        try:
            secondaryitems = driver.find_elements_by_xpath("//div[@class='pws_box_list']//ul[@class='list-unstyled']//li")
        except:
            driver.close()
            continue
        print('------count:{}'.format(len(secondaryitems)))
        if len(secondaryitems) <= 1:
            driver.close()
            continue
        
        secondarylinkurls = {}
        for secondaryitem in secondaryitems:
            linkUrl = secondaryitem.find_element_by_tag_name("a").get_attribute("href")
            linkText = secondaryitem.text
            #print(linkText, ':', linkUrl)

            secondarylinkurls[linkText] = linkUrl
            
        parentlinkurls[key] = secondarylinkurls

        driver.close()

    
    #àprint(parentlinkurls)

    #Get Data

    tmpoutputfile = output_file
    isFileExist = os.path.isfile(latest_file_list)
    lstFileContent = []
    if isFileExist:
        f = open(latest_file_list, "r")
        for content in f:
          lstFileContent.append(content.split(",")[0])

        f.close()


    isdir6 = os.path.isdir('{}/'.format(output_default_path))
    if not isdir6:
        os.mkdir('{}/'.format(output_default_path)) 
    isdir4 = os.path.isdir('{}/DIFF/'.format(output_default_path))
    if not isdir4:
        os.mkdir('{}/DIFF/'.format(output_default_path)) 
    isdir5 = os.path.isdir('{}/DIFF/DETAIL/'.format(output_default_path))
    if not isdir5:
        os.mkdir('{}/DIFF/DETAIL/'.format(output_default_path))
    isdir7 = os.path.isdir('{}/TEXT_OUT'.format(output_default_path))
    if not isdir7:
        os.mkdir('{}/TEXT_OUT'.format(output_default_path))

    isDownloadFileExist = os.path.isfile(latest_download_file_list)
    lstdownloadfilecontent = []
    if isDownloadFileExist:
        f = open(latest_download_file_list, "r")
        for content in f:
            lstdownloadfilecontent.append(content.split(",")[0])

        f.close()

    latest_file = open(latest_file_list, 'w')
    latest_file_list_writer = csv.DictWriter(latest_file, delimiter=",", fieldnames=['filename'])

    latest_download_file = open(latest_download_file_list, 'w')
    latest_download_file_writer = csv.DictWriter(latest_download_file, delimiter=",", fieldnames=['filename'])

    dicFileContents = {}
    for filename in lstFileContent:
        File_Content = []
        if not os.path.exists(filename):
            continue

        latestfile = open(filename.replace('\n', ''), 'r')
        for content in latestfile:
          print("content:{}".format(content))
          File_Content.append(content.split(",")[1].replace("\n", ""))
        latestfile.close()
        time_sleep(1)

        dicFileContents[filename] = File_Content

    difffile = open('{}/DIFF/{}-diff.csv'.format(output_default_path, str_date), 'w')
    print("difffile:{}".format('{}/DIFF/{}-diff.csv'.format(output_default_path, str_date)))
    diffwriter = csv.DictWriter(difffile, delimiter=",", fieldnames=['COMPANY', 'DATE', 'SEGMENT', 'MAIN PRODUCT', 'PRODUCT', 'CODE'])
    diffwriter.writeheader()

    for key1 in parentlinkurls:
        output = {'header1':'', 'header2':''}
        output_filename = {'filename':''}


        difffile_field = {'COMPANY':'', 'DATE':'', 'SEGMENT':'', 'MAIN PRODUCT':'', 'PRODUCT':'', 'CODE':''}

        if isinstance(parentlinkurls[key1],dict):
            for key2 in parentlinkurls[key1]:
                subfilename = key1 + '_' + key2

                output_file = tmpoutputfile.replace("***", subfilename)

                csvfile = open(output_file, 'w')
                print("output_file:{}".format(output_file))
                writer = csv.DictWriter(csvfile, delimiter=",", fieldnames=output_header)
                output_downloadfilename = {'filename':''}

                driver = get_seleniumdriver(parentlinkurls[key1][key2])

                items = driver.find_elements_by_xpath("//div[@class='pdf_component']//ul[@class='list-unstyled']//li")
                print('items count:', len(items))
                for item in items:
                    isdir1 = os.path.isdir('{}/UNICREDIT/'.format(output_default_path))
                    if not isdir1:
                        os.mkdir('{}/UNICREDIT'.format(output_default_path)) 
                    isdir2 = os.path.isdir('{}/UNICREDIT/PRIVATI/'.format(output_default_path))
                    if not isdir2:
                        os.mkdir('{}/UNICREDIT/PRIVATI/'.format(output_default_path))
                    isdir3 = os.path.isdir('{}/UNICREDIT/PRIVATI/{}/'.format(output_default_path, subfilename))
                    if not isdir3:
                        os.mkdir('{}/UNICREDIT/PRIVATI/{}/'.format(output_default_path, subfilename)) 
                    
                    pdfdocfilename = "{}/UNICREDIT/PRIVATI/{}/{}-UNICREDIT-PRIVATI-{}.pdf".format(output_default_path, subfilename, str_date, unicodedata.normalize('NFKD', item.text).encode('ascii', 'ignore').decode('ascii'))
                
                    pdflinktext = item.find_element_by_tag_name("a").get_attribute('href')
                    try:

                        print("{} downloading...".format(pdflinktext))
                        req = urllib.request.Request(pdflinktext, headers={'User-Agent': 'Mozilla/5.0'})

                        file = open(pdfdocfilename, 'wb')
                        file.write(urllib.request.urlopen(req).read())
                        file.close()

                    except Exception as e:
                        print("Download Error:{}".format(e))
                        continue
                    output_downloadfilename['filename'] = pdfdocfilename
                    latest_download_file_writer.writerow(output_downloadfilename)

                    #compare file changes
                    difffile_field['COMPANY'] = 'UNICREDIT'
                    difffile_field['DATE'] = str_date
                    difffile_field['SEGMENT'] = 'PRIVATI'
                    difffile_field['MAIN PRODUCT'] = subfilename
                    difffile_field['PRODUCT'] = item.text
                    curpdfname = pdfdocfilename
                    prepdfname = ''

                    output['header1'] = subfilename
                    output['header2'] = unicodedata.normalize('NFKD', item.text).encode('ascii', 'ignore').decode('ascii')

                    for onefilename in lstdownloadfilecontent:

                        print("----output:{}=={}".format(output['header2'], onefilename))
                        if "-" + output['header2'] + ".pdf" in onefilename:
                            prepdfname = onefilename
                            continue

                    
                    print('---------------------outputfile:{}'.format(output_file))
                    print('---------------------output:{}'.format(output))
                    writer.writerow(output)
                    print("====={} and {}".format(prepdfname, curpdfname))

                    difffile_field['CODE'] = 'no-change'
                    if prepdfname != "":
                        convertMultiple(curpdfname.replace('\n', ''), prepdfname.replace('\n', ''), '{}/TEXT_OUT/'.format(output_default_path))


                        f1 = open("{}/TEXT_OUT/1.pdf.txt".format(output_default_path))
                        f2 = open("{}/TEXT_OUT/2.pdf.txt".format(output_default_path))

                        lines = f2.readlines()
                        changedetailfilename = '{}/DIFF/DETAIL/{}-INTESA-PERSONE-{}.txt'.format(output_default_path, str_date, item.text)
                        detailfile = open(changedetailfilename, 'w')
                        for i,line in enumerate(f1):
                            try:
                                if line != lines[i]:
                                    #print("line", i, "is different:")
                                    #print('\t', line)
                                    #print('\t', lines[i])
                                    difffile_field['CODE'] = 'change'

                                    detailfile.write("======================\nline, {}, is different: \n {} \n {}\n======================\n".format(i, line, lines[i]))
                            except:
                                    #print("line", i, "is different:")
                                    #print('\t', line)
                                    difffile_field['CODE'] = 'change'

                                    detailfile.write("======================\nline, {}, is different: \n {} \n No content\n======================\n".format(i, line))

                        detailfile.close()
                        if difffile_field['CODE'] == 'no-change':                
                            os.remove(changedetailfilename)

                    diffwriter.writerow(difffile_field)
                    print('difffile_field:{}'.format(difffile_field))

                driver.close()
                time_sleep(3)
        else:
            subfilename = key1
            output_file = tmpoutputfile.replace("***", subfilename)


            csvfile = open(output_file, 'w')
            print("output_file:{}".format(output_file))
            writer = csv.DictWriter(csvfile, delimiter=",", fieldnames=output_header)
            output_downloadfilename = {'filename':''}

            driver = get_seleniumdriver(parentlinkurls[key1])
            
            items = driver.find_elements_by_xpath("//div[@class='pdf_component']//ul[@class='list-unstyled']//li")
            print('items count:', len(items))
            for item in items:
                isdir1 = os.path.isdir('{}/UNICREDIT/'.format(output_default_path))
                if not isdir1:
                    os.mkdir('{}/UNICREDIT'.format(output_default_path)) 
                isdir2 = os.path.isdir('{}/UNICREDIT/PRIVATI/'.format(output_default_path))
                if not isdir2:
                    os.mkdir('{}/UNICREDIT/PRIVATI/'.format(output_default_path))
                isdir3 = os.path.isdir('{}/UNICREDIT/PRIVATI/{}/'.format(output_default_path, subfilename))
                if not isdir3:
                    os.mkdir('{}/UNICREDIT/PRIVATI/{}/'.format(output_default_path, subfilename)) 
                
                pdfdocfilename = "{}/UNICREDIT/PRIVATI/{}/{}-UNICREDIT-PRIVATI-{}.pdf".format(output_default_path, subfilename, str_date, unicodedata.normalize('NFKD', item.text).encode('ascii', 'ignore').decode('ascii'))
            
                pdflinktext = item.find_element_by_tag_name("a").get_attribute('href')
                
                try:

                    print("{} downloading...".format(pdflinktext))
                    req = urllib.request.Request(pdflinktext, headers={'User-Agent': 'Mozilla/5.0'})

                    file = open(pdfdocfilename, 'wb')
                    file.write(urllib.request.urlopen(req).read())
                    file.close()
                except Exception as e:
                    print("Download Error:{}".format(e))
                    continue
                output_downloadfilename['filename'] = pdfdocfilename
                latest_download_file_writer.writerow(output_downloadfilename)

                #compare file changes
                difffile_field['COMPANY'] = 'UNICREDIT'
                difffile_field['DATE'] = str_date
                difffile_field['SEGMENT'] = 'PRIVATI'
                difffile_field['MAIN PRODUCT'] = subfilename
                difffile_field['PRODUCT'] = item.text
                curpdfname = pdfdocfilename
                prepdfname = ''

                output['header1'] = subfilename
                output['header2'] = unicodedata.normalize('NFKD', item.text).encode('ascii', 'ignore').decode('ascii')

                for onefilename in lstdownloadfilecontent:
                    print("----output:{}=={}".format(output['header2'], onefilename))
                    if "-" + output['header2'] + ".pdf" in onefilename:
                        prepdfname = onefilename
                        continue

                print('---------------------outputfile:{}'.format(output_file))
                print('---------------------output:{}'.format(output))
                writer.writerow(output)
                print("======={} and {}".format(prepdfname, curpdfname))

                difffile_field['CODE'] = 'no-change'
                if prepdfname != "":
                    convertMultiple(curpdfname.replace('\n', ''), prepdfname.replace('\n', ''), '{}/TEXT_OUT/'.format(output_default_path))


                    f1 = open("{}/TEXT_OUT/1.pdf.txt".format(output_default_path))
                    f2 = open("{}/TEXT_OUT/2.pdf.txt".format(output_default_path))

                    lines = f2.readlines()
                    changedetailfilename = '{}/DIFF/DETAIL/{}-UNICREDIT-PRIVATI-{}.txt'.format(output_default_path, str_date, output['header2'])
                    detailfile = open(changedetailfilename, 'w')
                    for i,line in enumerate(f1):
                        try:
                            if line != lines[i]:
                                #print("line", i, "is different:")
                                #print('\t', line)
                                #print('\t', lines[i])
                                difffile_field['CODE'] = 'change'

                                detailfile.write("======================\nline, {}, is different: \n {} \n {}\n======================\n".format(i, line, lines[i]))
                        except:
                                #print("line", i, "is different:")
                                #print('\t', line)
                                difffile_field['CODE'] = 'change'

                                detailfile.write("======================\nline, {}, is different: \n {} \n No content\n======================\n".format(i, line))

                    detailfile.close()
                    if difffile_field['CODE'] == 'no-change':                
                        os.remove(changedetailfilename)

                diffwriter.writerow(difffile_field)
                print('difffile_field:{}'.format(difffile_field))    

            driver.close()
            time_sleep(3)

        
        csvfile.close()
        time_sleep(2)

        output_filename['filename'] = output_file
        latest_file_list_writer.writerow(output_filename)

    latest_file.close()
    latest_download_file.close()
    difffile.close()


def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = io.StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text 

#converts all pdfs in directory pdfDir, saves all resulting txt files to txtdir
def convertMultiple(curpdfname, prepdfname, txtDir):
    try:
        text1 = convert(curpdfname) #get string of text content of pdf
        textFilename1 = txtDir + "1.pdf.txt"
        textFile1 = open(textFilename1, "w") #make text file
        textFile1.write(text1) #write text to text file

        text2 = convert(prepdfname) #get string of text content of pdf
        textFilename2 = txtDir + "2.pdf.txt"
        textFile2 = open(textFilename2, "w") #make text file
        textFile2.write(text2) #write text to text file
    except:
        print("Convert Error")
        print("curpdfname:{}".format(curpdfname))
        print("prepdfname:{}".format(prepdfname))
    
if __name__ == '__main__':
    config_option = load_config()

    out_file = config_option['output_path']
    out_default_path = config_option['output_default_path']

    driver = get_seleniumdriver('https://www.unicredit.it/it/info/trasparenzabancaria/trasparenza/privati.html')
    time_sleep(5)

    latest_file_list = os.path.join(out_default_path, "latest_file_list")
    latest_download_file_list = os.path.join(out_default_path, "latest_downloadfile_list")

    get_data(driver, out_file, latest_file_list, out_default_path, latest_download_file_list)
    time_sleep(2)

    print("\n~ ~ ~ F i n i s h e d ~ ~ ~ ")
