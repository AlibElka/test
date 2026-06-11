import requests
import time
import statistics
import pytest

BASE = 'https://www.demoblaze.com'
REPEAT = 10 

ENDPOINTS = [
    ('/', 'Главная страница'),
    ('/config.json', 'Конфигурация'),
    ('/api/config', 'API конфиг'),
]

# Вспомогательная функция
def measure(url: str, n: int = REPEAT) -> dict:
    """
    Выполнить n GET-запросов к url и вернуть статистику времени ответа.

    Возвращаемые метрики:
    - min / max / mean / median — базовая статистика (мс)
    - p95  — 95-й перцентиль (хвостовая задержка)
    - stdev — стандартное отклонение (разброс)
    - size_kb — средний размер тела ответа (кб)
    - errors — количество не-200 ответов
    """
    times, sizes, statuses = [], [], []

    for _ in range(n):
        t0 = time.perf_counter()
        r = requests.get(url, timeout=15)
        elapsed = (time.perf_counter() - t0) * 1000  # → мс
        times.append(elapsed)
        sizes.append(len(r.content))
        statuses.append(r.status_code)

    sorted_times = sorted(times)
    return {
        'min':     round(min(times), 1),
        'max':     round(max(times), 1),
        'mean':    round(statistics.mean(times), 1),
        'median':  round(statistics.median(times), 1),
        'p95':     round(sorted_times[int(n * 0.95) - 1], 1),
        'stdev':   round(statistics.stdev(times), 1),
        'size_kb': round(statistics.mean(sizes) / 1024, 1),
        'errors':  statuses.count(200) - n,  # отрицательное = есть ошибки
    }
# PERF-01: Latency главной страницы
def test_homepage_latency():
    """
    PERF-01: Замер latency главной страницы (10 запросов).

    Пороги:
    - mean < 2000 мс  (средняя задержка)
    - P95  < 4000 мс  (хвостовая задержка — 95% запросов быстрее)
    """
    stats = measure(BASE + '/')

    print(f'\nPERF-01: GET /')
    print(f'  min={stats["min"]}мс  max={stats["max"]}мс  '
          f'mean={stats["mean"]}мс  median={stats["median"]}мс')
    print(f'  P95={stats["p95"]}мс  stdev={stats["stdev"]}мс  '
          f'size={stats["size_kb"]}кб  errors={abs(stats["errors"])}')

    assert stats['mean'] < 2000, \
        f'Среднее время {stats["mean"]}мс превышает порог 2000мс'
    assert stats['p95'] < 4000, \
        f'P95 {stats["p95"]}мс превышает порог 4000мс'

# PERF-02: Сравнительный замер эндпоинтов
def test_all_endpoints_latency():
    """
    PERF-02: Сравнительный замер всех ключевых эндпоинтов (5 запросов на каждый).

    Используется для выявления «тяжёлых» страниц и сравнения их производительности.
    Результаты выводятся в виде таблицы в консоль.
    """
    print('\nPERF-02: Замер эндпоинтов')
    print(f'  {"Эндпоинт":25s} │ {"mean":>8} │ {"P95":>8} │ {"size":>7}')
    print('  ' + '─' * 55)

    for path, name in ENDPOINTS:
        try:
            s = measure(BASE + path, n=5)
            print(f'  {name:25s} │ {s["mean"]:>7.1f}мс │ '
                  f'{s["p95"]:>7.1f}мс │ {s["size_kb"]:>5.1f}кб')
        except Exception as e:
            print(f'  {name:25s} │ ОШИБКА: {e}')

# PERF-03: Анализ HTTP-заголовков ответа
def test_response_headers_analysis():
    r = requests.get(BASE + '/', timeout=10)
    headers = r.headers

    INTERESTING = [
        'Content-Type', 'Content-Length', 'Content-Encoding',
        'Cache-Control', 'Connection', 'Server', 'X-Response-Time',
    ]

    print('\nPERF-03: HTTP-заголовки ответа')
    print('  ' + '─' * 55)
    for key in INTERESTING:
        val = headers.get(key, '(отсутствует)')
        print(f'  {key:30s}: {val}')

    encoding = headers.get('Content-Encoding', '')
    print(f'\n  Сжатие: {encoding if encoding else "НЕТ — сжатие не применяется"}')

    cache = headers.get('Cache-Control', '')
    print(f'  Кэш:    {cache if cache else "Заголовок Cache-Control отсутствует"}')

    size_kb = len(r.content) / 1024
    print(f'  Размер: {size_kb:.1f} кб')
    print(f'  Статус: HTTP {r.status_code}')

    assert r.status_code == 200, \
        f'Главная страница вернула статус {r.status_code}, ожидался 200'
