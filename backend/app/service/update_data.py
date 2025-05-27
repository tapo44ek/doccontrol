from repository.doccontrol import DocRepository
from repository.user import UserRepository
from repository.update_data import SedoData
from fastapi import HTTPException
import traceback
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, Tag
import re
import psycopg2
from psycopg2.extras import execute_values
import sys
import os
from core.config import ProjectManagementSettings
import pandas as pd
from zoneinfo import ZoneInfo
from dateutil.parser import isoparse
import json
from pprint import pprint
import requests
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait
import asyncio
import time
from copy import deepcopy


class DataService:
    def __init__(self):
        self.doc_repository = DocRepository()
        self.sedo_data = SedoData()
        self.user_repository = UserRepository()

    def make_search_sogl_data(self, fio, sedo_id):
    # date_from = datetime.strftime(date_from, "%d.%m.%Y")

        params = {
            'check_all_documents': "1",
            'type_0': "1",
            'type_1': "1",
            'type_2': "1",
            'type_3': "1",
            'type_12': "1",
            'type_13': "1",
            'type_4': "1",
            'type_5': "1",
            'check_all_projects': "1",
            'project_type_1': "1",
            'project_type_3': "1",
            'project_type_13': "1",
            'project_type_4': "1",
            'project_type_5': "1",
            'has_period': "1",
            'year_from': "2009",
            'year_to': f"{datetime.now().year}",
            'org_name': 'ДГИгМ',
            'org': "21",
            'order_by': 'cdate',
            'required_text': '',
            'num': '',
            'rdate_f': '',
            'reg_user': '',
            'reg_user_id': '',
            'rdate_t': '',
            'recipient': '',
            'recipient_id': '',
            'recipient_group': '',
            'recipient_group_id': '',
            'in_number': '',
            'bound_number': '',
            'contract_bound_number': '',
            'recipient_org_id': "0",
            'cl_out_num': '',
            'cl_out_date_f': '',
            'cl_out_date_t': '',
            'cl_sign': '',
            'cl_sign_id': '',
            'cl_sign_group': '',
            'cl_sign_group_id': '',
            'cl_executor': '',
            'cl_executor_id': '',
            'cl_executor_group': '',
            'cl_executor_group_id': '',
            'cl_text': '',
            'out_number': '',
            'out_date_f': '',
            'out_reg_user': '',
            'out_reg_user_id': '',
            'out_date_t': '',
            'author': '',
            'author_id': '',
            'author_group': '',
            'author_group_id': '',
            'prepared_by': '',
            'prepared_by_id': '',
            'prepared_by_org_id': "0",
            'curator': '',
            'curator_id': '',
            'short_content': '',
            'document_kind': "0",
            'delivery_type': '',
            'document_special_kind': "0",
            'external_id': '',
            'has_manual_sign': "0",
            'is_hand_shipping': "0",
            'sign_type': "0",
            'is_dsp': "0",
            'is_urgent': "0",
            'creator': '',
            'creator_id': '',
            'memo': '',
            'send_date_f': '',
            'send_date_t': '',
            'info': '',
            'info_author': '',
            'info_author_id': '',
            'info_date_f': '',
            'info_date_t': '',
            'og_file_number': "0",
            'rec_vdelo': "0",
            'vdelo_date_f': '',
            'vdelo_date_t': '',
            'vdelo_prepared': '',
            'vdelo_prepared_id': '',
            'vdelo_signed': '',
            'vdelo_signed_id': '',
            'vdelo_text': '',
            'res_type': "0",
            'res_urgency': "0",
            'resolution_num': '',
            'r_rdate_f': '',
            'resolution_creator': '',
            'resolution_creator_id': '',
            'r_rdate_t': '',
            'resolution_author': '',
            'resolution_author_id': '',
            'resolution_author_group': '',
            'resolution_author_group_id': '',
            'resolution_author_org_id': "0",
            'r_special_control': "0",
            'resolution_behalf': '',
            'resolution_behalf_id': '',
            'resolution_acting_author': '',
            'resolution_acting_author_id': '',
            'resolution_to': '',
            'resolution_to_id': '',
            'resolution_to_group': '',
            'resolution_to_group_id': '',
            'resolution_to_org_id': "0",
            'res_project_letter': "0",
            'res_curator': '',
            'res_curator_id': '',
            'r_control': "0",
            'r_control_f': '',
            'r_control_t': '',
            'r_otv': "0",
            'r_dback': "0",
            'resolution_text': '',
            'r_ef_reason_category_id': "0",
            'r_ef_reason_id': "0",
            'r_is_signed': "0",
            'r_plus': "0",
            'r_another_control': "0",
            'r_oncontrol': "0",
            'r_oncontrol_f': '',
            'r_oncontrol_t': '',
            'unset_control': "0",
            'unset_control_f': '',
            'unset_control_t': '',
            're_date_f': '',
            're_date_t': '',
            're_author': '',
            're_author_id': '',
            're_author_group': '',
            're_author_group_id': '',
            're_acting_author': '',
            're_acting_author_id': '',
            're_is_interim': "-1",
            're_text': '',
            'docs_in_execution': "0",
            're_doc_org_id': '',
            'csdr_initiator': '',
            'csdr_initiator_id': '',
            'csdr_initiator_group': '',
            'csdr_initiator_group_id': '',
            'csdr_start': "0",
            'csdr_stop': "2",
            'csdr_current_version_only': "1",
            'and[csdr][0]': "0",
            'participant_name_0': f'{fio}',
            'participant_name_0_id': f"{sedo_id}",
            'participant_group_0': 'Департамент городского имущества города Москвы',
            'participant_group_0_id': "21",
            'csdr_has_deadline_0': "0",
            'csdr_status_0': "0",
            'csdr_init_date_0_f': '',
            'csdr_init_date_0_t': ''
        }

        return params


    def make_search_doc_data(self, date_from, fio, sedo_id):
        date_from = datetime.strftime(date_from, "%d.%m.%Y")

        params = {
            "check_all_documents": "on",
            "type_0": "1",
            "type_1": "1",
            "type_2": "1",
            "type_3": "1",
            "type_12": "1",
            "type_13": "1",
            "type_4": "1",
            "type_5": "1",
            "has_period": "1",
            "year_from": "2009",
            "year_to": f"{datetime.now().year}",
            "org_name": "ДГИГМ",
            "org": "21",
            "order_by": "default",
            "required_text": "",
            "num": "",
            "rdate_f": "",
            "reg_user": "",
            "reg_user_id": "",
            "rdate_t": "",
            "recipient": "",
            "recipient_id": "",
            "recipient_group": "",
            "recipient_group_id": "",
            "in_number": "",
            "bound_number": "",
            "contract_bound_number": "",
            "recipient_org_id": "0",
            "cl_out_num": "",
            "cl_out_date_f": "",
            "cl_out_date_t": "",
            "cl_sign": "",
            "cl_sign_id": "",
            "cl_sign_group": "",
            "cl_sign_group_id": "",
            "cl_executor": "",
            "cl_executor_id": "",
            "cl_executor_group": "",
            "cl_executor_group_id": "",
            "cl_text": "",
            "out_number": "",
            "out_date_f": "",
            "out_reg_user": "",
            "out_reg_user_id": "",
            "out_date_t": "",
            "author": "",
            "author_id": "",
            "author_group": "",
            "author_group_id": "",
            "prepared_by": "",
            "prepared_by_id": "",
            "prepared_by_org_id": "0",
            "curator": "",
            "curator_id": "",
            "short_content": "",
            "document_kind": "0",
            "delivery_type": "",
            "document_special_kind": "0",
            "external_id": "",
            "has_manual_sign": "0",
            "is_hand_shipping": "0",
            "sign_type": "0",
            "is_dsp": "0",
            "is_control": "0",
            "is_urgent": "0",
            "creator": "",
            "creator_id": "",
            "memo": "",
            "send_date_f": "",
            "send_date_t": "",
            "info": "",
            "info_author": "",
            "info_author_id": "",
            "info_date_f": "",
            "info_date_t": "",
            "og_file_number": "0",
            "rec_vdelo": "0",
            "vdelo_date_f": "",
            "vdelo_date_t": "",
            "vdelo_prepared": "",
            "vdelo_prepared_id": "",
            "vdelo_signed": "",
            "vdelo_signed_id": "",
            "vdelo_text": "",
            "res_type": "0",
            "res_urgency": "0",
            "resolution_num": "",
            "r_rdate_f": f"{date_from}",
            "resolution_creator": "",
            "resolution_creator_id": "",
            "r_rdate_t": "",
            "resolution_author": "",
            "resolution_author_id": "",
            "resolution_author_group": "",
            "resolution_author_group_id": "",
            "resolution_author_org_id": "0",
            "r_special_control": "0",
            "resolution_behalf": "",
            "resolution_behalf_id": "",
            "resolution_acting_author": "",
            "resolution_acting_author_id": "",
            "resolution_to": f"{fio}",
            "resolution_to_id": f"{sedo_id}",
            "resolution_to_group": "Департамент городского имущества города Москвы",
            "resolution_to_group_id": "21",
            "resolution_to_org_id": "0",
            "res_project_letter": "0",
            "res_curator": "",
            "res_curator_id": "",
            "r_control": "0",
            "r_control_f": "",
            "r_control_t": "",
            "r_otv": "0",
            "r_dback": "0",
            "resolution_text": "",
            "r_ef_reason_category_id": "0",
            "r_ef_reason_id": "0",
            "r_is_signed": "0",
            "r_plus": "0",
            "r_another_control": "0",
            "r_oncontrol": "0",
            "r_oncontrol_f": "",
            "r_oncontrol_t": "",
            "unset_control": "0",
            "unset_control_f": "",
            "unset_control_t": "",
            "re_date_f": "",
            "re_date_t": "",
            "re_author": "",
            "re_author_id": "",
            "re_author_group": "",
            "re_author_group_id": "",
            "re_acting_author": "",
            "re_acting_author_id": "",
            "re_is_interim": "-1",
            "re_text": "",
            "docs_in_execution": "0",
            "re_doc_org_id": "",
            "csdr_initiator": "",
            "csdr_initiator_id": "",
            "csdr_initiator_group": "",
            "csdr_initiator_group_id": "",
            "csdr_start": "0",
            "csdr_stop": "0",
            "and[csdr][0]": "0",
            "participant_name_0": "",
            "participant_name_0_id": "",
            "participant_group_0": "",
            "participant_group_0_id": "",
            "csdr_has_deadline_0": "0",
            "csdr_status_0": "0",
            "csdr_init_date_0_f": "",
            "csdr_init_date_0_t": "",
        }

        return params


    def make_search_doc_data_forward(self, date_to, fio, sedo_id):
        date_to = datetime.strftime(date_to, "%d.%m.%Y")
        boss_list = [1558294, 78164285]
        # print(sedo_id)
        if sedo_id in boss_list:
            # print('--------\nnachalnick detected\n------')
            params = {
                "check_all_documents": "on",
                "type_0": "1",
                "type_1": "1",
                "type_2": "1",
                "type_3": "1",
                "type_12": "1",
                "type_13": "1",
                "type_4": "1",
                "type_5": "1",
                "has_period": "1",
                "year_from": "2009",
                "year_to": f"{datetime.now().year}",
                "org_name": "ДГИГМ",
                "org": "21",
                "order_by": "default",
                "required_text": "",
                "num": "",
                "rdate_f": "",
                "reg_user": "",
                "reg_user_id": "",
                "rdate_t": "",
                "recipient": "",
                "recipient_id": "",
                "recipient_group": "",
                "recipient_group_id": "",
                "in_number": "",
                "bound_number": "",
                "contract_bound_number": "",
                "recipient_org_id": "0",
                "cl_out_num": "",
                "cl_out_date_f": "",
                "cl_out_date_t": "",
                "cl_sign": "",
                "cl_sign_id": "",
                "cl_sign_group": "",
                "cl_sign_group_id": "",
                "cl_executor": "",
                "cl_executor_id": "",
                "cl_executor_group": "",
                "cl_executor_group_id": "",
                "cl_text": "",
                "out_number": "",
                "out_date_f": "",
                "out_reg_user": "",
                "out_reg_user_id": "",
                "out_date_t": "",
                "author": "",
                "author_id": "",
                "author_group": "",
                "author_group_id": "",
                "prepared_by": "",
                "prepared_by_id": "",
                "prepared_by_org_id": "0",
                "curator": "",
                "curator_id": "",
                "short_content": "",
                "document_kind": "0",
                "delivery_type": "",
                "document_special_kind": "0",
                "external_id": "",
                "has_manual_sign": "0",
                "is_hand_shipping": "0",
                "sign_type": "0",
                "is_dsp": "0",
                "is_control": "0",
                "is_urgent": "0",
                "creator": "",
                "creator_id": "",
                "memo": "",
                "send_date_f": "",
                "send_date_t": "",
                "info": "",
                "info_author": "",
                "info_author_id": "",
                "info_date_f": "",
                "info_date_t": "",
                "og_file_number": "0",
                "rec_vdelo": "0",
                "vdelo_date_f": "",
                "vdelo_date_t": "",
                "vdelo_prepared": "",
                "vdelo_prepared_id": "",
                "vdelo_signed": "",
                "vdelo_signed_id": "",
                "vdelo_text": "",
                "res_type": "0",
                "res_urgency": "0",
                "resolution_num": "",
                "r_rdate_f": "",
                "resolution_creator": "",
                "resolution_creator_id": "",
                "r_rdate_t": "",
                "resolution_author": "",
                "resolution_author_id": "",
                "resolution_author_group": "",
                "resolution_author_group_id": "",
                "resolution_author_org_id": "0",
                "r_special_control": "0",
                "resolution_behalf": "",
                "resolution_behalf_id": "",
                "resolution_acting_author": "",
                "resolution_acting_author_id": "",
                "resolution_to": f"{fio}",
                "resolution_to_id": f"{sedo_id}",
                "resolution_to_group": "Департамент городского имущества города Москвы",
                "resolution_to_group_id": "21",
                "resolution_to_org_id": "0",
                "res_project_letter": "0",
                "res_curator": "",
                "res_curator_id": "",
                "r_control": "2",
                "r_control_f": "",
                "r_control_t": f"{date_to}",
                "r_otv": "0",
                "r_dback": "0",
                "resolution_text": "",
                "r_ef_reason_category_id": "0",
                "r_ef_reason_id": "0",
                "r_is_signed": "0",
                "r_plus": "0",
                "r_another_control": "0",
                "r_oncontrol": "2",
                "r_oncontrol_f": "",
                "r_oncontrol_t": f"{date_to}",
                "unset_control": "0",
                "unset_control_f": "",
                "unset_control_t": "",
                "re_date_f": "",
                "re_date_t": "",
                "re_author": "",
                "re_author_id": "",
                "re_author_group": "",
                "re_author_group_id": "",
                "re_acting_author": "",
                "re_acting_author_id": "",
                "re_is_interim": "-1",
                "re_text": "",
                "docs_in_execution": "0",
                "re_doc_org_id": "",
                "csdr_initiator": "",
                "csdr_initiator_id": "",
                "csdr_initiator_group": "",
                "csdr_initiator_group_id": "",
                "csdr_start": "0",
                "csdr_stop": "0",
                "and[csdr][0]": "0",
                "participant_name_0": "",
                "participant_name_0_id": "",
                "participant_group_0": "",
                "participant_group_0_id": "",
                "csdr_has_deadline_0": "0",
                "csdr_status_0": "0",
                "csdr_init_date_0_f": "",
                "csdr_init_date_0_t": "",
            }
        else:
            params = {
                "check_all_documents": "on",
                "type_0": "1",
                "type_1": "1",
                "type_2": "1",
                "type_3": "1",
                "type_12": "1",
                "type_13": "1",
                "type_4": "1",
                "type_5": "1",
                "has_period": "1",
                "year_from": "2009",
                "year_to": f"{datetime.now().year}",
                "org_name": "ДГИГМ",
                "org": "21",
                "order_by": "default",
                "required_text": "",
                "num": "",
                "rdate_f": "",
                "reg_user": "",
                "reg_user_id": "",
                "rdate_t": "",
                "recipient": "",
                "recipient_id": "",
                "recipient_group": "",
                "recipient_group_id": "",
                "in_number": "",
                "bound_number": "",
                "contract_bound_number": "",
                "recipient_org_id": "0",
                "cl_out_num": "",
                "cl_out_date_f": "",
                "cl_out_date_t": "",
                "cl_sign": "",
                "cl_sign_id": "",
                "cl_sign_group": "",
                "cl_sign_group_id": "",
                "cl_executor": "",
                "cl_executor_id": "",
                "cl_executor_group": "",
                "cl_executor_group_id": "",
                "cl_text": "",
                "out_number": "",
                "out_date_f": "",
                "out_reg_user": "",
                "out_reg_user_id": "",
                "out_date_t": "",
                "author": "",
                "author_id": "",
                "author_group": "",
                "author_group_id": "",
                "prepared_by": "",
                "prepared_by_id": "",
                "prepared_by_org_id": "0",
                "curator": "",
                "curator_id": "",
                "short_content": "",
                "document_kind": "0",
                "delivery_type": "",
                "document_special_kind": "0",
                "external_id": "",
                "has_manual_sign": "0",
                "is_hand_shipping": "0",
                "sign_type": "0",
                "is_dsp": "0",
                "is_control": "0",
                "is_urgent": "0",
                "creator": "",
                "creator_id": "",
                "memo": "",
                "send_date_f": "",
                "send_date_t": "",
                "info": "",
                "info_author": "",
                "info_author_id": "",
                "info_date_f": "",
                "info_date_t": "",
                "og_file_number": "0",
                "rec_vdelo": "0",
                "vdelo_date_f": "",
                "vdelo_date_t": "",
                "vdelo_prepared": "",
                "vdelo_prepared_id": "",
                "vdelo_signed": "",
                "vdelo_signed_id": "",
                "vdelo_text": "",
                "res_type": "0",
                "res_urgency": "0",
                "resolution_num": "",
                "r_rdate_f": "",
                "resolution_creator": "",
                "resolution_creator_id": "",
                "r_rdate_t": "",
                "resolution_author": "",
                "resolution_author_id": "",
                "resolution_author_group": "",
                "resolution_author_group_id": "",
                "resolution_author_org_id": "0",
                "r_special_control": "0",
                "resolution_behalf": "",
                "resolution_behalf_id": "",
                "resolution_acting_author": "",
                "resolution_acting_author_id": "",
                "resolution_to": f"{fio}",
                "resolution_to_id": f"{sedo_id}",
                "resolution_to_group": "Департамент городского имущества города Москвы",
                "resolution_to_group_id": "21",
                "resolution_to_org_id": "0",
                "res_project_letter": "0",
                "res_curator": "",
                "res_curator_id": "",
                "r_control": "2",
                "r_control_f": "",
                "r_control_t": f"{date_to}",
                "r_otv": "0",
                "r_dback": "0",
                "resolution_text": "",
                "r_ef_reason_category_id": "0",
                "r_ef_reason_id": "0",
                "r_is_signed": "0",
                "r_plus": "0",
                "r_another_control": "0",
                "r_oncontrol": "0",
                "r_oncontrol_f": "",
                "r_oncontrol_t": "",
                "unset_control": "0",
                "unset_control_f": "",
                "unset_control_t": "",
                "re_date_f": "",
                "re_date_t": "",
                "re_author": "",
                "re_author_id": "",
                "re_author_group": "",
                "re_author_group_id": "",
                "re_acting_author": "",
                "re_acting_author_id": "",
                "re_is_interim": "-1",
                "re_text": "",
                "docs_in_execution": "0",
                "re_doc_org_id": "",
                "csdr_initiator": "",
                "csdr_initiator_id": "",
                "csdr_initiator_group": "",
                "csdr_initiator_group_id": "",
                "csdr_start": "0",
                "csdr_stop": "0",
                "and[csdr][0]": "0",
                "participant_name_0": "",
                "participant_name_0_id": "",
                "participant_group_0": "",
                "participant_group_0_id": "",
                "csdr_has_deadline_0": "0",
                "csdr_status_0": "0",
                "csdr_init_date_0_f": "",
                "csdr_init_date_0_t": "",
            }

        return params

    def get_session(self):
    
        s = requests.Session()

        data = {"DNSID": 'wWKtfVYPrUwz4estPdKE9sA',
                "group_id": "21",
                "login": ProjectManagementSettings.SEDO_LOG,
                "user_id": "80742170",
                "password": ProjectManagementSettings.SEDO_PASS,
                "token": "",
                "x": "1"}

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Connection': 'keep-alive', }

        url_auth = 'https://mosedo.mos.ru/auth.php?group_id=21'

        r = s.post(url_auth, data=data, headers=headers, allow_redirects=False)

        DNSID = r.headers['location'].split('DNSID=')[1]

        return s, DNSID

    def parse_control_dates(self, span):
        """
        get span with control date/dates for a man or a group of people (bs4 object)
        returns ....
        """

        pattern = (
            r'^(.*?)\s+-\s+срок:\s+(\d{2}\.\d{2}\.\d{4})'
            r'(?:\s+-\s+изменен:\s+(\d{2}\.\d{2}\.\d{4}))?'
            r'(?:\s+-\s+снят с контроля:\s+(\d{2}\.\d{2}\.\d{4}))?'
            r'(?:\s+-\s+просрочено\s+(\d+)\s+(?:день|дня|дней))?'
            r'(?:\s+-\s+(?:осталось\s+\d+\s+(?:день|дня|дней)|сегодня))?'
            r'(?:\s+-\s+на докладе)?$'
        )
        # print(span.get_text())
        people = span.get_text().split('\n')
        result = []
        for man in people:
            if man == '':
                continue
            cleaned = re.sub(r'[\xa0\u202f\u2009]', ' ', man.strip())
            match = re.match(pattern, cleaned)

            if match:
                person = match.group(1)
                due_date = match.group(2)
                modified_date = match.group(3) or None
                closed_date = match.group(4) or None
                overdue_days = int(match.group(5)) if match.group(5) else None

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

    def is_visible_tr(self, tr):
        '''
        keeps only elements without display:none
        '''

        style = tr.get('style', '') or ''
        return 'display:none' not in style.replace(' ', '').lower()

    def build_chain_from_linear_dl(self, nodes, document_card_id):
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
                "author_id": node.get("data")["author_id"],
                "recipients": node.get("data")["recipients"],
                "controls": node.get("data")["controls"],
                "parent_id": parent_id,
                "executions": []
            }

            result.append(entry)
            id_to_node[nid] = entry

            # обновляем стек
            # убираем все уровни ≥ текущего
            stack = [(d, pid) for d, pid in stack if d < dl]
            stack.append((dl, nid))

        return result
                

    def get_fwd_info(self, item):
        userrepository = UserRepository()
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
                                'fio': userrepository.no_pool_get_user_fio_by_sedo_id(recipient.find('span').get('axuiuserid')),
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


    def get_resolution_project_info(self, item):
        """
        params: item: bs4 object
        get data from forwardings of documents
        """
        userrepository = UserRepository()
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
                                'fio': userrepository.no_pool_get_user_fio_by_sedo_id(recipient.find('span').get('axuiuserid')),
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


    def get_exec_info(self, item):
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


    def get_res_info(self, item):
        """
        params: item: bs4 object
        get data from resolutions of documents
        """
        userrepository = UserRepository()
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
                                'fio': userrepository.no_pool_get_user_fio_by_sedo_id(recipient.find('span').get('axuiuserid'))})

        dues = item.find('div', attrs={'class': 'resolution-item__orders-wrapper'})
        dates = []
        control_group = []
        due_group = []
        if dues is not None:

            if dues.div.div is not None:
                # z = 0
                for divs in dues.children:

                    if not isinstance(divs, Tag):
                            continue
                    if divs.div is None:
                        print(f'!!!!!\n\n!!!!!!\n{divs}\n!!!!!\n')
                        continue
                    if divs.div.div is None:
                        tags = divs.div.children
                    else:
                        tags = divs.div.div.children
                    for tag in tags:
                        # print(tag)
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
                                    # print(fckn_tag)
                                    # print(f"current type is {current_group}")
                                    # print(f"current = {control_group}")
                                    if tag.name == "br":
                                        try:
                                            for blyat_tag in fckn_tag.children:
                                                if tag.name == "br":
                                                    # print(tag)
                                                    try:
                                                        for blyat_blyat_tag in blyat_tag.children:
                                                            if not isinstance(blyat_blyat_tag, Tag):
                                                                continue
                                                            if 'resolution-executor-history' in blyat_blyat_tag.get('class', [''])[0]:
                                                                man = parse_control_dates(blyat_blyat_tag)

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
                                                        pass

                                                if not isinstance(blyat_tag, Tag):
                                                    continue
                                                if 'resolution-executor-history' in blyat_tag.get('class', [''])[0]:
                                                    man = self.parse_control_dates(blyat_tag)

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
                                    if 'resolution-executor-history' in fckn_tag.get('class', [''])[0]:
                                        man = self.parse_control_dates(fckn_tag)

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

                            man = self.parse_control_dates(tag)

                            if current_group is not None:

                                if current_group == 0:
                                    for i in range(len(man)):
                                        man[i]['is_control'] = True

                                elif current_group == 1:
                                    for i in range(len(man)):
                                        man[i]['is_control'] = False

                                for m in man:
                                    control_group.append(m)
            # elif dues.div.div is not None:
            #     print(dues)

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

        info = {
            "type":res_type,
            "date":res_date,
            "author_id":res_author_id,
            "recipients": recipients,
            "controls": control_group
        }
        # print(df_final)
        return info


    def get_doc_info_test(self, document, doc_id):
        # print(f'doc info start for {doc_id}')
        # with open ('./test_docs/4.html', 'r') as doccard:
        #     document = BeautifulSoup(doccard, 'html.parser')
        doccard_table = document.find('table', attrs={"id": "maintable"})
        if doccard_table is None:
            print('!!!!!! \n', doc_id, '\n !!!!!!!')
            return 0
        answer_result = []
        recipients = []
        result = {
        "sedo_id": doc_id,
        "dgi_number": '',
        "date": '',
        "signed_by_id": None,
        "signed_by_fio": '',
        "signed_by_company": '',
        "executor_id": None,
        "executor_fio": '',
        "executor_company": '',
        "recipients": recipients,
        "answer": answer_result,
        "description": ''
        }

        element = doccard_table.find_all('td', attrs={"data-tour":"1"}) # Номер документа 12

        for item in element:
            try:
                result["dgi_number"] = item.find('span', attrs={"class": "main-document-field"}).text.strip()
            except Exception as e: pass
        
        if result["dgi_number"] == '':
            element = doccard_table.find_all('td', attrs={"data-tour":"12"}) # Номер документа 12

            for item in element:
                try:
                    result["dgi_number"] = item.find('span', attrs={"class": "main-document-field"}).text.strip()
                except Exception as e: pass
        
        element = doccard_table.find_all('td', attrs={"data-tour":"2"}) # Дата документа 13
        for item in element:
            try:
                result["date"] = item.find('span', attrs={"class": "main-document-field"}).text.strip()
            except Exception as e: pass

        if result['date'] == '':
            element = doccard_table.find_all('td', attrs={"data-tour":"13"}) # Дата документа 13
            for item in element:
                try:
                    result["date"] = item.find('span', attrs={"class": "main-document-field"}).text.strip()
                except Exception as e: pass

        element = doccard_table.find_all('td', attrs={"data-tour":"14"}) # Подпись

        for item in element:
            try:
                result["signed_by_id"] = item.find('span').get('axuiuserid')
                result["signed_by_fio"] = item.find('span').strong.text.strip()
                company = item.find('span').text.strip()
                match = re.findall(r'\((.*?)\)', company)
                if match:
                    if "не направлять" not in match[0]:
                        result["signed_by_company"] = match[0] # выводит: первый
                    else:
                        try:
                            result["signed_by_company"] = match[1]
                        except:
                            result["signed_by_company"] = 'Not Found'
            except Exception as e: pass

        element = doccard_table.find_all('td', attrs={"data-tour":"15"}) # Исполнитель

        for item in element:
            try:
                result["executor_id"] = item.find('span').get('axuiuserid')
                result["executor_fio"] = item.find('span').b.text.strip()
                company = item.find('span').text.strip()
                match = re.findall(r'\((.*?)\)', company)
                if match:
                    if "не направлять" not in match[0]:
                        result["executor_company"] = match[0] # выводит: первый
                    else:
                        try:
                            result["executor_company"] = match[1]
                        except:
                            result["executor_company"] = 'Not Found'
            except Exception as e: pass

        element = doccard_table.find_all('td', attrs={"data-tour":"5"}) # На №

        for item in element:
            try:
                answers = item.find_all('a')
                prev_answer_id = 0
                if answers:
                    for answer in answers:
                        # print(answer)
                        answer_id = answer.get('href')
                        match = re.search(r"id=(\d+)", answer_id)
                        answer_id = match.group(1) if match else None
                        answer_text = answer.text.strip()
                        if prev_answer_id != answer_id:
                            answer_result.append({"answer_id": answer_id, "answer_text": answer_text})
                        prev_answer_id = answer_id
            except Exception as e: pass
                        
        element = doccard_table.find_all('td', attrs={"colspan": "3", "class": "td-1 highlightable b_new"})

        for item in element:
            if item.find('span').get('axuiuserid'):
                rec_id = item.find('span').get('axuiuserid')
                rec_fio = item.find('span').strong.text.strip()
                company = item.find('span').text.strip()
                match = re.findall(r'\((.*?)\)', company)
                if match:
                    if "не направлять" not in match[0]:
                        rec_company = match[0] # выводит: первый
                    else:
                        try:
                            rec_company = match[1]
                        except:
                            rec_company = 'Not Found'
                recipients.append({"sedo_id": rec_id, "fio": rec_fio, "company": rec_company})

        try:
            result["description"] = doccard_table.find('td',
                                        attrs={"data-tour":"20",
                                        "class": "highlightable card-annotation-short-content b3"})\
                                        .text.strip() # Краткое содержание
        except Exception as e: pass
        sedodata = SedoData()
        res = sedodata.insert_documents_into_db(result)

        return res

            
    def get_test_tree_from_sample(self, document, doc_id):

        ts = datetime.now()
        try:
            resolution_div = document.find('div', attrs={"id": "res-lugs"})\
                                        .find('table', attrs={"class": "card s-resolutions-table"})\
                                        .find("tbody").find_all('tr')
        except Exception as e:
            print('!!!!!! \n', doc_id, '\n!!!!!!!\n', e)
            return 0

        parsed_nodes = []

        visible_trs = list(filter(self.is_visible_tr, resolution_div))
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
                    info = self.get_fwd_info(tr)
                    count += 1
                elif 'rrr2' in tr_class:
                    info = self.get_resolution_project_info(tr)
                    count += 1
                elif 'rr1' in tr_class:
                    info = self.get_res_info(tr)
                    count += 1
                elif 'rrr5' in tr_class:
                    info = self.get_exec_info(tr)

            node['data'] = info

            trash_marker = False # Маркер для первых нескольких технических строк

            if (row_id is None) & (len(parsed_nodes) == 0):
                trash_marker = True

            if not trash_marker:
                parsed_nodes.append(node)
            
            trash_marker = False

        insert_data = self.build_chain_from_linear_dl(parsed_nodes, doc_id)
        sedodata = SedoData()
        res = sedodata.insert_resolutions_into_db(insert_data)

        return res


    def get_doc_ids(self, date_from, date_to, fio, sedo_id, session, DNSID):
        

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Connection': 'keep-alive',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document'
        }
        data = self.make_search_doc_data(date_from, fio, sedo_id)
        data_forward = self.make_search_doc_data_forward(date_to, fio, sedo_id)
        url_search = f'https://mosedo.mos.ru/document_search.php?new=0&DNSID={DNSID}'
        r2 = session.post(url_search, data=data, headers=headers)
        first_soup = BeautifulSoup(r2.text, 'html.parser')

        try:
            count_doc = int(first_soup.find('span', class_='search-export__count').text.split(': ')[1])
        except: count_doc = 1
        count_pages = count_doc // 15 + 3
        
        all_pages = range(2, count_pages)  # страницы 2–153 включительно



        doc_ids = []
        docs_ids_soap = first_soup.find('table', attrs={"id": "mtable"}).tbody.find_all('tr')
        for docs in docs_ids_soap:
            try:
                doc_ids.append(docs.get('data-docid'))
            except: pass

        def worker(page):
            return self.process_doc_ids(session, DNSID, headers, page)

        with ThreadPoolExecutor(max_workers=75) as executor:
            results = list(executor.map(worker, all_pages))



        # Склеиваем списки в один
        flat_doc_ids = sum(results, [])
        print (count_pages)
        doc_ids = doc_ids + flat_doc_ids


        r2 = session.post(url_search, data=data_forward, headers=headers)


        # with open("./test_docs/res_2.html", "w") as f:
        #     f.write(r2.text)
        # print(r2.text)
        first_soup = BeautifulSoup(r2.text, 'html.parser')

        try:
            count_doc = int(first_soup.find('span', class_='search-export__count').text.split(': ')[1])
        except: count_doc = 1
        count_pages = count_doc // 15 + 3
        
        all_pages = range(2, count_pages) 
        print(all_pages) # страницы 2–153 включительно


        docs_ids_soap = first_soup.find('table', attrs={"id": "mtable"}).tbody.find_all('tr')
        for docs in docs_ids_soap:
            try:
                doc_ids.append(docs.get('data-docid'))
            except: pass

        def worker(page):
            return self.process_doc_ids(session, DNSID, headers, page)

        with ThreadPoolExecutor(max_workers=75) as executor:
            results = list(executor.map(worker, all_pages))



        # Склеиваем списки в один
        flat_doc_ids = sum(results, [])
        print (count_pages)
        doc_ids = doc_ids + flat_doc_ids
        print(len(doc_ids))


        doc_ids = list(dict.fromkeys(doc_ids))
        print(len(doc_ids))
        return doc_ids

    def get_sogl_ids(self, fio, sedo_id, session, DNSID):
        

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Connection': 'keep-alive',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document'
        }
        data = self.make_search_sogl_data(fio, sedo_id)
        url_search = f'https://mosedo.mos.ru/document_search.php?new=0&DNSID={DNSID}'
        r2 = session.post(url_search, data=data, headers=headers)
        first_soup = BeautifulSoup(r2.text, 'html.parser')

        try:
            count_doc = int(first_soup.find('span', class_='search-export__count').text.split(': ')[1])
        except: count_doc = 1
        count_pages = count_doc // 15 + 3
        
        all_pages = range(2, count_pages)  # страницы 2–153 включительно



        doc_ids = []
        docs_ids_soap = first_soup.find('table', attrs={"id": "mtable"}).tbody.find_all('tr')
        for docs in docs_ids_soap:
            try:
                doc_ids.append(docs.get('data-docid'))
            except: pass

        def worker(page):
            return self.process_doc_ids(session, DNSID, headers, page)

        with ThreadPoolExecutor(max_workers=75) as executor:
            results = list(executor.map(worker, all_pages))



        # Склеиваем списки в один
        flat_doc_ids = sum(results, [])
        print (count_pages)
        doc_ids = doc_ids + flat_doc_ids

        return doc_ids


    def process_doc_ids(self, session, DNSID, headers, page):
        response = session.get(f'https://mosedo.mos.ru/document.php?perform_search=1&DNSID={DNSID}&page={page}', headers=headers)
        first_soup = BeautifulSoup(response.text, 'html.parser')
        doc_ids = []
        try:
            docs_ids_soap = first_soup.find('table', attrs={"id": "mtable"}).tbody.find_all('tr')
        except:
            with open("./test_docs/res_33.html", "w") as f:
                f.write(response.text)
            print(response.status_code)
            print(page)
            exit()

        for docs in docs_ids_soap:
            try:
                doc_ids.append(docs.get('data-docid'))
            except: pass

        doc_ids = [x for x in doc_ids if x is not None]
        return doc_ids

    def process_sogl(self, session, doc_id, DNSID):
        with ThreadPoolExecutor(max_workers=2) as executor:
            response = session.get(f'https://mosedo.mos.ru/document.card.php?id={doc_id}&DNSID={DNSID}').text
            bs = BeautifulSoup(response, 'html.parser')
            future1 = executor.submit(self.get_sogl_info, bs, doc_id)
            wait([future1])
            sogl_result = future1.result()

        return f'sogl insert = {sogl_result}'

    def process_doc(self, session, doc_id, DNSID):
        with ThreadPoolExecutor(max_workers=2) as executor:
            response = session.get(f'https://mosedo.mos.ru/document.card.php?id={doc_id}&DNSID={DNSID}').text
            bs = BeautifulSoup(response, 'html.parser')
            future1 = executor.submit(self.get_doc_info_test, bs, doc_id)
            future2 = executor.submit(self.get_test_tree_from_sample, bs, doc_id)
            wait([future1, future2])
            doc_result = future1.result()
            res_result = future2.result()

        return f'doc insert = {doc_result}, res_insert = {res_result}'

    def get_sogl_info(self, document, doc_id):
    # with open (path, 'r') as doccard:
    #     document = BeautifulSoup(doccard, 'html.parser')

        doccard_table = document.find('table', attrs={"class": "card maintable-width scrollable-section"})
        if not doccard_table:
            print('error')
            return

        answer_result = []
        recipients = []
        result = {
        "sedo_id": doc_id,
        "dgi_number": '',
        "date": '',
        "signed_by_id": None,
        "signed_by_fio": '',
        "signed_by_company": '',
        "executor_id": None,
        "executor_fio": '',
        "executor_company": '',
        "recipients": recipients,
        "answer": answer_result,
        "description": '',
        'registered_id': None,
        'registered_number': None
        }
        registered_number = None
        registered_id = None
        number = None
        date = None
        author_id = None
        response_on_result = []
        recipient = None
        description = None


        ## Номер регистрации
        reg_num_soup = document.find('a', attrs={"class": "s-agree-subcomment__link"})
        if reg_num_soup:
            print(reg_num_soup)
            print(type(reg_num_soup))
            result['registered_number'] = reg_num_soup.text.strip()
            registered_id = reg_num_soup.get('href')
            match = re.search(r"id=(\d+)", registered_id)
            result['registered_id'] = int(match.group(1)) if match else None      


        element = doccard_table.find_all('td', attrs={"data-tour":"1"}) # Номер документа 12

        for item in element:
            try:
                result["dgi_number"] = item.find('span', attrs={"class": "main-document-field"}).text.strip()
            except Exception as e: pass
        
        if result["dgi_number"] == '':
            element = doccard_table.find_all('td', attrs={"data-tour":"12"}) # Номер документа 12

            for item in element:
                try:
                    result["dgi_number"] = item.find('span', attrs={"class": "main-document-field"}).text.strip()
                except Exception as e: pass
        
        element = doccard_table.find_all('td', attrs={"data-tour":"2"}) # Дата документа 13
        for item in element:
            try:
                result["date"] = item.find('span', attrs={"class": "main-document-field"}).text.strip()
            except Exception as e: pass

        if result['date'] == '':
            element = doccard_table.find_all('td', attrs={"data-tour":"13"}) # Дата документа 13
            for item in element:
                try:
                    result["date"] = item.find('span', attrs={"class": "main-document-field"}).text.strip()
                except Exception as e: pass
        # ## Номер согла
        # number_soup = doccard_table.find('td', attrs={"data-tour":"1"}) # Номер документа 1
        # if number_soup:
        #     el = number_soup.find('span', attrs={"class": "main-document-field"})
        #     result['number'] = el.text.strip() if el else None
        # else:
        #     number_soup = doccard_table.find('td', attrs={"data-tour":"12"}) # Номер документа 12
        #     if number_soup:
        #         el = number_soup.find('span', attrs={"class": "main-document-field"})
        #         result['number'] = el.text.strip() if el else None


        # ## Дата согла
        # date_soup = doccard_table.find('td', attrs={"data-tour":"2"}) # Дата документа 13
        # if date_soup:
        #     el = date_soup.find('span', attrs={"class": "main-document-field"})
        #     result['date'] = el.text.strip() if el else None
        # else:
        #     date_soup = doccard_table.find('td', attrs={"data-tour":"13"}) # Дата документа 13
        #     if date_soup:
        #         el = date_soup.find('span', attrs={"class": "main-document-field"})
        #         result['date'] = el.text.strip() if el else None

    ####################
        element = doccard_table.find_all('td', attrs={"data-tour":"14"}) # Подпись
        for item in element:
            try:
                result["signed_by_id"] = int(item.find('span').get('axuiuserid'))
                result["signed_by_fio"] = item.find('span').strong.text.strip()
                company = item.find('span').text.strip()
                match = re.findall(r'\((.*?)\)', company)
                if match:
                    if "не направлять" not in match[0]:
                        result["signed_by_company"] = match[0] # выводит: первый
                    else:
                        try:
                            result["signed_by_company"] = match[1]
                        except:
                            result["signed_by_company"] = 'Not Found'
            except Exception as e: pass

        element = doccard_table.find_all('td', attrs={"data-tour":"15"}) # Исполнитель

        for item in element:
            try:
                result["executor_id"] = int(item.find('span').get('axuiuserid'))
                result["executor_fio"] = item.find('span').b.text.strip()
                company = item.find('span').text.strip()
                match = re.findall(r'\((.*?)\)', company)
                if match:
                    if "не направлять" not in match[0]:
                        result["executor_company"] = match[0] # выводит: первый
                    else:
                        try:
                            result["executor_company"] = match[1]
                        except:
                            result["executor_company"] = 'Not Found'
            except Exception as e: pass

        element = doccard_table.find_all('td', attrs={"data-tour":"5"}) # На №

        for item in element:
            try:
                answers = item.find_all('a')
                prev_answer_id = 0
                if answers:
                    for answer in answers:
                        # print(answer)
                        answer_id = answer.get('href')
                        match = re.search(r"id=(\d+)", answer_id)
                        answer_id = int(match.group(1)) if match else None
                        answer_text = answer.text.strip()
                        if prev_answer_id != answer_id:
                            answer_result.append({"answer_id": answer_id, "answer_text": answer_text})
                        prev_answer_id = answer_id
            except Exception as e: pass

        element = doccard_table.find_all('td', attrs={"colspan": "3", "class": "td-1 highlightable b_new"})

        for item in element:
            if item.find('span').get('axuiuserid'):
                rec_id = item.find('span').get('axuiuserid')
                rec_fio = item.find('span').strong.text.strip()
                company = item.find('span').text.strip()
                match = re.findall(r'\((.*?)\)', company)
                if match:
                    if "не направлять" not in match[0]:
                        rec_company = match[0] # выводит: первый
                    else:
                        try:
                            rec_company = match[1]
                        except:
                            rec_company = 'Not Found'
                recipients.append({"sedo_id": int(rec_id), "fio": rec_fio, "company": rec_company})

        try:
            result["description"] = doccard_table.find('td',
                                        attrs={"data-tour":"20",
                                        "class": "highlightable card-annotation-short-content b3"})\
                                        .text.strip() # Краткое содержание
        except Exception as e: pass

        try:
            result['started_at'] = document.find('table', attrs={'class': 's-agree-comment__table'}).find_all('tr')[2].find_all('td')[1].text.strip()
        except Exception as e:
            print(e)

        result['structure'] = self.parse_sogl_structure(document)

        sedodata = SedoData()
        result = sedodata.insert_sogly_into_db(result)
        # pprint(result)
        return result
    ####################


    def merge_redirect_status_to_previous(self, data):
        result = []
        last_redirected = {}  # (dl, sedo_id) → индекс перенаправленного элемента

        for item in data:
            key = (item["dl"], item["sedo_id"])

            if key in last_redirected and item["status"] != "Перенаправлено":
                prev_idx = last_redirected[key]
                result[prev_idx]["status_after_redirect"] = item["status"]
                result[prev_idx]["date_after_redirect"] = item["date"]
                # не добавляем текущий
            else:
                result.append(deepcopy(item))

                # сохраняем в last_redirected ТОЛЬКО если статус == Перенаправлено
                if item["status"] == "Перенаправлено":
                    last_redirected[key] = len(result) - 1

        return result

    def build_sogl_tree(self, flat_list):
        tree = []
        stack = []

        for item in flat_list:
            node = deepcopy(item)
            node["z_children"] = []

            dl = node["dl"]

            if dl == 0:
                tree.append(node)
                stack = [node]
            else:
                # Найдём родителя на уровень выше
                if dl <= len(stack) - 1:
                    stack = stack[:dl]  # обрезаем стек до нужной глубины

                parent = stack[dl - 1]
                parent["z_children"].append(node)

                if len(stack) > dl:
                    stack[dl] = node
                else:
                    stack.append(node)

        return tree


    def parse_sogl_structure(self, document):
        # with open (path, 'r') as doccard:
        #     document = BeautifulSoup(doccard, 'html.parser')
        chain = {}
        sogl_type = None
        dl = 0

        number = None
        fio = None
        status = None
        date = None
        duration = None


        sogl_table = document.find('tbody', attrs={"class": "agreetable__tbody"})
        trs = sogl_table.find_all('tr')
        nodes = []
        row = {}
        for i in range(len(trs)):
            # if fio == 'Нестеренко А.И.':
            #     print(trs[i])
            # print(tr.get('class'))
            if any(cls in trs[i].get('class', []) for cls in ['agreetable__head', 'agreetable-head']):
                chain[dl] = trs[i].td.div.span.strong.text
                continue
            
            if any(cls in trs[i].get('class', []) for cls in ['agreetable__tr--redirect']):
                redirect = trs[i].find('td', attrs={"class": "agreetable__subhead"}).find('div', attrs={"class": "agreetable__redirect agreetable-redirect"})
                if redirect.find('div', attrs={"class": "agreetable-redirect__title"}).text.strip() == "Перенаправление":
                    dl = dl + 1
                    sogl_type = redirect.find('div', attrs={"class": "agreetable-redirect__csdr-type"}).span.text.strip()
                    chain[dl] = sogl_type
                    continue
            
            if i != len(trs)-1:
                # print(i)
                # print(len(trs))
                if any(cls in trs[i].get('class', []) for cls in ['agreetable__tr--first-level', 'agreetable__tr']) and not any(cls in trs[i].get('class', []) for cls in ['agreetable__redirect', 'agreetable-redirect', 'agreetable__head', 'agreetable-head']):
                    # print('in if')
                    tds = trs[i].find_all('td')
                    number = tds[0].text.strip()
                    fio = tds[1].span.text.strip().split('\n')[0]
                    status = tds[3].text.strip()
                    lines = [line.strip() for line in tds[3].span.stripped_strings]
                    status = lines[0]  # "Перенаправлено"
                    try: date = lines[1]
                    except Exception as e: date = None
                    sedo_id = tds[1].span.get('axuiuserid')
                    # print(chain)
                    row = {  # 🔥 создаём новый dict КАЖДЫЙ РАЗ
                        'dl': dl,
                        'type': chain.get(dl, None),
                        'number': number,
                        'fio': fio,
                        'sedo_id': int(sedo_id),
                        'status': status,
                        'date': date
                    }
                    
                    # if any(item["fio"] == fio and item["status"] == "Перенаправлено" and item['dl'] == dl - 1 for item in nodes) and chain[dl] == 'параллельное':
                    if any(item["sedo_id"] == sedo_id and item["status"] == "Перенаправлено" and item['dl'] == dl - 1 for item in nodes):
                        dl = dl - 1
                        row['dl'] = dl
                    nodes.append(row)
                    # print(f'dl = {dl}, type = {chain[dl]}, number = {number}, fio = {fio}, status = {status.split()[0]}')
                    # if (chain[dl] == "последовательное") and ("Согласовано" in status) and (dl > 0) and not (any(cls in trs[i+1].get('class', []) for cls in ['agreetable__tr--redirect'])):
                    #     # print("YESSS")
                    #     dl = dl - 1
                    

            else:
                if any(cls in trs[i].get('class', []) for cls in ['agreetable__tr--first-level', 'agreetable__tr']) and not any(cls in trs[i].get('class', []) for cls in ['agreetable__redirect', 'agreetable-redirect', 'agreetable__head', 'agreetable-head']):
                    tds = trs[i].find_all('td')
                    number = tds[0].text.strip()
                    fio = tds[1].span.text.strip().split('\n')[0]
                    status = tds[3].text.strip()
                    lines = [line.strip() for line in tds[3].span.stripped_strings]
                    status = lines[0]  # "Перенаправлено"
                    try: date = lines[1]
                    except Exception as e: date = None
                    sedo_id = tds[1].span.get('axuiuserid')
                    row = {  # 🔥 создаём новый dict КАЖДЫЙ РАЗ
                        'dl': dl,
                        'type': chain.get(dl, None),
                        'number': number,
                        'fio': fio,
                        'sedo_id': int(sedo_id),
                        'status': status,
                        'date': date
                    }
                    nodes.append(row)
                    # print(f'dl = {dl}, type = {chain[dl]}, number = {number}, fio = {fio}, status = {status.split()[0]}')
                    # if (chain[dl] == "Последовательное") and ("Согласовано" in status):
                    #     dl = dl - 1
        # # pprint(nodes)
        # print("!!!!!!!!!!!!")
        # # cleaned = merge_redirect_status_to_previous(nodes)

        # # pprint(cleaned)
        # # print("------------")
        # pprint(build_sogl_tree(merge_redirect_status_to_previous(nodes)))
            




        # print(chain)
        return self.build_sogl_tree(self.merge_redirect_status_to_previous(nodes))

    def update_data(self, params :dict):
        user_repository = UserRepository()
        params = user_repository.no_pool_get_user_info_by_id(params['user_id'])
        fio = params['name']
        date_from = datetime.now() - timedelta(days=params['start_d_days'])
        date_to = datetime.now() + timedelta(days=params['end_d_days'])

        db_doc_ids = self.doc_repository.get_docs_to_update(params=params)
        db_doc_ids = [str(x) for x in db_doc_ids]

        session, DNSID = self.get_session()
        doc_ids = self.get_doc_ids(date_from, date_to, fio=fio, sedo_id=params['sedo_id'], session=session, DNSID=DNSID)
        full_doc_ids = list(dict.fromkeys(db_doc_ids + doc_ids))

        with ProcessPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(self.process_doc, session, doc_id, DNSID) for doc_id in full_doc_ids]

            for future in futures:
                print(future.result())
        return 'success'

    def update_sogl_data(self, params: dict):
        user_repository = UserRepository()
        params = user_repository.no_pool_get_user_info_by_id(params['user_id'])
        fio = params['name']
        print(fio)
        db_sogl_ids = self.doc_repository.get_sogl_to_update(params=params)
        db_sogl_ids = [str(x) for x in db_sogl_ids]
        session, DNSID = self.get_session()
        print(params['sedo_id'])
        doc_ids = self.get_sogl_ids(fio=fio, sedo_id=params['sedo_id'], session=session, DNSID=DNSID)
        full_doc_ids = list(dict.fromkeys(db_sogl_ids + doc_ids))
        with ProcessPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(self.process_sogl, session, doc_id, DNSID) for doc_id in full_doc_ids]

        for future in futures:
            print(future.result())
        return 'success'

    def update_sogl_by_list(self, doclist):
        session, DNSID = self.get_session()
        
        with ProcessPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(self.process_sogl, session, doc_id, DNSID) for doc_id in doclist]

            for future in futures:
                print(future.result())
        return



    def update_docs_by_list(self, doclist):
        session, DNSID = self.get_session()
        
        with ProcessPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(self.process_doc, session, doc_id, DNSID) for doc_id in doclist]

            for future in futures:
                print(future.result())
        return

    async def run_update_data_and_wait(self, params :dict) -> dict:
        try:
            result = await self.sedo_data.set_env_update_on(params['user_id'])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'failed to set query: {str(e)}')
        try:
            result = await asyncio.to_thread(self.update_data, params)
            result = await asyncio.to_thread(self.update_sogl_data, params)
            result = await self.sedo_data.set_env_update_off(params['user_id'])
        except Exception as e:
            try:
                result = await self.sedo_data.set_env_update_off(params['user_id'])
            except Exception as e:
                raise HTTPException(status_code=500, detail=f'failed to unset query: {str(e)}')
            raise HTTPException(status_code=500, detail=str(traceback.print_exc()))
        return {"status": "success", "result": result}

    async def run_update_sogl_and_wait(self, params :dict) -> dict:
        try:
            result = await self.sedo_data.set_env_update_on(params['user_id'])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'failed to set query: {str(e)}')
        try:
            result = await asyncio.to_thread(self.update_sogl_data, params)
            result = await self.sedo_data.set_env_update_off(params['user_id'])
        except Exception as e:
            try:
                result = await self.sedo_data.set_env_update_off(params['user_id'])
            except Exception as e:
                raise HTTPException(status_code=500, detail=f'failed to unset query: {str(e)}')
            raise HTTPException(status_code=500, detail=str(traceback.print_exc()))
        return {"status": "success", "result": result}

    async def run_update_list_docs(self, params :dict) -> dict:
        try:
            user_repository = UserRepository()
            doclist = params['doclist']
            params = await user_repository.get_user_info_by_id(params['user_id'])
            params['doclist'] = doclist
            params['boss1_name'] = await self.user_repository.get_user_fio_by_sedo_id(int(params['boss1_sedo']) if params['boss1_sedo'] is not None else None)
            params['boss2_name'] = await self.user_repository.get_user_fio_by_sedo_id(int(params['boss2_sedo']) if params['boss2_sedo'] is not None else None)
            params['boss3_name'] = await self.user_repository.get_user_fio_by_sedo_id(int(params['boss3_sedo']) if params['boss3_sedo'] is not None else None)
            print(params)
            result = await asyncio.to_thread(self.update_docs_by_list, params['doclist'])
            # result = await asyncio.to_thread(self.update_sogl_by_list, params['doclist'])
            new_data = await self.doc_repository.get_docs_by_id(params)
            return new_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=traceback.print_exc())

    async def run_update_list_sogl(self, params :dict) -> dict:
        try:
            user_repository = UserRepository()
            doclist = params['doclist']
            params = await user_repository.get_user_info_by_id(params['user_id'])
            params['doclist'] = doclist
            params['boss1_name'] = await self.user_repository.get_user_fio_by_sedo_id(int(params['boss1_sedo']) if params['boss1_sedo'] is not None else None)
            params['boss2_name'] = await self.user_repository.get_user_fio_by_sedo_id(int(params['boss2_sedo']) if params['boss2_sedo'] is not None else None)
            params['boss3_name'] = await self.user_repository.get_user_fio_by_sedo_id(int(params['boss3_sedo']) if params['boss3_sedo'] is not None else None)
            print(params)
            result = await asyncio.to_thread(self.update_sogl_by_list, params['doclist'])
            new_data = await self.doc_repository.get_docs_by_id(params)
            return new_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=traceback.print_exc())