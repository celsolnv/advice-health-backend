from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestLogin:
    def test_login_success(self, driver, app_url, registered_user):
        driver.get(f"{app_url}/login")

        # Aguarda a página carregar
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='input-email']"))
        )

        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-email']").send_keys(registered_user["email"])
        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-password']").send_keys(registered_user["password"])
        driver.find_element(By.CSS_SELECTOR, "[data-testid='btn-submit']").click()

        WebDriverWait(driver, 10).until(EC.url_contains("/tarefas"))
        assert "/tarefas" in driver.current_url

    def test_login_invalid_credentials(self, driver, app_url):
        # Limpa sessão do teste anterior
        driver.delete_all_cookies()
        driver.execute_script("localStorage.clear()")
        driver.get(f"{app_url}/login")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='input-email']"))
        )

        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-email']").send_keys("errado@teste.com")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-password']").send_keys("SenhaErrada")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='btn-submit']").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='error-message']"))
        )
        assert driver.find_element(By.CSS_SELECTOR, "[data-testid='error-message']").is_displayed()

    def test_login_redirects_unauthenticated_user(self, driver, app_url):
        # Limpa sessão
        driver.delete_all_cookies()
        driver.execute_script("localStorage.clear()")

        driver.get(f"{app_url}/tarefas")

        WebDriverWait(driver, 10).until(EC.url_contains("/login"))
        assert "/login" in driver.current_url
