from seleniumbase import Driver
import time
import random
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def random_delay(min_delay=0.5, max_delay=1.5):
    time.sleep(random.uniform(min_delay, max_delay))

def human_type(element, text):
    for char in text:
        element.send_keys(char)
        random_delay(0.05, 0.15)

def get_accounts():
    try:
        with open('accounts.txt', 'r', encoding='utf-8') as f:
            line = f.readline().strip()
            email, password = line.split('|')
            return email.strip(), password.strip()
    except Exception as e:
        print(f"Error reading accounts.txt: {e}")
        return None, None

def wait_for_element(driver, selector, by=By.CSS_SELECTOR, timeout=30, condition="clickable"):
    try:
        wait = WebDriverWait(driver, timeout)
        if condition == "clickable":
            element = wait.until(EC.element_to_be_clickable((by, selector)))
        elif condition == "visible":
            element = wait.until(EC.visibility_of_element_located((by, selector)))
        elif condition == "presence":
            element = wait.until(EC.presence_of_element_located((by, selector)))
        return element
    except TimeoutException:
        print(f"Timeout waiting for element: {selector}")
        return None

def safe_click(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)
        element.click()
        return True
    except Exception as e:
        print(f"Error clicking element: {e}")
        return False

def solve_captcha(api_key, url, sitekey):
    api_endpoint = "https://api.capsolver.com/createTask"
    payload = {
        "clientKey": api_key,
        "task": {
            "type": "HCaptchaTaskProxyless",
            "websiteURL": url,
            "websiteKey": sitekey,
        }
    }
    try:
        response = requests.post(api_endpoint, json=payload)
        if response.status_code == 200:
            task_id = response.json().get("taskId")
            for _ in range(30):
                result_response = requests.post(
                    "https://api.capsolver.com/getTaskResult",
                    json={"clientKey": api_key, "taskId": task_id}
                )
                if result_response.status_code == 200:
                    result_data = result_response.json()
                    if result_data.get("status") == "ready":
                        return result_data.get("solution").get("gRecaptchaResponse")
                time.sleep(2)
    except Exception as e:
        print(f"Error solving captcha: {e}")
    return None

def main():
    email, password = get_accounts()
    if not email or not password:
        print("Failed to get account credentials")
        return

    username = email.split('@')[0]

    driver = Driver(uc=True)
    driver.maximize_window()

    try:
        print("Opening GitHub signup...")
        driver.get("https://github.com/signup")
        random_delay(3, 5)

        print("Filling email...")
        email_field = wait_for_element(driver, "#email")
        if email_field:
            human_type(email_field, email)
            random_delay()

        continue_button = wait_for_element(driver, "button[data-continue-to='password-container']")
        if continue_button:
            safe_click(driver, continue_button)
            random_delay(2, 3)

        print("Filling password...")
        password_field = wait_for_element(driver, "#password")
        if password_field:
            human_type(password_field, password)
            random_delay()

        continue_button = wait_for_element(driver, "button[data-continue-to='username-container']")
        if continue_button:
            safe_click(driver, continue_button)
            random_delay(2, 3)

        print("Filling username...")
        username_field = wait_for_element(driver, "#login")
        if username_field:
            human_type(username_field, username)
            random_delay()

        continue_button = wait_for_element(driver, "button[data-continue-to='opt-in-container']")
        if continue_button:
            safe_click(driver, continue_button)
            random_delay(2, 3)

        print("Handling opt-in...")
        opt_in_button = wait_for_element(driver, "button[data-continue-to='captcha-and-submit-container']")
        if opt_in_button:
            safe_click(driver, opt_in_button)
            random_delay(2, 3)

        # Cập nhật phần click với tọa độ cụ thể
        print("Clicking at specific coordinates...")
        try:
            script = """
                const element = document.querySelector("[name='h-captcha-response']");
                if (element) {
                    const rect = element.getBoundingClientRect();
                    const x = rect.left + 257.320;
                    const y = rect.top + 18.000;
                    const clickEvent = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true,
                        clientX: x,
                        clientY: y
                    });
                    element.dispatchEvent(clickEvent);
                }
            """
            driver.execute_script(script)
            random_delay(2, 3)
        except Exception as e:
            print(f"Error clicking at coordinates: {e}")

        print("Handling captcha...")
        sitekey = "4c672d35-0701-42b2-88c3-78380b0db560"
        captcha_response = solve_captcha(
            "CAP-22CD1A3CB55623F4A04A8583274CE2AF",  # Replace with your Capsolver API key
            "https://github.com/signup",
            sitekey
        )
        if captcha_response:
            print("Captcha solved successfully")
            driver.execute_script(f'document.querySelector("[name=h-captcha-response]").value = "{captcha_response}";')
            random_delay(2, 3)

        submit_button = wait_for_element(driver, "button[data-optimizely-event='click.signup_continue.captcha']")
        if submit_button:
            safe_click(driver, submit_button)
            random_delay(5, 7)

        print("Opening mail.tm...")
        driver.execute_script("window.open('https://mail.tm/en/', '_blank');")
        driver.switch_to.window(driver.window_handles[1])
        random_delay(3, 5)

        print("Logging into mail.tm...")
        login_button = wait_for_element(driver, "a[href='/en/login']")
        if login_button:
            safe_click(driver, login_button)
            random_delay(2, 3)

        email_input = wait_for_element(driver, "#address")
        if email_input:
            human_type(email_input, email)

        password_input = wait_for_element(driver, "#password")
        if password_input:
            human_type(password_input, password)
            random_delay()

        submit_button = wait_for_element(driver, "button[type='submit']")
        if submit_button:
            safe_click(driver, submit_button)
            random_delay(3, 5)

        print("Waiting for GitHub verification email...")
        for _ in range(30):
            github_email = wait_for_element(driver, "td.from:contains('GitHub')", condition="presence", timeout=5)
            if github_email:
                safe_click(driver, github_email)
                random_delay(2, 3)
                break
            driver.refresh()
            random_delay(2, 3)
        else:
            print("GitHub verification email not found")
            return

        code_element = wait_for_element(driver, "table.content td.code")
        if code_element:
            verification_code = code_element.text.strip()

            driver.switch_to.window(driver.window_handles[0])
            random_delay(2, 3)

            print("Entering verification code...")
            for i, digit in enumerate(verification_code):
                input_selector = f"input[name='input-{i}']"
                code_input = wait_for_element(driver, input_selector)
                if code_input:
                    human_type(code_input, digit)
                    random_delay(0.2, 0.4)

            random_delay(3, 5)
            print("Registration completed successfully!")
        else:
            print("Verification code not found in email")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        random_delay(3, 5)
        driver.quit()

if __name__ == "__main__":
    main()
