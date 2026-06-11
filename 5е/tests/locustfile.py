from locust import HttpUser, task, between


class ShopUser(HttpUser):
    wait_time = between(1, 3)
    host = 'https://www.demoblaze.com'

    @task(3)   # вес 3: выполняется в 3× чаще других
    def view_homepage(self):
        with self.client.get('/', catch_response=True, name='GET /') as r:
            if r.status_code != 200:
                r.failure(f'Главная: ожидался 200, получен {r.status_code}')

    @task(2)
    def view_phone_category(self):
        with self.client.post(
            '/bycat',
            json={'cat': 'phone'},
            catch_response=True,
            name='POST /bycat (phones)'
        ) as r:
            if r.status_code != 200:
                r.failure(f'Категория: статус {r.status_code}')

    @task(2)
    def view_laptop_category(self):
        with self.client.post(
            '/bycat',
            json={'cat': 'notebook'},
            catch_response=True,
            name='POST /bycat (laptops)'
        ) as r:
            if r.status_code != 200:
                r.failure(f'Категория: статус {r.status_code}')

    @task(1)
    def view_product(self):
        with self.client.post(
            '/view',
            json={'id': '1'},
            catch_response=True,
            name='POST /view (product)'
        ) as r:
            if r.status_code != 200:
                r.failure(f'Товар: статус {r.status_code}')

    @task(1)
    def check_cart(self):
        with self.client.post(
            '/viewcart',
            json={'cookie': 'locust_test_user', 'flag': True},
            catch_response=True,
            name='POST /viewcart'
        ) as r:
            if r.status_code != 200:
                r.failure(f'Корзина: статус {r.status_code}')
