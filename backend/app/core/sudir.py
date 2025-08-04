import requests
from bs4 import BeautifulSoup
import hashlib
import itertools
from urllib.parse import urlparse, parse_qs

ALPHABET = "0123456789/+abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

class RsmLogin:

    #алфавит из pOfw.js aaseta 
    ALPHABET = "0123456789/+abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def find_suffix_pow(self, base: str, max_len=4, required_leading_zero_bytes=2):
        """
        Подбирает суффикс, такой что sha1(base + ':' + suffix) начинается с required_leading_zero_bytes нулей
        """
        for length in range(1, max_len + 1):
            for combo in itertools.product(self.ALPHABET, repeat=length):
                suffix = ''.join(combo)
                candidate = f"{base}:{suffix}"
                digest = hashlib.sha1(candidate.encode("utf-8")).digest()
                if digest.startswith(b'\x00' * required_leading_zero_bytes):
                    return candidate
        raise RuntimeError("Не найден рабочий proofOfWork")


    def get_pow(self, login, password):
        #урл для редиректа
        base_url = 'https://sudir.mos.ru'

        #урл для входа в рсм
        url = 'https://sudir.mos.ru/blitz/login/methods/password?bo=%2Fblitz%2Foauth%2Fae%3Fresponse_type%3Dcode%26client_id%3Dwebrsm.mlc.gov%26redirect_uri%3Dhttp%3A%2F%2Fwebrsm.mlc.gov%3A5222%2FSudir%2FAuth%26scope%3Dopenid%2Bprofile'
        
        #открываем сессию
        session = requests.Session()

        #Заголовки из браузера, не уверен нужны ли они
        headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://sudir.mos.ru",
        "Referer": "https://sudir.mos.ru/blitz/login/methods/password?bo=%2Fblitz%2Foauth%2Fae%3Fresponse_type%3Dcode%26client_id%3Dwebrsm.mlc.gov%26redirect_uri%3Dhttp%3A%2F%2Fwebrsm.mlc.gov%3A5222%2FSudir%2FAuth%26scope%3Dopenid%2Bprofile",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        #нулевой гет чтобы получить первичный куки и редирект обратно на форму входа
        response = requests.get(url, allow_redirects=False, headers=headers)

        #начальный гет чтобы получить все Set-Cookie
        response = session.get(base_url+response.headers['Location'], headers=headers)
        # print(response.status_code)
        # print(session.cookies.get_dict())  # тут уже будут все куки

        #Заводит пэйлоад
        soup = BeautifulSoup(response.text, 'html.parser')
        request_data = {
            'proofOfWork': '',
            'isDelayed': 'false',
            'login': '',
            'password': '',
            'bfp': '23f2ab015b787a1a0bad5d5b5b3e99b9' #какой-то служебный токен, статичный
        }
        #достаем значение value из input 
        proof_input = soup.find('input', attrs={'name': 'proofOfWork'}).get('value')

        base = proof_input.rstrip(':')
        #генерируем валидный pow
        final_proof = self.find_suffix_pow(base)

        request_data['proofOfWork'] = final_proof
        request_data['login'] = login
        request_data['password'] = password

        #засылваем форму входа, теперь можно дергать токен РСМ
        session.post(url, data=request_data, allow_redirects=True, headers=headers)

        #вытаскиваем токен из куки сессии
        return session.cookies.get_dict()['Rsm.Cookie']
    
class SedoLogin:

    ALPHABET = "0123456789/+abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def find_suffix_pow(self, base: str, max_len=4, required_leading_zero_bytes=2):
        """
        Подбирает суффикс, такой что sha1(base + ':' + suffix) начинается с required_leading_zero_bytes нулей
        """
        for length in range(1, max_len + 1):
            for combo in itertools.product(self.ALPHABET, repeat=length):
                suffix = ''.join(combo)
                candidate = f"{base}:{suffix}"
                digest = hashlib.sha1(candidate.encode("utf-8")).digest()
                if digest.startswith(b'\x00' * required_leading_zero_bytes):
                    return candidate
        raise RuntimeError("Не найден рабочий proofOfWork")
    

    def get_pow(self, login, password):
        """
        Returns DNSID, session requests object
        """

        base_url = 'https://sudir.mos.ru'

        session = requests.Session()

        DNSID = 'w-TCSidwCyPiK5j0ONV6z8g'

        second_response = session.get(f'https://mosedo.mos.ru/auth.php?DNSID={DNSID}&openid', allow_redirects=False)

        sudir_response = session.get(second_response.headers['Location'], allow_redirects=False)

        sudir_second_response = session.get(base_url+sudir_response.headers['Location'], allow_redirects=False)

        soup = BeautifulSoup(sudir_second_response.text, 'html.parser')
        request_data = {
            'proofOfWork': '',
            'isDelayed': 'false',
            'login': '',
            'password': '',
            'bfp': '23f2ab015b787a1a0bad5d5b5b3e99b9' #какой-то служебный токен, статичный
        }
        with open ('test.html', 'w', encoding='utf-8') as file:
            file.write(sudir_second_response.text)
        #достаем значение value из input 
        proof_input = soup.find('input', attrs={'name': 'proofOfWork'}).get('value')

        base = proof_input.rstrip(':')
        #генерируем валидный pow
        final_proof = self.find_suffix_pow(base)

        request_data['proofOfWork'] = final_proof
        request_data['login'] = login
        request_data['password'] = password

        sudir_post = session.post(base_url+sudir_response.headers['Location'], data=request_data)
        print(sudir_post.status_code)
        print(sudir_post.request.url)
        print(session.cookies.get_dict())

        #разбираем URL
        parsed = urlparse(sudir_post.request.url)

        #извлекаем GET-параметры
        params = parse_qs(parsed.query)

        #получаем DNSID
        dnsid = params.get('DNSID', [None])[0]

        return dnsid, session



if __name__ == '__main__':
    rsm_login = RsmLogin()
    sedo_login = SedoLogin()
    print(sedo_login.get_pow('', ''))
    pass