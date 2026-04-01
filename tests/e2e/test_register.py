import pytest
from selenium.webdriver.common.by import By


class TestRegister:
    def test_register_success(self, driver, app_url):
        driver.get(f"{app_url}/register")

        driver.find_element(By.NAME, "first_name").send_keys("Teste")
        driver.find_element(By.NAME, "email").send_keys("novo@teste.com")
        driver.find_element(By.NAME, "password").send_keys("Senha@1234")
        driver.find_element(By.NAME, "password_confirm").send_keys("Senha@1234")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        assert "/login" in driver.current_url or "/tarefas" in driver.current_url

    def test_register_duplicate_email(self, driver, app_url):
        driver.get(f"{app_url}/register")

        driver.find_element(By.NAME, "first_name").send_keys("Teste")
        driver.find_element(By.NAME, "email").send_keys("selenium@teste.com")
        driver.find_element(By.NAME, "password").send_keys("Senha@1234")
        driver.find_element(By.NAME, "password_confirm").send_keys("Senha@1234")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        error = driver.find_element(By.CSS_SELECTOR, "[role='alert'], .error, .toast")
        assert error.is_displayed()

    def test_register_password_mismatch(self, driver, app_url):
        driver.get(f"{app_url}/register")

        driver.find_element(By.NAME, "first_name").send_keys("Teste")
        driver.find_element(By.NAME, "email").send_keys("outro@teste.com")
        driver.find_element(By.NAME, "password").send_keys("Senha@1234")
        driver.find_element(By.NAME, "password_confirm").send_keys("SenhaErrada")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        error = driver.find_element(By.CSS_SELECTOR, "[role='alert'], .error, .toast")
        assert error.is_displayed()