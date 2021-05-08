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

import re

import unicodedata

import urllib.request

from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import getopt
import io

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
                defaults['output_path'] = '{}/{}-BNL-PRIVATI-***.txt'.format(defaults['output_default_path'], str_date)
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

def get_data(output_file, latest_file_list, output_default_path, latest_download_file_list):

    parenturls = [
        'https://bnl.it/it/Footer/Trasparenza/Documenti-di-Trasparenza/Libretti-deposito-a-risparmio',
        'https://bnl.it/it/Footer/Trasparenza/Documenti-di-Trasparenza/Mutui',
        'https://bnl.it/it/Footer/Trasparenza/Documenti-di-Trasparenza/Carte',
        'https://bnl.it/it/Footer/Trasparenza/Documenti-di-Trasparenza/Servizi-Italia',
        'https://bnl.it/it/Footer/Trasparenza/Documenti-di-Trasparenza/Titoli',
        'https://bnl.it/it/Footer/Trasparenza/Documenti-di-Trasparenza/Conti-Correnti'
    ]

    maintitle = ['LIBRETTI DEPOSITO A RISPARMIO', 'MUTUI', 'CARTE DI CREDITO, DEBITO E PREPAGATE', 'SERVIZI ITALIA', 'TITOLI', '']
   
    tmpoutputfile = output_file


    isFileExist = os.path.isfile(latest_file_list)
    lstFileContent = []
    if isFileExist:
        f = open(latest_file_list, "r")
        for content in f:
          lstFileContent.append(content)

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
        latestfile = open(filename.replace('\n', '').replace('"', ''), 'r')
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

    itemindex = 0
    for url in parenturls:
        driver = get_seleniumdriver(url)
        print("====={}".format(maintitle[itemindex]))
        output_file = tmpoutputfile.replace("***", maintitle[itemindex])


        output = {'header1':'', 'header2':''}
        output_filename = {'filename':''}

        if itemindex in [0, 1, 2]:
            items = driver.find_elements_by_xpath(".//div[@class='accordion-content']//p") 
        if itemindex in [3, 4]:
            items = driver.find_elements_by_xpath(".//div[@class='iw_component']/div[2]/div[@class='accordion-content']/div[@class='legal-attachment doc-pdf']")
        if itemindex == 5:
            soup = BeautifulSoup(driver.page_source)
            allitems = soup.findAll('div',attrs={'class':'legal-module'})

            #allitems = driver.find_elements_by_xpath(".//div[@class='iw_component']/div[@class='legal-module']")
            print('allitemcount:{}'.format(len(allitems)))
            
            for _itemindex in range(int(len(allitems)/2)):
                
                parentitem = allitems[_itemindex * 2]
                childitem = allitems[_itemindex * 2 + 1]

                parenttitle = parentitem.text.replace("\n", "")
                print('------parentitle:{}'.format(parenttitle))

                output_file = tmpoutputfile.replace("***", parenttitle)

                csvfile = open(output_file, 'w')
                print("output_file:{}".format(output_file))
                writer = csv.DictWriter(csvfile, delimiter=",", fieldnames=output_header)
                output_downloadfilename = {'filename':''}

                difffile_field = {'COMPANY':'', 'DATE':'', 'SEGMENT':'', 'MAIN PRODUCT':'', 'PRODUCT':'', 'CODE':''}


                childitems = childitem.findAll('div',attrs={'class':'legal-attachment doc-pdf'})

                for subitem in childitems:
                    if subitem.text == '':
                        continue
                    output['header1'] = parenttitle
                    output['header1'] = re.sub(r'[/\\:*?"<>|]', '', parenttitle)

                    output['header2'] = subitem.text.replace('\n', '')
                    output['header2'] = re.sub(r'[/\\:*?"<>|]', '', output['header2'])

                    print("---------item:{}".format(output['header2']))
                    writer.writerow(output)

                    #if not output['header2'] in FileContent:
                    #download the pdf doc
                    isdir1 = os.path.isdir('{}/BNL/'.format(output_default_path))
                    if not isdir1:
                        os.mkdir('{}/BNL'.format(output_default_path)) 
                    isdir2 = os.path.isdir('{}/BNL/PRIVATI/'.format(output_default_path))
                    if not isdir2:
                        os.mkdir('{}/BNL/PRIVATI/'.format(output_default_path))
                    isdir3 = os.path.isdir('{}/BNL/PRIVATI/{}/'.format(output_default_path, output['header1']))
                    if not isdir3:
                        os.mkdir('{}/BNL/PRIVATI/{}/'.format(output_default_path, output['header1'])) 

                    pdfdocfilename = "{}/BNL/PRIVATI/{}/{}-BNL-PRIVATI-{}.pdf".format(output_default_path, output['header1'], str_date, output['header2'])
                    
                    try:
                        pdflinktext = subitem.find("a")['href']
                    except Exception as e:
                        print('Error:{}'.format(e))
                        continue
                    #print(pdfdocfilename, pdflinktext)

                    print("{} downloading...".format(pdflinktext))
                    try:
                        req = urllib.request.Request(pdflinktext, headers={'User-Agent': 'Mozilla/5.0'})

                        file = open(pdfdocfilename, 'wb')
                        file.write(urllib.request.urlopen(req).read())
                        file.close()
                        #urllib.request.urlretrieve(pdflinktext, pdfdocfilename)
                    except Exception as e:
                        print("Download Error:{}".format(e))
                        continue
                    output_downloadfilename['filename'] = pdfdocfilename
                    latest_download_file_writer.writerow(output_downloadfilename)

                    #compare file changes
                    difffile_field['COMPANY'] = 'BNL'
                    difffile_field['DATE'] = str_date
                    difffile_field['SEGMENT'] = 'PERSONA'
                    difffile_field['MAIN PRODUCT'] = output['header1']
                    difffile_field['PRODUCT'] = output['header2']
                    curpdfname = pdfdocfilename
                    prepdfname = ''
                    for onefilename in lstdownloadfilecontent:
                        if output['header2'] in onefilename:
                            prepdfname = onefilename
                            continue

                    print("{} and {}".format(prepdfname, curpdfname))

                    difffile_field['CODE'] = 'no-change'
                    if prepdfname != "":
                        convertMultiple(curpdfname.replace('\n', ''), prepdfname.replace('\n', ''), '{}/TEXT_OUT/'.format(output_default_path))


                        f1 = open("{}/TEXT_OUT/1.pdf.txt".format(output_default_path))
                        f2 = open("{}/TEXT_OUT/2.pdf.txt".format(output_default_path))

                        lines = f2.readlines()
                        changedetailfilename = '{}/DIFF/DETAIL/{}-BNL-PRIVATI-{}.txt'.format(output_default_path, str_date, output['header2'])
                        detailfile = open(changedetailfilename, 'w')
                        for i,line in enumerate(f1):
                            try:
                                if line != lines[i]:
                                    print("line", i, "is different:")
                                    print('\t', line)
                                    print('\t', lines[i])
                                    difffile_field['CODE'] = 'change'

                                    detailfile.write("======================\nline, {}, is different: \n {} \n {}\n======================\n".format(i, line, lines[i]))
                            except:
                                    print("line", i, "is different:")
                                    print('\t', line)
                                    difffile_field['CODE'] = 'change'

                                    detailfile.write("======================\nline, {}, is different: \n {} \n No content\n======================\n".format(i, line))

                        detailfile.close()
                        if difffile_field['CODE'] == 'no-change':                
                            os.remove(changedetailfilename)

                    diffwriter.writerow(difffile_field)
                    print('difffile_field:{}'.format(difffile_field))


                csvfile.close()
                time_sleep(2)

                output_filename['filename'] = output_file
                latest_file_list_writer.writerow(output_filename)

            
            driver.close()
            latest_file.close()
            latest_download_file.close()
            difffile.close()

            return
                

        print('Itemcount:{}'.format(len(items)))
        

        csvfile = open(output_file, 'w')
        print("output_file:{}".format(output_file))
        writer = csv.DictWriter(csvfile, delimiter=",", fieldnames=output_header)
        output_downloadfilename = {'filename':''}

        difffile_field = {'COMPANY':'', 'DATE':'', 'SEGMENT':'', 'MAIN PRODUCT':'', 'PRODUCT':'', 'CODE':''}

        for item in items:
            if item.text == '':
                continue
            output['header1'] = maintitle[itemindex]

            output['header2'] = item.text
            output['header2'] = re.sub(r'[/\\:*?"<>|]', '', output['header2'])

            print("---------item:{}".format(output['header2']))
            writer.writerow(output)

            #if not output['header2'] in FileContent:
            #download the pdf doc
            isdir1 = os.path.isdir('{}/BNL/'.format(output_default_path))
            if not isdir1:
                os.mkdir('{}/BNL'.format(output_default_path)) 
            isdir2 = os.path.isdir('{}/BNL/PRIVATI/'.format(output_default_path))
            if not isdir2:
                os.mkdir('{}/BNL/PRIVATI/'.format(output_default_path))
            isdir3 = os.path.isdir('{}/BNL/PRIVATI/{}/'.format(output_default_path, maintitle[itemindex]))
            if not isdir3:
                os.mkdir('{}/BNL/PRIVATI/{}/'.format(output_default_path, maintitle[itemindex])) 

            pdfdocfilename = "{}/BNL/PRIVATI/{}/{}-BNL-PRIVATI-{}.pdf".format(output_default_path, maintitle[itemindex], str_date, output['header2'])
            
            try:
                pdflinktext = item.find_element_by_tag_name("a").get_attribute('href')
            except Exception as e:
                print('Error:{}'.format(e))
                continue
            #print(pdfdocfilename, pdflinktext)

            print("{} downloading...".format(pdflinktext))
            try:
                req = urllib.request.Request(pdflinktext, headers={'User-Agent': 'Mozilla/5.0'})

                file = open(pdfdocfilename, 'wb')
                file.write(urllib.request.urlopen(req).read())
                file.close()
                #urllib.request.urlretrieve(pdflinktext, pdfdocfilename)
            except Exception as e:
                print("Download Error:{}".format(e))
                continue
            output_downloadfilename['filename'] = pdfdocfilename
            latest_download_file_writer.writerow(output_downloadfilename)

            #compare file changes
            difffile_field['COMPANY'] = 'BNL'
            difffile_field['DATE'] = str_date
            difffile_field['SEGMENT'] = 'PERSONA'
            difffile_field['MAIN PRODUCT'] = output['header1']
            difffile_field['PRODUCT'] = output['header2']
            curpdfname = pdfdocfilename
            prepdfname = ''
            for onefilename in lstdownloadfilecontent:
                if output['header2'] in onefilename:
                    prepdfname = onefilename
                    continue

            print("{} and {}".format(prepdfname, curpdfname))

            difffile_field['CODE'] = 'no-change'
            if prepdfname != "":
                convertMultiple(curpdfname.replace('\n', ''), prepdfname.replace('\n', ''), '{}/TEXT_OUT/'.format(output_default_path))


                f1 = open("{}/TEXT_OUT/1.pdf.txt".format(output_default_path))
                f2 = open("{}/TEXT_OUT/2.pdf.txt".format(output_default_path))

                lines = f2.readlines()
                changedetailfilename = '{}/DIFF/DETAIL/{}-BNL-PRIVATI-{}.txt'.format(output_default_path, str_date, output['header2'])
                detailfile = open(changedetailfilename, 'w')
                for i,line in enumerate(f1):
                    try:
                        if line != lines[i]:
                            print("line", i, "is different:")
                            print('\t', line)
                            print('\t', lines[i])
                            difffile_field['CODE'] = 'change'

                            detailfile.write("======================\nline, {}, is different: \n {} \n {}\n======================\n".format(i, line, lines[i]))
                    except:
                            print("line", i, "is different:")
                            print('\t', line)
                            difffile_field['CODE'] = 'change'

                            detailfile.write("======================\nline, {}, is different: \n {} \n No content\n======================\n".format(i, line))

                detailfile.close()
                if difffile_field['CODE'] == 'no-change':                
                    os.remove(changedetailfilename)

            diffwriter.writerow(difffile_field)
            print('difffile_field:{}'.format(difffile_field))
            
        driver.close()
        itemindex = itemindex + 1
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
        text1 = convert(curpdfname) #get string of text content of pdf
        textFilename1 = txtDir + "1.pdf.txt"
        textFile1 = open(textFilename1, "w") #make text file
        textFile1.write(text1) #write text to text file

        text2 = convert(prepdfname) #get string of text content of pdf
        textFilename2 = txtDir + "2.pdf.txt"
        textFile2 = open(textFilename2, "w") #make text file
        textFile2.write(text2) #write text to text file


if __name__ == '__main__':
    config_option = load_config()

    out_file = config_option['output_path']
    out_default_path = config_option['output_default_path']

    latest_file_list = os.path.join(out_default_path, "latest_file_list")
    latest_download_file_list = os.path.join(out_default_path, "latest_downloadfile_list")


    get_data(out_file, latest_file_list, out_default_path, latest_download_file_list)
    time_sleep(2)


    print("\n~ ~ ~ F i n i s h e d ~ ~ ~ ")
