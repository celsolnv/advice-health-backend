from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestTasks:
    def _clear_session(self, driver, app_url):
        driver.get(f"{app_url}/login")
        driver.delete_all_cookies()
        try:
            driver.execute_script("localStorage.clear()")
        except Exception:
            pass

    def _login(self, driver, app_url, user):
        self._clear_session(driver, app_url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='input-email']"))
        )

        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-email']").send_keys(user["email"])
        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-password']").send_keys(user["password"])
        driver.find_element(By.CSS_SELECTOR, "[data-testid='btn-submit']").click()

        WebDriverWait(driver, 10).until(EC.url_contains("/tarefas"))

    def test_create_task_success(self, driver, app_url, registered_user):
        self._login(driver, app_url, registered_user)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='btn-nova-tarefa']"))
        )
        driver.find_element(By.CSS_SELECTOR, "[data-testid='btn-nova-tarefa']").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='input-task-title']"))
        )
        driver.find_element(By.CSS_SELECTOR, "[data-testid='input-task-title']").send_keys("Tarefa Selenium")
        driver.find_element(By.CSS_SELECTOR, "[data-testid='btn-submit']").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Tarefa Selenium')]"))
        )
        assert "Tarefa Selenium" in driver.page_source