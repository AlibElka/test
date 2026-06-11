import pytest
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

@pytest.fixture(scope='function')
def driver():
    options = webdriver.EdgeOptions()
    options.add_argument('--window-size=1280,800')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    drv = webdriver.Edge(
        service=Service(EdgeChromiumDriverManager().install()),
        options=options
    )
    drv.implicitly_wait(10)
    yield drv
    drv.quit()