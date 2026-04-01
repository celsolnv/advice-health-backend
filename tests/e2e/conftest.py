import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

API_URL = "http://localhost:8000/api/v1"


@pytest.fixture(scope="session")
def driver():
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("detach", True)  # mantém janela aberta

    # service = Service(ChromeDriverManager().install())
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


@pytest.fixture(scope="session")
def app_url():
    return "http://localhost:5555"


@pytest.fixture(scope="session")
def registered_user():
    """Cria o usuário via API antes dos testes e retorna os dados."""
    user = {
        "first_name": "Selenium",
        "email": "selenium@teste.com",
        "password": "Senha@1234",
        "password_confirm": "Senha@1234",
    }

    # Tenta criar — ignora se já existir (400 = email duplicado)
    response = requests.post(f"{API_URL}/users/register/", json=user)
    assert response.status_code in (201, 400), (
        f"Falha inesperada ao criar usuário de teste: {response.text}"
    )

    return {
        "first_name": user["first_name"],
        "email": user["email"],
        "password": user["password"],
    }