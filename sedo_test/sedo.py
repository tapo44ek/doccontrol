from bs4 import BeautifulSoup, Tag
import re
from datetime import datetime
import psycopg2
import sys
import os
from config import ProjectManagementSettings
import pandas as pd


def get_recipient_fio(rec_id :int):
    """
    function gets recipient id and search fio in catalog.sedo 
    usually used for mathing resolution recipient and due dates in resolution
    """

    connection = psycopg2.connect(
            host=ProjectManagementSettings.DB_HOST,
            user=ProjectManagementSettings.DB_USER,
            password=ProjectManagementSettings.DB_PASSWORD,
            port=ProjectManagementSettings.DB_PORT,
            database=ProjectManagementSettings.DB_NAME
        )
    cursor = connection.cursor()

    cursor.execute(f'SELECT name FROM catalog.sedo WHERE sedo_id = {rec_id}')

    row = cursor.fetchone()
    fio = row[0] if row else 'ERROR'

    return fio


def parse_control_dates(span):
    """
    get span with control date/dates for a man or a group of people (bs4 object)
    returns ....
    """

    pattern = (
        r'^(.*?)\s+-\s+срок:\s+(\d{2}\.\d{2}\.\d{4})'
        r'(?:\s+-\s+изменен:\s+(\d{2}\.\d{2}\.\d{4}))?'
        r'(?:\s+-\s+снят с контроля:\s+(\d{2}\.\d{2}\.\d{4}))?'
        r'(?:\s+-\s+просрочено\s+(\d+)\s+(?:день|дня|дней))?$'
    )
    # print(span.get_text())
    people = span.get_text().split('\n')
    result = []
    for man in people:
        if man == '':
            continue
        match = re.match(pattern, man.strip())

        if match:
            person = match.group(1)
            due_date = match.group(2)
            modified_date = match.group(3) or None
            closed_date = match.group(4) or None
            overdue_days = int(match.group(5)) if match.group(5) else None
            # if 'арапо' in person:
                # result = {'person': person, 
                #     'due_date': due_date, 
                #     'modified_date': modified_date, 
                #     'closed_date': closed_date, 
                #     'overdue_day': overdue_days}

                # print(result)

            # print("👤", person)
            # print("📅 срок:", due_date)
            # print("🛠 изменен:", modified_date)
            # print("✅ снят:", closed_date)
            # print("⏱ просрочено:", overdue_days)
            result.append({'person': person, 
                    'due_date': due_date, 
                    'modified_date': modified_date, 
                    'closed_date': closed_date, 
                    'overdue_day': overdue_days})
        else:
            print("❌ Не удалось разобрать строку\n", man)
            result.append({'person': None, 
                    'due_date': None, 
                    'modified_date': None, 
                    'closed_date': None, 
                    'overdue_day': None})
    # print(result)
    return result
    


class Resolution():

    __slots__ = ('sedo_id', 
                'type', 
                'parent_ids', 
                'child_ids', 
                'author_id', 
                'date', 
                'is_cancelled', 
                'recipients'
    )

    def __init__ (self):
        self.sedo_id :str = None
        self.type :int = None
        self.parent_ids :list = None
        self.child_ids :list = None
        self.author_id :int = None
        self.date :datetime = None
        self.is_cancelled :bool = False
        self.recipients = None


class Recipient():
    __slots__ = ('recipient_id', 
                'resolution_id', 
                'on_control', 
                'due_date',
                'done_date', 
                'is_master', 
                'is_cancelled', 
                'note'
    )

    def __init__ (self):
        self.recipient_id :int = None
        self.resolution_id :str = None
        self.on_control :bool = False
        self.due_date :datetime = None
        self.done_date :datetime = None
        self.is_master :bool = False
        self.is_cancelled :bool = False
        self.note :str = ''

    def set_red_control(self, control_date :datetime):
        self.on_control = True
        self.due_date = control_date

    def set_green_control(self, control_date :datetime):
        self.on_control = False
        self.due_date = control_date

    def set_done_date(self, complete_date :datetime):
        self.done_date = complete_date

    def set_master(self):
        self.is_master = True

    def __repr__ (self):

        if self.on_control:
            due_date = f'На контроле, срок - {datetime.strftime(due_date, '%d.%m.%Y')}'
        elif self.due_date:
            due_date = f'Срок исполнения - {datetime.strftime(due_date, '%d.%m.%Y')}'
        else:
            due_date = 'Без срока'

        if self.is_master:
            is_master = '(Отв.)'
        else:
            is_master = ''

        return f'По резолюции {self.resolution_id} - Исполнитель {self.recipient_id} {is_master} {due_date}'


        



def is_visible_tr(tr):
    '''
    keeps only elements without display:none
    '''

    style = tr.get('style', '') or ''
    return 'display:none' not in style.replace(' ', '').lower()


def print_tree(nodes, level=0):
    """
    prints visual for resolution tree
    """
    for node in nodes:
        if node.get("dl"):
            level = node.get("dl")
        indent = '  ' * level
        nid = node.get("id", "∅")
        is_exec = node.get("execution", False)

        if is_exec:
            print(f"{indent}[✓ исполнено]")
        else:
            print('\n')
            print(f"{indent}id={nid}, dl={node.get('dl')}, info={node.get('data')} ")

        # Сначала отображаем дочерние элементы
        for child in node.get("children", []):
            print_tree([child], level + 1)

        # Потом — исполнения, если есть
        for exec_note in node.get("executions", []):
            print_tree([exec_note], level + 1)

            

def get_fwd_info(item):
    """
    params: item: bs4 object
    get data from forwardings of documents
    """
    res_type = item.find('span', attrs={"class": "resolution-item__prefix"}).text
    res_date = item.find('span', attrs={"class": "resolution-item__timestamp"}).text

    match = re.search(r'\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}', res_date)


    if match:
        res_date = match.group()
        res_date = datetime.strptime(res_date, '%d.%m.%Y %H:%M:%S')

    res_author_id = item.find('span', attrs={"class": "resolution-item__recipient-title"})\
        .find_next_sibling('span')\
            .find('span')\
                .get('axuiuserid')


    res_recipients = item.find_all('span', attrs={"class": "to-user-container"})
    recipients = []
    # res_recipients_ids = []
    # res_recipients_texts = []
    for recipient in res_recipients:
        recipients.append({'sedo_id': recipient.find('span').get('axuiuserid'),
                            'text': recipient.find('span').text,
                            'fio': get_recipient_fio(recipient.find('span').get('axuiuserid')),
                            'due_date': None,
                            'modified_date': None,
                            'closed_date': None,
                            'overdue_day': None,
                            'is_control': None,})

    info = {
        "type":res_type,
        "date":res_date,
        "author_id":res_author_id,
        "recipients":recipients
    }

    return info


def get_res_info(item):
    """
    params: item: bs4 object
    get data from resolutions of documents
    """
    res_type = 'Резолюция'
    res_date = item.find('span', attrs={"class": "resolution-item__timestamp"}).text

    match = re.search(r'\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}', res_date)


    if match:
        res_date = match.group()
        res_date = datetime.strptime(res_date, '%d.%m.%Y %H:%M:%S')

    res_author_id = item.find('span', attrs={"class": "resolution-item__author"})\
            .find('span')\
                .get('axuiuserid')


    res_recipients = item.find_all('span', attrs={"class": "to-user-container"})
    recipients = []
    # res_recipients_ids = []
    # res_recipients_texts = []
    # res_recipients_fio = []
    # res_recipients_dates = []
    for recipient in res_recipients:
        recipients.append({'sedo_id': recipient.find('span').get('axuiuserid'),
                            'text': recipient.find('span').text,
                            'fio': get_recipient_fio(recipient.find('span').get('axuiuserid'))})

        # res_recipients_ids.append(recipient.find('span').get('axuiuserid'))
        # res_recipients_texts.append(recipient.find('span').text)

        # Очковый момент, надо проработать на возможные ошибки
        # Вообще это бы все переписать на словарь, а не на списки, но потом
        # res_recipients_fio.append(get_recipient_fio(recipient.find('span').get('axuiuserid')))
        # Конец очкового момента


    dues = item.find('div', attrs={'class': 'resolution-item__orders-wrapper'})
    # print(dues)
    dates = []
    control_group = []
    due_group = []
    if dues is not None:
        # print('11')
        # print(res_recipients_texts)
        if dues.div.div.div is not None:
            # print("______________")
            z = 0
            # print(repr(dues.div.div.div))
            for divs in dues.children:
                # print(repr(divs))
                if not isinstance(divs, Tag):
                        continue
                if divs.div.div is None:
                    tags = divs.div.children
                else:
                    tags = divs.div.div.children
                for tag in tags:
                    z = z + 1
                    # if not isinstance(tag, Tag):
                    #     continue
                    if tag.name == 'strong':
                        text = tag.get_text(strip=True)
                        # print(text)
                        if 'На контроле' in text:
                            current_group = 0
                        elif 'Срок исполнения' in text:
                            current_group = 1
                    elif tag.name == 'br':
                        try:
                            # print(tag.span.text)
                            for fckn_tag in tag.children:
                                # print(repr(fckn_tag))
                                if 'resolution-executor-history' in fckn_tag.get('class', [''])[0]:
                                    man = parse_control_dates(fckn_tag)

                                    if current_group is not None:
                                        # print("!!! - " + str(res_recipients_texts))
                                        if current_group == 0:
                                            for i in range(len(man)):
                                                man[i]['is_control'] = True
                                            # control_group.append(man)
                                            # current_group = None
                                        elif current_group == 1:
                                            for i in range(len(man)):
                                                man[i]['is_control'] = False
                                            # due_group.append(man)
                                            # current_group = None
                                        for m in man:
                                            control_group.append(m)
                                        # current_group = None
                        except Exception as e:
                            print(e)
                    elif tag.name == 'span' and 'resolution-executor-history' in tag.get('class', [''])[0]:

                        man = parse_control_dates(tag)

                        if current_group is not None:
                            # print("!!! - " + str(res_recipients_texts))
                            if current_group == 0:
                                for i in range(len(man)):
                                    man[i]['is_control'] = True
                                # control_group.append(man)
                                # current_group = None
                            elif current_group == 1:
                                for i in range(len(man)):
                                    man[i]['is_control'] = False
                                # due_group.append(man)
                                # current_group = None
                            for m in man:
                                control_group.append(m)
                        # current_group = None
            # print(z)
    
    # Проверим результат
    # str_control_group = ''
    # str_due_group = ''
    # if len(control_group) > 0:
    #     print("🎯 На контроле:")
    #     for span in control_group:
    #         str_control_group = str_control_group + span.get_text(strip=True) + '\n'
    #         print(span.get_text(strip=True))


    # for i in range(len(recipients)):
    #     recipients[i]['due_date'] = None
    #     recipients[i]['modified_date'] = None
    #     recipients[i]['closed_date'] = None
    #     recipients[i]['overdue_day'] = None
    #     recipients[i]['is_control'] = None
    #     for j in range(len(control_group)):
    #         if recipients[i]['fio'] == control_group[j]['person'] and recipients[i]['due_date'] == None:
    #             # recipients[i]['data'] = control_group[j]['person']
    #             recipients[i]['due_date'] = control_group[j]['due_date']
    #             recipients[i]['modified_date'] = control_group[j]['modified_date']
    #             recipients[i]['closed_date'] = control_group[j]['closed_date']
    #             recipients[i]['overdue_day'] = control_group[j]['overdue_day']
    #             recipients[i]['is_control'] = control_group[j]['is_control']
    print(control_group)
    df = pd.DataFrame(recipients)
    df2 = pd.DataFrame(control_group)
    columns = ["person", "due_date", "modified_date", "closed_date", "overdue_day", "is_control"]
    if df2.empty:
        df2 = pd.DataFrame(columns=columns)
        # print(df2)
    df_final = df.merge(df2, how="left", left_on='fio', right_on='person')
    df_final['res_date'] = res_date
    # df.to_excel('test.xlsx')
        # print(recipients[i])
    

    # if len(due_group) > 0:
    #     print("\n📅 Срок исполнения:")
    #     for span in due_group:
    #         str_due_group = str_due_group + span.get_text(strip=True) + '\n'
    #         print(span.get_text(strip=True))


    info = {
        "type":res_type,
        "date":res_date,
        "author_id":res_author_id,
        "recipients": recipients
    }
    print(df_final)
    return df_final
        
        


if __name__ == "__main__":

    with open ('./test_docs/4.html', 'r') as doccard:
        document = BeautifulSoup(doccard, 'html.parser')
    

# Парсим с найденной кодировкой
    # document = BeautifulSoup(raw_data.decode(encoding), 'html.parser')
    resolution_div = document.find('div', attrs={"id": "res-lugs"})\
                                .find('table', attrs={"class": "card s-resolutions-table"})\
                                .find("tbody").find_all('tr')

    parsed_nodes = []

    visible_trs = list(filter(is_visible_tr, resolution_div))
    final_df = pd.DataFrame()
    for tr in visible_trs:
        row_id = tr.get('id')
        dl_attr = tr.get('data-level')
        
        tr_class = tr.get('class')

        node = {"id": row_id, "tag": tr}
        
        if dl_attr is not None:
            try:
                node["dl"] = int(dl_attr)
            except ValueError:
                pass  # Мусорная глубина — игнорировать
        
        execution = tr.get('data-level') is None
        node["execution"] = execution
        df_ex = pd.DataFrame()
        info = {}
        if tr_class:
            if 'rr_fwd' in tr_class:
                info = get_fwd_info(tr)
            elif 'rr1' in tr_class:
                # info = get_res_info(tr)
                df_ex = pd.concat([df_ex, get_res_info(tr)], ignore_index=True)
        df_ex['id'] = row_id
        final_df = pd.concat([final_df, df_ex], ignore_index=True)
        # node['data'] = info

        # trash_marker = False # Маркер для первых нескольких технических строк

        # if (row_id is None) & (len(parsed_nodes) == 0):
        #     trash_marker = True

        # if not trash_marker:
        #     parsed_nodes.append(node)
        
        # trash_marker = False
    final_df.drop_duplicates(inplace=True)
    final_df.to_excel('export.xlsx')
            
    # print_tree(parsed_nodes)



    
    # print(len(parsed_nodes))
