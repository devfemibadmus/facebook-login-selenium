import os
import pickle
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FacebookLogin:
    def __init__(self, email, password, cookies_file="facebook_cookies.pkl"):
        # Set up Edge options
        edge_options = Options()
        # edge_options.add_argument("--headless")  # Run in headless mode (without a GUI)
        # edge_options.add_argument("--disable-gpu")  # Disable GPU acceleration
        
        # Initialize the WebDriver
        self.driver = webdriver.Edge(service=Service(), options=edge_options)
        
        self.email = email
        self.password = password
        self.cookies_file = cookies_file

    def load_cookies(self):
        """Load cookies from a file if available."""
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                    print(f"Loaded cookie: {cookie['name']}")
            print("All cookies loaded successfully.")
            return True
        else:
            print("No cookies file found. Need to login with username and password.")
            return False

    def save_cookies(self):
        """Save cookies to a file after login."""
        cookies = self.driver.get_cookies()
        with open(self.cookies_file, "wb") as file:
            pickle.dump(cookies, file)
        print("Cookies saved successfully.")

    def login(self):
        # Open Facebook login page
        self.driver.get("https://www.facebook.com/login")
        
        if self.load_cookies():
            print("Attempting to login with cookies...")
            self.driver.refresh()

        if "login" not in self.driver.current_url and "recover" not in self.driver.current_url:
            print(self.driver.current_url)
            print("Logged in with cookies!")
        else:
            print("Logging in with username and password...")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "email")))

            email_input = self.driver.find_element(By.ID, "email")
            print("Entering email...")
            email_input.send_keys(self.email)
            
            # Enter password
            password_input = self.driver.find_element(By.ID, "pass")
            print("Entering password...")
            password_input.send_keys(self.password)
            
            # Submit the form
            print("Submitting login form...")
            password_input.send_keys(Keys.RETURN)
            
            # Wait for a few seconds to allow the login process to complete
            time.sleep(5)
            
            if "login" not in self.driver.current_url and "recover" not in self.driver.current_url:
                print(self.driver.current_url)
                print("Login successful!")
                self.save_cookies()
            else:
                if "recover" not in self.driver.current_url:
                    try:
                        print("Incorrect Password processing...")
                        self.password_method()
                    except Exception as e:
                        print(f"Error in recovering: {e}")
                else:
                    try:
                        print("2F Authentication processing...")
                        self.recovery_method()
                    except Exception as e:
                        print(f"Error in recovering: {e}")

    def password_method(self):
        returnval = False
        error_messages = []
        tried_time = 0
        passwords = []
        new_password = None

        error_messages.append(f"TITLE: Incorrect Password")

        while tried_time < 3:
            print(f"Holding 5sec to get new password\nold passwords: {passwords}")
            time.sleep(5)
            with open("auth.txt", "r") as f:
                print("Looking for new password")
                lines = f.readlines()
                for line in lines:
                    if line.startswith("PASSWORD:"):
                        password = line.split(":")[1].strip()
                        if password in passwords:
                            new_password = None
                            print(f"No new password provided")
                            error_messages.append(f"No new password provided")
                        else:
                            passwords.append(password)
                            print(f"passwords: {passwords}")
                            error_messages.append(f"passwords: {passwords}")
                            new_password = password
                        tried_time +=1
                        break
            if new_password is not None:
                password_input = self.driver.find_element(By.ID, "pass")
                print("Entering password...")
                password_input.send_keys(new_password)

                time.sleep(5)

                if "login" not in self.driver.current_url and "recover" not in self.driver.current_url:
                    self.save_cookies()
                    tried_time +=3
                    print(f"Login Successful\npassword: {new_password}\nemail: {self.email}")
                    returnval = True
                    break
                else:
                    if "recover" not in self.driver.current_url:
                        error_messages.append(f"password {passwords} not correct")
                        print(f"Attempting recorvering....{self.driver.current_url}")
                        self.attempt_again()
                    else:
                        print("2F Authentication processing...")
                        self.recovery_method()
            f.close()
        with open("password_error.txt", "w") as f:
            password_error = "\n".join(error_messages)
            f.write(password_error)
            f.close()
        return returnval
        
    def recovery_method(self):

            returnval = False
            error_messages = []
            tried_time = 0
            auth_codes = []
            new_code = None

            try: 
                # Select the first option to receive the code
                option = self.driver.find_element(By.CSS_SELECTOR, "input[type='radio']")
                option.click()

                selected_text = option.get_attribute("value")
            except:
                selected_text = f"code sent to {self.email} or alternative emals or phone number"
            error_messages.append(f"TITLE: {selected_text}")

            # Attempt to find and click the submit button
            try:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            except Exception:
                # If the CSS selector fails, try finding a button with "Continue" text
                submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(),'Continue')]")
            
            submit_button.click()
            
            while tried_time < 3:
                print(f"Holding 5sec to get new code\nold codes: {auth_codes}")
                time.sleep(5)
                with open("auth.txt", "r") as f:
                    print("Looking for auth code")
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith("CODE:"):
                            code = line.split(":")[1].strip()
                            if code in auth_codes:
                                new_code = None
                                print("No new code provided")
                                error_messages.append("No new code provided")
                            else:
                                new_code = code
                                auth_codes.append(code)
                                print(f"auth_codes: {auth_codes}")
                                error_messages.append(f"auth_codes: {auth_codes}")
                            tried_time +=1
                            break
                if new_code is not None:
                    code_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
                    code_input.send_keys(new_code)
                    code_input.send_keys(Keys.RETURN)
                    time.sleep(5)
                    if "login" not in self.driver.current_url and "recover" not in self.driver.current_url:
                        tried_time +=3
                        self.save_cookies()
                        print(f"Login Successful\npassword: {self.password}\nemail: {self.email}\ncode: {new_code}")
                        returnval = True
                        break
                    else:
                        print(f"Login attempt {tried_time} failed with codes {auth_codes}")
                f.close()
            
            with open("recover_error.txt", "w") as f:
                recover_error = "\n".join(error_messages)
                f.write(recover_error)
                f.close()

            return returnval

    def close(self):
        self.driver.quit()

# Usage example:
if __name__ == "__main__":
    email = "your-email@example.com"
    password = "your-password"
    
    fb_login = FacebookLogin(email, password)
    fb_login.login()
    # time.sleep(100) # Optional sleep to read GUI if enable
    fb_login.close()
