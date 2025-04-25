import requests
import certifi
from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == '__main__':
    sedo_pass = os.environ.get("SEDO_PASS")
    s = requests.Session()
    url_auth = 'https://mosedo.mos.ru/auth.php?group_id=21'
    data = {"DNSID": 'wcFDw9WVbMuoIfBOV9hvnAA',
            "group_id": "21",
            "login": 'Арсеньев В.Д.',  # %C0%F0%F1%E5%ED%FC%E5%E2+%C2.%C4.
            "user_id": "80742170",  ##80742170 Арсеньеw ##78264321 Габитов
            "password": sedo_pass,
            "token": "",
            "x": "1"}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Connection': 'keep-alive', }

    r = s.post(url_auth, data=data, headers=headers, allow_redirects=False)

    DNSID = r.headers['location'].split('DNSID=')[1]

    url = f'https://mosedo.mos.ru/document.card.php?id=548471399&DNSID={DNSID}'
    response = s.get(url, verify=certifi.where())
    # Сохраняем как HTML-файл
    with open("./test_docs/debug1.html", "w") as f:
        f.write(response.text)
    