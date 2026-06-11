import requests

BASE_URL = "https://jsonplaceholder.typicode.com"

def test_get_all_posts():
    """TC-001: Получение списка всех постов"""
    response = requests.get(f"{BASE_URL}/posts")
    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
    data = response.json()
    assert isinstance(data, list), "Ответ должен быть массивом"
    assert len(data) == 100, f"Ожидалось 100 постов, получено {len(data)}"
    assert "id" in data[0], "Каждый пост должен содержать поле 'id'"
    assert "title" in data[0], "Каждый пост должен содержать поле 'title'"
    print(f"[PASS] TC-001: GET /posts — {len(data)} постов, статус {response.status_code}")

def test_get_single_post():
    """TC-002: Получение одного поста по ID"""
    response = requests.get(f"{BASE_URL}/posts/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "userId" in data
    assert "body" in data
    print(f"[PASS] TC-002: GET /posts/1 — id={data['id']}, статус {response.status_code}")

def test_post_not_found():
    """TC-003: Запрос несуществующего поста"""
    response = requests.get(f"{BASE_URL}/posts/9999")
    assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}"
    print(f"[PASS] TC-003: GET /posts/9999 — статус {response.status_code} (Not Found)")

def test_create_post():
    """TC-004: Создание нового поста (POST)"""
    payload = {"title": "Test Post", "body": "Test body", "userId": 1}
    response = requests.post(f"{BASE_URL}/posts", json=payload)
    assert response.status_code == 201, f"Ожидался 201, получен {response.status_code}"
    data = response.json()
    assert data["title"] == payload["title"]
    assert "id" in data
    print(f"[PASS] TC-004: POST /posts — создан пост с id={data['id']}, статус {response.status_code}")

def test_filter_by_user():
    """TC-005: Фильтрация постов по userId"""
    response = requests.get(f"{BASE_URL}/posts?userId=1")
    assert response.status_code == 200
    data = response.json()
    assert all(p["userId"] == 1 for p in data), "Все посты должны принадлежать userId=1"
    print(f"[PASS] TC-005: GET /posts?userId=1 — найдено {len(data)} постов для userId=1")

def test_response_time():
    """TC-006: Проверка времени ответа"""
    import time
    start = time.time()
    response = requests.get(f"{BASE_URL}/posts")
    elapsed = time.time() - start
    assert elapsed < 3.0, f"Время ответа {elapsed:.2f}s превышает 3 секунды"
    print(f"[PASS] TC-006: Время ответа = {elapsed:.3f}s (< 3.0s)")

def test_content_type():
    """TC-007: Проверка Content-Type заголовка"""
    response = requests.get(f"{BASE_URL}/posts/1")
    ct = response.headers.get("Content-Type", "")
    assert "application/json" in ct, f"Ожидался application/json, получен: {ct}"
    print(f"[PASS] TC-007: Content-Type = '{ct}'")

def test_update_post():
    """TC-008: Обновление поста (PUT)"""
    payload = {"id": 1, "title": "Updated Title", "body": "Updated body", "userId": 1}
    response = requests.put(f"{BASE_URL}/posts/1", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    print(f"[PASS] TC-008: PUT /posts/1 — обновлён, статус {response.status_code}")

def test_delete_post():
    """TC-009: Удаление поста (DELETE)"""
    response = requests.delete(f"{BASE_URL}/posts/1")
    assert response.status_code == 200
    print(f"[PASS] TC-009: DELETE /posts/1 — статус {response.status_code}")

def test_empty_body_post():
    """TC-010: Негативный тест — отправка пустого тела запроса"""
    response = requests.post(f"{BASE_URL}/posts", json={})
    # JSONPlaceholder принимает даже пустые запросы (особенность мок-API)
    print(f"[INFO] TC-010: POST /posts с пустым телом — статус {response.status_code}, тело: {response.json()}")

if __name__ == "__main__":
    print("" * 55)
    print("  Тестирование API: JSONPlaceholder")
    print("  Базовый URL:", BASE_URL)
    print("" * 55)
    tests = [
        test_get_all_posts, test_get_single_post, test_post_not_found,
        test_create_post, test_filter_by_user, test_response_time,
        test_content_type, test_update_post, test_delete_post, test_empty_body_post
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}: {e}")
        except Exception as e:
            print(f"[ERROR] {t.__name__}: {e}")
    print("" * 55)
    print(f"Итог: {passed}/{len(tests)} тестов прошло")
    