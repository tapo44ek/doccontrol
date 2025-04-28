# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 15:42:13 2023

@author: ArsenevVD
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 08:35:31 2023

@author: ArsenevVD
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
from multiprocessing import Process, Queue
from datetime import datetime, timedelta
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import warnings



def KK (s, DNSID, doc_id, queue):
    warnings.filterwarnings('ignore')
    url = f'https://mosedo.mos.ru/document.card.php?id={doc_id}&DNSID={DNSID}'
    r2 = s.get(url)
    # print (r2.text)
    doc_soup = BeautifulSoup(r2.text, 'html.parser').find('table', id='rez-list')
    print(doc_id)
    try:
        list_DS = doc_soup.findAll('span', class_='resolution-executor-history')
    except: list_DS = ['DSP']
    executor = []
    try:
        author_DS = doc_soup.findAll('div', class_='resolution-item__header')

        for item in author_DS:
            if item.find('span'):
                if item.find('span').find('span'):
                    if 'Габитов Д.Ш.' in item.find('span').find('span').text:
                        if item.parent.find('span', class_='resolution-executor-history'):
                            in_res = item.parent.findAll('span', class_='resolution-executor-history')
                            for res in in_res:
                                try:
                                    executor.append(res.text.replace('\n',' '))
                                except:
                                    executor.append('-')
    #                        executor.append(item.parent.find('span', class_='resolution-executor-history').text.replace('\n',' '))
                        else: executor.append('-')
                    else: executor.append('-')
                else: executor.append('-')
            else: executor.append('-')
    except: executor.append('Документ ДСП')
    
    df = pd.DataFrame(columns=['A', 'B', 'C'])
    if 'DSP' not in list_DS:
        for item in list_DS:
            data = []
            gr = item.text
            gr = gr.replace('\n',' ')
            gr = ' '.join(gr.split())
            gr = gr.lstrip()
            gr = gr.rstrip()
            gr = gr.split(' - ')
            if 'змене' in gr[2]:
                data.append(gr[0])
                data.append(datetime.strptime(gr[2].split(': ')[1], '%d.%m.%Y'))
                data.append(gr[3])
            else:
                data.append(gr[0])
                data.append(datetime.strptime(gr[1].split(': ')[1], '%d.%m.%Y'))
                data.append(gr[2])
            df.loc[ len(df.index )] = data
    else: df.loc[ len(df.index )] = ['Документ ДСП','Документ ДСП','Документ ДСП']
    df = df[df['C'].str.contains('снят с контроля')==False]    
    df_RG = df[df['A'].str.contains('Биктимиров')]
    if df_RG.empty == False:
        df_RG.sort_values(by='B', inplace = True)
        srok_rg = df_RG.iloc[0]['B']
    else:
        srok_rg = '-'

    df_OA = df[df['A'].str.contains('Мусиенко')]
    if df_OA.empty == False:
        df_OA.sort_values(by='B', inplace = True)
        srok_oa = df_OA.iloc[0]['B']
    else: 
        srok_oa = '-'

    df_MM = df[df['A'].str.contains('Гибадулин')]
    if df_MM.empty == False:
        df_MM.sort_values(by='B', inplace = True)
        srok_mm = df_MM.iloc[0]['B']        
    else: srok_mm = '-' 
    df_DS = df[df['A'].str.contains('Габитов')]
    if df_DS.empty == False:
        df_DS.sort_values(by='B', inplace = True)
        srok_ds = df_DS.iloc[0]['B']        
    else: srok_ds = '-' 
    if 'Документ ДСП' not in executor:
        i = len(executor) - 1
        while i >= 0:
            if 'нят с контро' in executor[i]:
                del executor[i]
            i = i - 1
        i = len(executor) - 1
        while i >= 0:
            try: executor.remove('-')
            except: pass
            i = i - 1
        i = len(executor) - 1
        while i >= 0:
            try: executor.remove('Габитов Д.Ш.')
            except: pass
            i = i - 1


    #    print('!!!!!!!!!!!!!!!!!              ',executor) #################################### написать алгоритм добавления в датафрейм с последующей сортировкой по дате
    #    executor_one = executor[0]
    #    df_executor = pd.DataFrame(columns=['A', 'B', 'C'])
        df_exec_list = []
        if len(executor) == 0:
            executor.append('-')
            df_exec = pd.DataFrame({'A':['-'],'B':['-'],'C':['-']})
            df_exec_list.append(df_exec)

        else:
            for j in range(len(executor)):
                df_exec1 = pd.DataFrame(columns=['A', 'B', 'C'])
    #            print(executor[i])


                executor_one = executor[j].replace('\n',' ')
                executor_one = ' '.join(executor_one.split())
                executor_one = executor_one.lstrip()
                executor_one = executor_one.rstrip()
                executor_one = executor_one.split(' - ')
                if executor_one == 'Габитов Д.Ш.':
                    executor_one = '-'
                if executor_one != '-':
    #                if len(executor_one) < 3:
    #                    print('!!!!!!!!!!!!!!!!    ',executor_one)
                    executor1 = []

                    if 'змене' in executor_one[2]:
                        executor1.append(executor_one[0])
                        executor1.append(datetime.strptime(executor_one[2].split(': ')[1], '%d.%m.%Y'))
                        executor1.append(executor_one[3])
                    else:
                        executor1.append(executor_one[0])
                        executor1.append(datetime.strptime(executor_one[1].split(': ')[1], '%d.%m.%Y'))
                        executor1.append(executor_one[2])
                else:
                    executor1.append('-')
                    executor1.append('-')
                    executor1.append('-')



                df_exec1 = pd.DataFrame([executor1], columns=['A','B','C'])
                df_exec_list.append(df_exec1)
        print('----------------',len(df_exec_list),'-------------')
        if len(df_exec_list) > 1:
            df_executor = pd.concat(df_exec_list)
            print(type(df_executor))
        else :
            df_executor = df_exec_list[0]
            print(type(df_executor))
    #    else:
    #        df_executor = pd.DataFrame({'A':['-'],'B':['-'],'C':['-']})

        if len(df_executor) > 1:
            df_executor = df_executor.sort_values(by='B')


        #df_executor.to_excel(f'C:\\Users\\ArsenevVD\\Desktop\\control_mail_2.1\\debug\\{doc_id}.xlsx')
        df_executor = df_executor.iloc[0]
        print(df_executor.head())
        executor = df_executor.to_list()


    ###################################################################################################################################################
        data = [doc_id, srok_ds, srok_mm, srok_oa, srok_rg, executor[0], executor[1], executor[2]]
    else: data = [doc_id, srok_ds, srok_mm, srok_oa, srok_rg, 'ДСП', 'ДСП', 'ДСП']
    df2 = pd.DataFrame([data], columns=['doc', 'DS', 'MM','OA', 'RG', 'executor', 'executor_date', 'executor_stat'])
    
#    print(data)
    queue.put(df2)
    return

def sogly (s, DNSID, page, queue):
    url = f'https://mosedo.mos.ru/document.php?perform_search=1&DNSID={DNSID}&page={page}'
    r1 = s.get(url)
    with open("sogl1.html", "w") as file:
        file.write(r1.text)
#    print(r1.text)
    soup = BeautifulSoup(r1.text, "html.parser")
    allNews = soup.find('table', class_='document-list')
#    print(allNews)
    allNews = allNews.find('tbody')
    allNews1 = BeautifulSoup(str(allNews), "html.parser")
    doc_number = [element.text for element in allNews1.find_all(class_="main_doc_table-doc-number")]
    
    
#    print(doc_number)
    
    
    doc_recipient = [element.text.replace('Кому:','') for element in allNews1.find_all('span', class_="s-doc__recipient")]
    
    short_data = [element.text for element in allNews1.find_all('div', class_="s-table__shortcontent")]
    doc_id = [element['href'] for element in allNews1.find_all('a', class_='document-list__registration-date')]
    
    
    
#    tdtables = allNews1.find_all('td', class_='document-list__td--author')
#    resp_docs = []
#    for td in tdtables:
#        prev_sibling = td.find_previous_sibling()
#        
#        if prev_sibling and prev_sibling.name:
#            child_tag = prev_sibling.find('div')
#            if child_tag:
#                resp_docs.append(child_tag.text)
#            else:
#                resp_docs.append('-')
#        else:
#            resp_docs.append('-')
    
    
    
    
    doc_date = []
    
    for i in range(len(doc_number)):
        doc_number[i] = doc_number[i].replace('\n','')
        doc_number[i] = ' '.join(doc_number[i].split())
        doc_number[i] = doc_number[i].lstrip()
        doc_number[i] = doc_number[i].rstrip()
        try:
            doc_date.append(datetime.strptime(doc_number[i].split()[1], '%d.%m.%Y'))
        except:
            doc_date.append('')
        doc_number[i] = doc_number[i].split()[0]
    
    for i in range(len(doc_recipient)):
        doc_recipient[i] = doc_recipient[i].replace('\n','')
        doc_recipient[i] = ' '.join(doc_recipient[i].split())
        doc_recipient[i] = doc_recipient[i].lstrip()
        doc_recipient[i] = doc_recipient[i].rstrip()
#        
        
        
        
        
#    for i in range(len(resp_docs)):
#        resp_docs[i] = resp_docs[i].replace('\n','')
#        resp_docs[i] = ' '.join(resp_docs[i].split())
#        resp_docs[i] = resp_docs[i].lstrip()
#        resp_docs[i] = resp_docs[i].rstrip()
#    
    
    
    
    
    
    for i in range(len(short_data)):
        short_data[i] = short_data[i].replace('\n','')
        short_data[i] = ' '.join(short_data[i].split())
        short_data[i] = short_data[i].lstrip()
        short_data[i] = short_data[i].rstrip()
    
    for i in range(len(doc_id)):
        doc_id[i] = doc_id[i].replace('\n','')
        doc_id[i] = ' '.join(doc_id[i].split())
        doc_id[i] = doc_id[i].lstrip()
        doc_id[i] = doc_id[i].rstrip()   
        doc_id[i] = doc_id[i].split('=')[1]
        doc_id[i] = doc_id[i].split('&')[0]
    
    data = []
    
    for a, b, c, d, e, in zip(doc_number, doc_date, doc_recipient, short_data, doc_id):
        data.append([a, b, c, d, e, ])

    df1 = pd.DataFrame(data, columns=['Номер согла', 'Дата согла', 'Адресат', 'Краткое содержание', 'doc_id'])
    print(df1)
    queue.put(df1)
#    return df1

def sogl_status (s, doc_number, DNSID, queue):    
    url = f'https://mosedo.mos.ru/document.card.php?id={doc_number}&DNSID={DNSID}'
    r1 = s.get(url)
    soup = BeautifulSoup(r1.text, "html.parser")
    sogl = soup.findAll('table', class_='agreetable')
    doc_card = soup.find('table', class_='scrollable-section')
    doc_card_soup = BeautifulSoup(str(doc_card), "html.parser")
    doc_card = doc_card_soup.find('div', id='inNumberListContainer')
    print(doc_card)
    doc_card_soup = BeautifulSoup(str(doc_card), "html.parser")
    registration = soup.find('a', class_='s-agree-subcomment__link')
    if registration:
        try:
            registration_status = registration.text
            registration_status = registration_status.replace('\n','')
            registration_status = ' '.join(registration_status.split())
            registration_status = registration_status.lstrip()
            registration_status = registration_status.rstrip()
        except: registration_status = '-'
    else: registration_status = '-'
    
    try:
        resp_doc = [doc_card_soup.find('a', class_="document-badge").text]
    except: resp_doc = ['-']
    
    for i in range(len(resp_doc)):
        if resp_doc[i]=='':
            resp_doc[i] = '-'
        resp_doc[i] = resp_doc[i].replace('\n','')
        resp_doc[i] = ' '.join(resp_doc[i].split())
        resp_doc[i] = resp_doc[i].lstrip()
        resp_doc[i] = resp_doc[i].rstrip()   
        
    if len(resp_doc) < 1:
        resp_doc.append('-')
    
    
    
    sogl_soup = BeautifulSoup(str(sogl), "html.parser")
    sogl_user = [element.text for element in sogl_soup.find_all('b', class_="agreetable__user-name")]
    sogl_status = [element.text for element in sogl_soup.find_all('span', class_="csdr-status")]
    sogl_date = []

    for i in range(len(sogl_user)):
        if sogl_user[i]=='':
            sogl_user[i] = '-'
        sogl_user[i] = sogl_user[i].replace('\n','')
        sogl_user[i] = ' '.join(sogl_user[i].split())
        sogl_user[i] = sogl_user[i].lstrip()
        sogl_user[i] = sogl_user[i].rstrip()
        
    for i in range(len(sogl_status)):
        if sogl_status[i]=='':
            sogl_status[i] = '-'
        sogl_status[i] = sogl_status[i].replace('\n','')
        sogl_status[i] = ' '.join(sogl_status[i].split())
        sogl_status[i] = sogl_status[i].lstrip()
        sogl_status[i] = sogl_status[i].rstrip()
        try:
            sogl_date.append(datetime.strptime(sogl_status[i].split()[1] + ' ' + sogl_status[i].split()[2], '%d.%m.%Y %H:%M'))
        except:
            sogl_date.append('')
        
        if r'Подписан' in sogl_status[i]:
            sogl_status[i] = sogl_status[i].split()[0]
            
        if r'Не согласов' in sogl_status[i]:
            sogl_status[i] = sogl_status[i].split()[0] + ' ' + sogl_status[i].split()[1]

#    print(sogl_status)
    datata = []
    for a, b, c,   in zip(sogl_user, sogl_status, sogl_date):
        datata.append([a, b, c, ])
    print(datata)
    df = pd.DataFrame(datata, columns=['Пользователь','Статус', 'Время статуса'])
    df.insert(2, 'На №', resp_doc[0])
    statuslist = df['Время статуса'].to_list()
    resp_list = df['На №'].to_list()
    statuslist = [item for item in statuslist if pd.isnull(item) == False]
    resp_list = [item for item in resp_list if pd.isnull(item) == False]
    print(df['Статус'])
#    a=input()
    df_new = df.loc[df['Статус'] == r'На согласовании/подписании']
    if df_new.empty == False:
        df_new['Время статуса'] = statuslist[-1]
        df_new['На №'] = resp_list[-1]
    if df_new.empty:
        #print(df)
        df_new = df.loc[df['Статус'].str.contains(r'Подписан')]
        df_new['Время статуса'] = statuslist[-1]
        df_new['На №'] = resp_list[-1]
    if df_new.empty:
        df_new = df.loc[df['Статус'].str.contains(r'Не согласов')]
        df_new['Время статуса'] = statuslist[-1]
        df_new['На №'] = resp_list[-1]
    if df_new.empty:
        df_new = df.loc[df['Статус'].str.contains(r'На подписа')]
        df_new['Время статуса'] = statuslist[-1]
        df_new['На №'] = resp_list[-1]
    if df_new.empty:
        df_new = pd.DataFrame({'Пользователь':['-'],'Статус':['-'], 'На №':[resp_list[-1]]})
    del df
    df_new.insert(0, 'doc_id', doc_number)
    df_new.insert(4, 'regisrtation', registration_status)
    queue.put(df_new)


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    ds = datetime.now()
    print(ds)
    d_start = '01.01.2019'
    year = datetime.now().year
    print(type(year))
    d_end = f'31.12.{year}'
    EXECUTOR_ID = '78264321'  #ДШ
    date_now = datetime.strftime(datetime.now(), '%d.%m.%Y')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    
    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome()

    url_kontrol = f'https://mosedo.mos.ru/auth.php?uri=%2Fstat%2Fcontrol_stats.details.php%3Ffixed%3D%26delegate_id%3D%26is_letter%3D%26report_name%3Dcontrol_stats%26ctl_type%255B0%255D%3D0%26ctl_type%255B1%255D%3D1%26later_type%3D0%26due_date_from%3D{d_start}%26due_date_until%3D{d_end}%26start_rdate%3D%26end_rdate%3D%26user%255B0%255D%3D0%26inv_user%255B0%255D%3D0%26executor%3D{EXECUTOR_ID}%26inv_executor%3D0%26result%3D%25D1%25F4%25EE%25F0%25EC%25E8%25F0%25EE%25E2%25E0%25F2%25FC%2B%25EE%25F2%25F7%25E5%25F2...'
    url_auth = 'https://mosedo.mos.ru/auth.php?group_id=21'
    
    with open(r'C:\control_mail_2.1\settings.json') as f:
        settings = json.load(f)
        token = settings['token2']
        SEDOlog = settings['SEDOlog']
        SEDOpass = settings['SEDOpass']
        print(SEDOpass)
        PCuser = settings['PCuser']
        UserID = settings['UserID']

    s = requests.Session()

     
    driver.get(url_kontrol)
    organization = driver.find_element(By.XPATH, '//*[@id="organizations"]')
    user = driver.find_element(By.XPATH, '//*[@id="logins"]')
    psw = driver.find_element(By.XPATH, '//*[@id="password_input"]')
    login = driver.find_element(By.XPATH, '//*[@id="login_form"]/table/tbody/tr[11]/td[4]/input[1]')
    organization.send_keys('Департамент городского имущества города Москвы')
    time.sleep(2)
    organization1 = driver.find_element(By.XPATH, '//*[@id="ui-id-1"]/li/a[text() = "Департамент городского имущества города Москвы"]')
    organization1.click()
    user.send_keys(SEDOlog)
    time.sleep(3)
    user1 = driver.find_element(By.XPATH, '//*[@id="ui-id-2"]/li/a[text() = "'+ str(SEDOlog) +'"]')
    user1.click()
    psw.send_keys(SEDOpass)
    login.click()
    time.sleep(2)
    try:
        WebDriverWait(driver,6000).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div[2]/div/div[3]/div/div/table[1]')))
    except:
        print("Timed out waiting for page to load")
    page = driver.page_source
#    with open("control_page.html", "w") as file:
#        file.write(page) 
    driver.close()
    
    soup = BeautifulSoup(page, "html.parser")
    first_soup = soup.find('h4', text='Документы на контроле').parent.findNext('table').findNext('tbody').find_all('tr')
    print(len(first_soup))
    print(len(first_soup[0].find_all('td')))
    
    df = pd.DataFrame(columns=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'doc'])
    for j in range(len(first_soup)):
        data = []
        for i in range(len(first_soup[j].find_all('td'))):
            
            if first_soup[j].find_all('td')[i].text :
                gr = first_soup[j].find_all('td')[i].text
                gr = gr.replace('\n',' ')
                gr = ' '.join(gr.split())
                gr = gr.lstrip()
                gr = gr.rstrip()
                data.append(gr)
                
            else: data.append('-')
            
        if first_soup[j].find('a')['href']:
            doc_id = first_soup[j].find('a')['href']
            doc_id = doc_id.replace('\n','')
            doc_id = ' '.join(doc_id.split())
            doc_id = doc_id.lstrip()
            doc_id = doc_id.rstrip()   
            doc_id = doc_id.split('=')[1]
            doc_id = doc_id.split('&')[0]
            data.append(doc_id)
        else: data.append('-')
#        print(data)
        df.loc[len(df.index)] = data
        
    df.drop_duplicates(subset="B",
                     keep='first', inplace=True)
    df['B'] = df['B'].apply(lambda x: x.split()[0])
    df['A'] = np.arange(1, 1 + len(df))
    
#    print(df.info)
    #df.to_excel('kk_ds_test.xlsx')

    
    DNSID = 'wJBIu0NhWLwF8YslRiym5mw'

    data = {"DNSID":DNSID, 
            "group_id":"21",
            "login":SEDOlog,
            "user_id":"78264321", #"78264321",
            "password":SEDOpass,  #                                           ПОМЕНЯТЬ НА ДАННЫЕ ИЗ ФАЙЛА КОНФИГУРАЦИИ
            "token":"",
            "x":"1"}

    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
            'Connection': 'keep-alive'}
    


#    doc_id = '399854870'

    
    
    
    r = s.post('https://mosedo.mos.ru/auth.php?group_id=21&size=1920&x=1080', data=data, headers=headers, allow_redirects=False)
    print(r)
    print(r.headers)
    DNSID = r.headers['location'].split('DNSID=')[1]
    # auth_token = s.cookies.get_dict()['auth_token']
    headers2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Connection': 'keep-alive',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document'
    }
    url_sogl = f'https://mosedo.mos.ru/document.php?all=1&category=6&DNSID={DNSID}&whole_period=1&ajax=1&page=1&isJson=0&DNSID={DNSID}'
    url_control = f'https://mosedo.mos.ru/stat/reports_msk.php?DNSID={DNSID}'
    s.cookies
    
    r1 = s.get(url_sogl)
    s.cookies
    
#    df_final = pd.DataFrame(columns = ['doc_id', 'MM', 'OA', 'RG'])




    
    queue = Queue()
    processes = []
    df_list = []
    df_final = pd.DataFrame()

    
    doc_list = df['doc'].to_list()
    try:
        doc_list.remove('-')
    except: pass
    count_doc = len(doc_list)
    
    for i in range(count_doc):
        p = Process(target=KK, args=(s, DNSID, doc_list[i], queue))
        p.start()
        processes.append(p)
        
    for i in range(count_doc):
        df1 = queue.get()
        df_list.append(df1)
    
    for p in processes:
        p.join()
    
    df_final = pd.concat(df_list)
    df_final.to_excel(r'C:\control_mail_2.1\KK_test_1_0.xlsx', index= False)
    
    df_export = pd.merge(df, df_final, on='doc', how='left')       
    

        
        
    df_export.to_excel(r'C:\control_mail_2.1\KK_test_1.xlsx', index= False)
#    
#    
##df_final.to_excel('test_sogl.xlsx')
#    s.close()    
#    de = datetime.now()
#    print (de)
#    print ('\n')
#    print (de-ds)

###########################################################################
    sogl_s_date = datetime.strftime(datetime.now() - timedelta(days=14), '%d.%m.%Y')
    sogl_end_date = datetime.strftime(datetime.now(), '%d.%m.%Y')
                                    
    try:
        df_exist = pd.read_excel(r'C:\control_mail_2.1\test_sogl_status_v1.xlsx')
        df_exist = df_exist.loc[df_exist['Статус'] == 'Подписано']
        documents_trash = df_exist['doc_id'].to_list()
        print (documents_trash)
        
    except:
        documents_trash = []
        df_exist = pd.DataFrame()



    data = {"DNSID":DNSID, 
            "group_id":"21",
            "login":SEDOlog,#%C0%F0%F1%E5%ED%FC%E5%E2+%C2.%C4.
            "user_id":"78264321", ##80742170 Арсеньев ##78264321 Габитов
            "password":SEDOpass,
            "token":"",
            "x":"1"}

    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
            'Connection': 'keep-alive',}
    
    data_DS = {
            'check_all_projects':'on' ,
            'project_type_1':'1' ,
            'project_type_3':'1' ,
            'project_type_13':'1' ,
            'project_type_4':'1' ,
            'project_type_5':'1' ,
            'has_period':'1' ,
            'year_from':'2009' ,
            'year_to':f'{str(year)}' ,
            'order_by':'default' ,
            'required_text':'' ,
            'num':'' ,
            'rdate_f':'' ,
            'org_name':'%C4%C3%C8%E3%CC' ,
            'org':'21' ,
            'rdate_t':'' ,
            'reg_user':'' ,
            'reg_user_id':'' ,
            'recipient':'' ,
            'recipient_id':'' ,
            'recipient_group':'' ,
            'recipient_group_id':'' ,
            'in_number':'' ,
            'bound_number':'' ,
            'contract_bound_number':'' ,
            'recipient_org_id':'' ,
            'cl_out_num':'' ,
            'cl_out_date_f':'' ,
            'cl_out_date_t':'' ,
            'cl_sign':'' ,
            'cl_sign_id':'' ,
            'cl_sign_group':'' ,
            'cl_sign_group_id':'' ,
            'cl_executor':'' ,
            'cl_executor_id':'' ,
            'cl_executor_group':'' ,
            'cl_executor_group_id':'' ,
            'cl_text':'' ,
            'out_number':'' ,
            'out_date_f':'' ,
            'out_reg_user':'' ,
            'out_reg_user_id':'' ,
            'out_date_t':'' ,
            'author':'' ,
            'author_id':'' ,
            'author_group':'' ,
            'author_group_id':'' ,
            'prepared_by':'' ,
            'prepared_by_id':'' ,
            'prepared_by_org_id':'' ,
            'curator':'' ,
            'curator_id':'' ,
            'short_content':'' ,
            'document_kind':'0' ,
            'delivery_type':'' ,
            'document_special_kind':'0' ,
            'external_id':'' ,
            'has_manual_sign':'0' ,
            'is_hand_shipping':'0' ,
            'sign_type':'0' ,
            'is_dsp':'0' ,
            'is_control':'0' ,
            'is_urgent':'0' ,
            'creator':'' ,
            'creator_id':'' ,
            'memo':'' ,
            'send_date_f':'' ,
            'send_date_t':'' ,
            'info':'' ,
            'info_author':'' ,
            'info_author_id':'' ,
            'info_date_f':'' ,
            'info_date_t':'' ,
            'og_file_number':'0' ,
            'rec_vdelo':'0' ,
            'vdelo_date_f':'' ,
            'vdelo_date_t':'' ,
            'vdelo_prepared':'' ,
            'vdelo_prepared_id':'' ,
            'vdelo_signed':'' ,
            'vdelo_signed_id':'' ,
            'vdelo_text':'' ,
            'res_type':'0' ,
            'res_urgency':'0' ,
            'resolution_num':'' ,
            'r_rdate_f':'' ,
            'resolution_creator':'' ,
            'resolution_creator_id':'' ,
            'r_rdate_t':'' ,
            'resolution_author':'' ,
            'resolution_author_id':'' ,
            'resolution_author_group':'' ,
            'resolution_author_group_id':'' ,
            'resolution_author_org_id':'' ,
            'r_special_control':'0' ,
            'resolution_behalf':'' ,
            'resolution_behalf_id':'' ,
            'resolution_acting_author':'' ,
            'resolution_acting_author_id':'' ,
            'resolution_to':'' ,
            'resolution_to_id':'' ,
            'resolution_to_group':'' ,
            'resolution_to_group_id':'' ,
            'resolution_to_org_id':'' ,
            'res_project_letter':'0' ,
            'res_curator':'' ,
            'res_curator_id':'' ,
            'r_control':'0' ,
            'r_control_f':'' ,
            'r_control_t':'' ,
            'r_otv':'0' ,
            'r_dback':'0' ,
            'resolution_text':'' ,
            'r_ef_reason_category_id':'0' ,
            'r_ef_reason_id':'0' ,
            'r_is_signed':'0' ,
            'r_plus':'0' ,
            'r_another_control':'0' ,
            'r_oncontrol':'0' ,
            'r_oncontrol_f':'' ,
            'r_oncontrol_t':'' ,
            'unset_control':'0' ,
            'unset_control_f':'' ,
            'unset_control_t':'' ,
            're_date_f':'' ,
            're_date_t':'' ,
            're_author':'' ,
            're_author_id':'' ,
            're_author_group':'' ,
            're_author_group_id':'' ,
            're_acting_author':'' ,
            're_acting_author_id':'' ,
            're_is_interim':'-1' ,
            're_text':'' ,
            'docs_in_execution':'0' ,
            're_doc_org_id':'' ,
            'csdr_initiator':'' ,
            'csdr_initiator_id':'' ,
            'csdr_initiator_group':'' ,
            'csdr_initiator_group_id':'' ,
            'csdr_start':'0' ,
            'csdr_start_date_f':sogl_s_date,
            'csdr_start_date_t':sogl_end_date,
            'csdr_stop':'0' ,
            'csdr_current_version_only':'1',
            'and[csdr][0]':'0',
            'participant_name_0':'%C3%E0%E1%E8%F2%EE%E2+%C4.%D8.' ,
            'participant_name_0_id':'78264321' ,
            'participant_group_0':'%C4%E5%EF%E0%F0%F2%E0%EC%E5%ED%F2+%E3%EE%F0%EE%E4%F1%EA%EE%E3%EE+%E8%EC%F3%F9%E5%F1%F2%E2%E0+%E3%EE%F0%EE%E4%E0+%CC%EE%F1%EA%E2%FB' ,
            'participant_group_0_id':'21' ,
            'csdr_has_deadline_0':'0' ,
            'csdr_status_0':'0' ,
            'csdr_init_date_0_f':'' ,
            'csdr_init_date_0_t':''
            }

    # url_sogl = f'https://mosedo.mos.ru/document_search.php?new=0&DNSID={DNSID}'
    #
    # r = s.post(url_auth, data=data, headers=headers)
    r = s.post('https://mosedo.mos.ru/auth.php?group_id=21&size=1920&x=1080', data=data, headers=headers, allow_redirects=False)
    print(r)
    print(r.headers)
    DNSID = r.headers['location'].split('DNSID=')[1]
    # auth_token = s.cookies.get_dict()['auth_token']
    headers2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Connection': 'keep-alive',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
    }
    url_sogl = f'https://mosedo.mos.ru/document_search.php?new=0&DNSID={DNSID}'
    url_control = f'https://mosedo.mos.ru/stat/reports_msk.php?DNSID={DNSID}'
    s.cookies

    r2 = s.post(url_sogl, data=data_DS, headers=headers)
    
    first_soup = BeautifulSoup(r2.text, 'html.parser')
    try:
        count_doc = int(first_soup.find('span', class_='search-export__count').text.split(': ')[1])
    except: count_doc = 1
    count_doc = count_doc//15 + 1
    print (count_doc)

    with open("sogl.html", "w") as file:
        file.write(r2.text)
    
    
    df_final = pd.DataFrame()

    


    i = 1
    k = 0
    
    queue = Queue()
    processes = []
    df_list = []
    df_final = pd.DataFrame()
    
    for i in range(1,count_doc+1):
        p = Process(target=sogly, args=(s, DNSID, i, queue))
        p.start()
        processes.append(p)
        
    for i in range(1,count_doc+1):
        df = queue.get()
        df_list.append(df)
    
    for p in processes:
        p.join()
        
    df_final = pd.concat(df_list)
    print(df_final)
        
#    while k == 0:
#        df = sogly(DNSID, i)
#    
#        if df.empty:
#            k = k + 1
#        
#        df_final = pd.concat([df_final, df]) 
#        i = i + 1 
    
    documents = df_final['doc_id'].to_list()
    
    for i in range(len(documents_trash)):
        try: 
            documents.remove(str(documents_trash[i]))
        except:
            pass
        
    queue = Queue()
    processes = []
    df_list = []
    print(documents)
    df_status = pd.DataFrame()

    
    for i in range(len(documents)):
        p = Process(target=sogl_status, args=(s, documents[i], DNSID, queue))
        p.start()
        processes.append(p)
 
    for i in range(len(documents)):
        df = queue.get()
        df_list.append(df)
    
    for p in processes:
        p.join()
    
    df_status = pd.concat(df_list)
    df_final = pd.merge(df_final, df_status, on='doc_id', how='left')
    df_final = df_final.loc[pd.isna(df_final['Статус']) == False]
    if df_exist.empty == False:
        df_exist = df_exist.astype({'doc_id': str})
    df_final = pd.concat([df_final, df_exist])
    df_final['На №'] = df_final['На №'].apply(lambda x: x.split()[0])
    df_export = pd.merge(df_export, df_final, left_on='B', right_on='На №', how='left')
    df_export.to_excel(r'C:\control_mail_2.1\output1.xlsx')
        
#    df_final['Статус'] = df_final['Статус'].fillna('Подписано')
#    df_final = pd.merge(df_final, df_exist, on='doc_id', how='left')
        
        
    df_final.to_excel(r'C:\control_mail_2.1\sogl_ds.xlsx', index= False)
    
    
#df_final.to_excel('test_sogl.xlsx')
    s.close()    
    de = datetime.now()
    print (de)
    print ('\n')
    print (de-ds)

















