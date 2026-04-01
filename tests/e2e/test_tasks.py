# tests/e2e/test_tasks.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestTasks:
    def _login(self, driver, app_url, user):
        driver.get(f"{app_url}/login")
        driver.find_element(By.NAME, "email").send_keys(user["email"])
        driver.find_element(By.NAME, "password").send_keys(user["password"])
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(EC.url_contains("/tarefas"))

    def test_create_task_success(self, driver, app_url, registered_user):
        self._login(driver, app_url, registered_user)

        driver.find_element(By.CSS_SELECTOR, "button[data-testid='nova-tarefa']").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        )

        driver.find_element(By.NAME, "title").send_keys("Tarefa Selenium")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Tarefa Selenium')]"))
        )

        assert "Tarefa Selenium" in driver.page_source