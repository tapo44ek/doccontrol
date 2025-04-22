from bs4 import BeautifulSoup, Tag
import re
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
import sys
import os
from config import ProjectManagementSettings
import pandas as pd
from zoneinfo import ZoneInfo
from config import ProjectManagementSettings
from dateutil.parser import isoparse
import json


def insert_resolutions_into_db(data :list):
    connection = psycopg2.connect(
            host=ProjectManagementSettings.DB_HOST,
            user=ProjectManagementSettings.DB_USER,
            password=ProjectManagementSettings.DB_PASSWORD,
            port=ProjectManagementSettings.DB_PORT,
            database=ProjectManagementSettings.DB_NAME
        )
    cursor = connection.cursor()

    rows = []
    for item in data:
        row = (
            item['id'],
            item.get('parent_id'),
            item['doc_id'],
            item['author_id'],
            isoparse(item['date']),
            item['dl'],
            item['type'],
            json.dumps(item.get('controls', []), ensure_ascii=False),
            json.dumps(item.get('executions', []), ensure_ascii=False),
            json.dumps(item.get('recipients', []), ensure_ascii=False)
        )
        rows.append(row)

    try:
        execute_values(cursor, """
            INSERT INTO public.flat_resolution (
                id, parent_id, doc_id, author_id, date, dl, type,
                controls, executions, recipients
            )
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                parent_id = EXCLUDED.parent_id,
                doc_id = EXCLUDED.doc_id,
                author_id = EXCLUDED.author_id,
                date = EXCLUDED.date,
                dl = EXCLUDED.dl,
                type = EXCLUDED.type,
                controls = EXCLUDED.controls,
                executions = EXCLUDED.executions,
                recipients = EXCLUDED.recipients,
                updated_at = NOW()
        """, rows)

        connection.commit()
        result = 1
        return 1
    except Exception as e:
        result = e
    finally:
        cursor.close()
        connection.close()
    return result


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
            print(f"{indent}[✓ исполнено], info={node.get('data')}")
        else:
            print('\n')
            print(f"{indent}id={nid}, dl={node.get('dl')}, info={node.get('data')} ")

        # Сначала отображаем дочерние элементы
        for child in node.get("children", []):
            print_tree([child], level + 1)

        # Потом — исполнения, если есть
        for exec_note in node.get("executions", []):
            print_tree([exec_note], level + 1)



def build_chain_from_linear_dl(nodes, document_card_id):
    """
    Преобразует линейный список резолюций с полем `dl` в структуру для БД.
    Исполнения встраиваются в executions.
    Возвращает список элементов с parent_id и списком executions.
    """
    result = []
    stack = []  # каждый элемент — (dl, id)

    last_node_by_dl = {}  # для быстрого поиска родителя по dl
    id_to_node = {}

    for node in nodes:
        if not node.get("data"):  # отловит и {}, и None
            continue
        is_exec = node.get("execution", False)

        if is_exec:
            # найдем, к какому элементу цепляться (последний на 1 уровень ниже)
            parent = stack[-1][1] if stack else None
            if parent:
                id_to_node[parent].setdefault("executions", []).append({
                    "author": node.get("data")["author"],
                    "date": node.get("data")["date"],
                    "exec_docs": node.get("data")["exec_docs"],
                    "exec_text": node.get("data")["exec_text"]
                })
            continue

        # обычная резолюция
        nid = node.get("id")
        dl = node.get("dl", 0)

        # определяем родителя
        parent_id = None
        for d, pid in reversed(stack):
            if d < dl:
                parent_id = pid
                break
        # print(node.get("data"))
        entry = {
            "doc_id": document_card_id,
            "id": nid,
            "dl": dl,
            "type": node.get("data")["type"],
            "date": node.get("data")["date"].replace(tzinfo=ZoneInfo("Europe/Moscow")).isoformat(),
            "author_id": int(node.get("data")["author_id"]),
            "recipients": node.get("data")["recipients"],
            "controls": node.get("data")["controls"],
            "parent_id": parent_id,
            "executions": []
        }

        # print("=== ENTRY DEBUG ===")
        # print(entry)
        # print("-------------------")
        result.append(entry)
        id_to_node[nid] = entry

        # обновляем стек
        # убираем все уровни ≥ текущего
        stack = [(d, pid) for d, pid in stack if d < dl]
        stack.append((dl, nid))

    return result
            

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

    for recipient in res_recipients:
        recipients.append({'sedo_id': recipient.find('span').get('axuiuserid'),
                            'text': recipient.find('span').text,
                            'fio': get_recipient_fio(recipient.find('span').get('axuiuserid')),
                            })

    control_group = [{'person': None, 
                      'due_date': None, 
                      'modified_date': None, 
                      'closed_date': None, 
                      'overdue_day': None, 
                      'is_control': False}]
    info = {
        "type": res_type,
        "date": res_date,
        "author_id": res_author_id,
        "recipients": recipients,
        "controls": control_group
    }

    return info


def get_exec_info(item):
    """
    params: item: bs4 object
    get data from forwardings of documents
    """
    res_type = 'Исполнение'
    res_author = item.find('span', attrs={"class": "resolution-item__author"}).text
    res_date = item.find('span', attrs={"class": "resolution-item__timestamp"}).text
    exec_docs = item.find_all('div', attrs={"class": "resolution-item__row"})
    exec_docs_list = []
    for exec_doc in exec_docs:

        if exec_doc.a:
            exec_doc_link = exec_doc.a.get('href')
            match = re.search(r"id=(\d+)", exec_doc_link)
            doc_id = match.group(1) if match else None
            exec_doc_text = exec_doc.a.text.strip()
            exec_docs_list.append({"doc_id": doc_id, "doc_text": exec_doc_text})

    exec_text = item.find('div', attrs={"class": "resolution-item__row resolution-item__row--text"})

    if exec_text:
        exec_text = exec_text.text.strip()
    else:
        exec_text = None

    

    match = re.search(r'\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}', res_date)


    if match:
        res_date = match.group()
        res_date = datetime.strptime(res_date, '%d.%m.%Y %H:%M:%S')


    info = {
        "type": res_type,
        "date": datetime.strftime(res_date, "%d.%m.%Y %H:%M:%S"),
        "author": res_author,
        "exec_text": exec_text,
        "exec_docs": exec_docs_list
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

    for recipient in res_recipients:
        recipients.append({'sedo_id': recipient.find('span').get('axuiuserid'),
                            'text': recipient.find('span').text,
                            'fio': get_recipient_fio(recipient.find('span').get('axuiuserid'))})

    dues = item.find('div', attrs={'class': 'resolution-item__orders-wrapper'})
    dates = []
    control_group = []
    due_group = []
    if dues is not None:

        if dues.div.div.div is not None:
            # z = 0
            for divs in dues.children:

                if not isinstance(divs, Tag):
                        continue
                if divs.div.div is None:
                    tags = divs.div.children
                else:
                    tags = divs.div.div.children
                for tag in tags:
                    # z = z + 1

                    if tag.name == 'strong':
                        text = tag.get_text(strip=True)
                        if 'На контроле' in text:
                            current_group = 0
                        elif 'Срок исполнения' in text:
                            current_group = 1
                    elif tag.name == 'br':
                        try:

                            for fckn_tag in tag.children:

                                if 'resolution-executor-history' in fckn_tag.get('class', [''])[0]:
                                    man = parse_control_dates(fckn_tag)

                                    if current_group is not None:

                                        if current_group == 0:
                                            for i in range(len(man)):
                                                man[i]['is_control'] = True

                                        elif current_group == 1:
                                            for i in range(len(man)):
                                                man[i]['is_control'] = False

                                        for m in man:
                                            control_group.append(m)

                        except Exception as e:
                            print(e)
                    elif tag.name == 'span' and 'resolution-executor-history' in tag.get('class', [''])[0]:

                        man = parse_control_dates(tag)

                        if current_group is not None:

                            if current_group == 0:
                                for i in range(len(man)):
                                    man[i]['is_control'] = True

                            elif current_group == 1:
                                for i in range(len(man)):
                                    man[i]['is_control'] = False

                            for m in man:
                                control_group.append(m)

    # print(control_group)
    if len(control_group) < 1:
        control_group = [{
            "person": None,
            "due_date": None,
            "modified_date": None,
            "closed_date": None,
            "overdue_day": None,
            "is_control": None
        }]
    # df = pd.DataFrame(recipients)
    # df2 = pd.DataFrame(control_group)
    # columns = ["person", "due_date", "modified_date", "closed_date", "overdue_day", "is_control"]
    # if df2.empty:
    #     df2 = pd.DataFrame(columns=columns)
        # print(df2)
    # df_final = df.merge(df2, how="left", left_on='fio', right_on='person')
    # df_final['res_date'] = res_date

    info = {
        "type":res_type,
        "date":res_date,
        "author_id":res_author_id,
        "recipients": recipients,
        "controls": control_group
    }
    # print(df_final)
    return info
        
        
def get_test_tree_from_sample():
    ts = datetime.now()
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
    count = 0
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
                count += 1
            elif 'rr1' in tr_class:
                info = get_res_info(tr)
                count += 1
            elif 'rrr5' in tr_class:
                info = get_exec_info(tr)
        #         df_ex = pd.concat([df_ex, get_res_info(tr)], ignore_index=True)
        # df_ex['id'] = row_id
        # final_df = pd.concat([final_df, df_ex], ignore_index=True)

        node['data'] = info

        trash_marker = False # Маркер для первых нескольких технических строк

        if (row_id is None) & (len(parsed_nodes) == 0):
            trash_marker = True

        if not trash_marker:
            parsed_nodes.append(node)
        
        trash_marker = False
    # final_df.drop_duplicates(inplace=True)
    # final_df.to_excel('export.xlsx')
            
    # print_tree(parsed_nodes)
    from pprint import pprint
    # build_chain_from_linear_dl(parsed_nodes)
    insert_data = build_chain_from_linear_dl(parsed_nodes, 519917990)
    print(count)
    print(insert_resolutions_into_db(insert_data))
    print(f'working time: {datetime.now() - ts}')
    return    


if __name__ == "__main__":
    get_test_tree_from_sample()


