from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestRegister:
    def _clear_session(self, driver, app_url):
        """Limpa sessão navegando para a URL correta primeiro."""
        driver.get(f"{app_url}/cadastro")
        driver.delete_all_cookies()
        try:
            driver.execute_script("localStorage.clear()")
        except Exception:
            pass  # ignora se localStorage não estiver disponível

    def test_register_success(self, driver, app_url):
        self._clear_session(driver, app_url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='input-first-name']"))
        )

        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-first-name']").send_keys("Teste")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-email']").send_keys("novo@teste.com")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-password']").send_keys("Senha@1234")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-password-confirm']").send_keys("Senha@1234")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='btn-submit']").click()

        WebDriverWait(driver, 10).until(lambda d: "/login" in d.current_url or "/tarefas" in d.current_url)
        assert "/login" in driver.current_url or "/tarefas" in driver.current_url

    def test_register_duplicate_email(self, driver, app_url, registered_user):
        self._clear_session(driver, app_url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='input-first-name']"))
        )

        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-first-name']").send_keys("Teste")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-email']").send_keys(registered_user["email"])
        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-password']").send_keys("Senha@1234")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-password-confirm']").send_keys("Senha@1234")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='btn-submit']").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='error-message']"))
        )
        assert driver.find_element(By.CSS_SELECTOR, "[data-testid='error-message']").is_displayed()

    def test_register_password_mismatch(self, driver, app_url):
        self._clear_session(driver, app_url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='input-first-name']"))
        )

        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-first-name']").send_keys("Teste")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-email']").send_keys("outro@teste.com")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-password']").send_keys("Senha@1234")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-password-confirm']").send_keys("SenhaErrada")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='btn-submit']").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='error-message']"))
        )
        assert driver.find_element(By.CSS_SELECTOR, "[data-testid='error-message']").is_displayed()
