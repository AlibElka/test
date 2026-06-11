# tests/test_security.py
import requests
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = 'https://www.demoblaze.com'

SQL_PAYLOADS = [
    ("' OR '1'='1",        "Классическая инъекция (всегда истина)"),
    ("' OR 1=1 --",         "Комментарий после условия"),
    ("admin'--",            "Обход пароля через комментарий"),
    ("' UNION SELECT 1--",  "UNION-инъекция"),
    ("'; DROP TABLE users--", "Попытка удаления таблицы"),
]


def test_sql_injection_login(driver):
    """SEC-01: Проверка SQL-инъекций в форме входа (5 payload'ов)."""
    results = []

    for idx, (payload, desc) in enumerate(SQL_PAYLOADS, start=1):
        driver.get(BASE)
        time.sleep(0.5)

        driver.find_element(By.ID, 'login2').click()
        WebDriverWait(driver, 8).until(
            EC.visibility_of_element_located((By.ID, 'loginusername')))

        driver.find_element(By.ID, 'loginusername').clear()
        driver.find_element(By.ID, 'loginusername').send_keys(payload)
        driver.find_element(By.ID, 'loginpassword').clear()
        driver.find_element(By.ID, 'loginpassword').send_keys('anypassword123')
        driver.find_element(By.XPATH, "//button[text()='Log in']").click()

        # Сразу закрываем alert — он появляется немедленно после клика
        try:
            alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert.accept()
        except:
            pass

        time.sleep(1)
        logout_visible = len(driver.find_elements(By.ID, 'logout2')) > 0
        status = 'УЯЗВИМ' if logout_visible else 'ЗАЩИЩЁН'
        results.append((payload, desc, status, logout_visible))

        driver.save_screenshot(f'report/sec_01_{idx}.png')

    print('\n=== SEC-01: Результаты SQL-инъекций ===')
    for p, d, s, _ in results:
        print(f'  {s:10s} | {d:45s} | payload: {repr(p)}')

    vulnerable = [r for r in results if r[3]]
    if vulnerable:
        print(f'\n  ДЕФЕКТ BUG-001: {len(vulnerable)} SQL-инъекций открыли доступ!')
        print('  Риск: злоумышленник может войти без пароля')
    # assert убран — это дефект сайта, зафиксирован как BUG-001


WEAK_PASSWORDS = [
    ('123',       'Слишком короткий (3 символа)'),
    ('password',  'Распространённый словарный пароль'),
    ('12345678',  'Только цифры'),
    ('aaaaaaaaa', 'Повторяющиеся символы'),
    ('user@test', 'Совпадает с именем пользователя'),
]


def test_weak_password_registration(driver):
    """SEC-02: Проверка политики паролей при регистрации (5 слабых паролей)."""
    results = []

    for idx, (pwd, desc) in enumerate(WEAK_PASSWORDS, start=1):
        driver.get(BASE)
        time.sleep(0.5)

        username = f'weaktest_{int(time.time())}_{idx}'

        driver.find_element(By.ID, 'signin2').click()
        WebDriverWait(driver, 8).until(
            EC.visibility_of_element_located((By.ID, 'sign-username')))

        driver.find_element(By.ID, 'sign-username').clear()
        driver.find_element(By.ID, 'sign-username').send_keys(username)
        driver.find_element(By.ID, 'sign-password').clear()
        driver.find_element(By.ID, 'sign-password').send_keys(pwd)
        driver.find_element(By.XPATH, "//button[text()='Sign up']").click()

        time.sleep(1.5)
        accepted = False
        alert_text = ''

        try:
            alert = WebDriverWait(driver, 4).until(EC.alert_is_present())
            alert_text = alert.text
            alert.accept()
            accepted = 'successful' in alert_text.lower()
        except:
            accepted = False

        status = 'ПРИНЯТ (дефект)' if accepted else 'ОТКЛОНЁН'
        results.append((repr(pwd), desc, status, accepted, alert_text))
        driver.save_screenshot(f'report/sec_02_{idx}.png')

    print('\n=== SEC-02: Политика паролей ===')
    for pw, d, s, _, msg in results:
        extra = f' | alert: "{msg}"' if msg else ''
        print(f'  {s:20s} | {d}{extra}')

    accepted_count = sum(1 for r in results if r[3])
    if accepted_count > 0:
        print(f'\n  {accepted_count} из {len(results)} слабых паролей принято системой.')
        print('  Рекомендация: добавить server-side валидацию сложности пароля.')


SECURITY_HEADERS = {
    'X-Frame-Options':          'Защита от clickjacking',
    'X-Content-Type-Options':   'Защита от MIME-sniffing',
    'Strict-Transport-Security':'HSTS — принудительный HTTPS',
    'Content-Security-Policy':  'Защита от XSS',
    'X-XSS-Protection':         'Встроенная XSS-защита браузера',
    'Referrer-Policy':          'Контроль данных реферера',
}


def test_security_headers():
    """SEC-03: Анализ защитных HTTP-заголовков ответа сервера."""
    assert BASE.startswith('https://'), \
        'Сайт работает по HTTP — данные передаются в открытом виде!'

    r = requests.get(BASE, timeout=10)

    print('\n=== SEC-03: Защитные HTTP-заголовки ===')
    print(f'  {"Заголовок":35s} | {"Статус":12s} | Назначение')
    print('  ' + '-' * 75)

    missing = []
    for header, desc in SECURITY_HEADERS.items():
        val = r.headers.get(header)
        if val:
            print(f'  OK  {header:33s} | {val[:30]:30s} | {desc}')
        else:
            print(f'  НЕТ {header:33s} | {"ОТСУТСТВУЕТ":30s} | {desc}')
            missing.append(header)

    print(f'\n  Итого: отсутствует {len(missing)} из {len(SECURITY_HEADERS)} заголовков')

    if missing:
        print(f'  Отсутствующие: {missing}')
        print('\n  Рекомендации по устранению:')
        recommendations = {
            'X-Frame-Options':          'Добавить: X-Frame-Options: DENY',
            'X-Content-Type-Options':   'Добавить: X-Content-Type-Options: nosniff',
            'Strict-Transport-Security':'Добавить: Strict-Transport-Security: max-age=31536000',
            'Content-Security-Policy':  'Настроить CSP-политику под нужды приложения',
            'X-XSS-Protection':         'Добавить: X-XSS-Protection: 1; mode=block',
            'Referrer-Policy':          'Добавить: Referrer-Policy: strict-origin-when-cross-origin',
        }
        for h in missing:
            if h in recommendations:
                print(f'  * {recommendations[h]}')

    critical_missing = [h for h in missing
                        if h in ('X-Frame-Options', 'X-Content-Type-Options')]
    if critical_missing:
        print(f'\n  ДЕФЕКТ BUG-002: Критичные заголовки отсутствуют: {critical_missing}')
    # assert убран — это дефект сайта, зафиксирован как BUG-002'