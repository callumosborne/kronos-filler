from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pickle
import select
import time
import sys
import os

"""
Exit codes:
0: Success
1: No Timesheets to fill in
2: Incorrect Login
3: No One Time Code Given During Login
4: Timesheet unsuccessfully filled in
"""

LOGIN_FILE = os.path.join(sys.path[0], "login.txt")
COOKIES_FILE = os.path.join(sys.path[0], "cookies.pkl")

class Kronos:

    def __init__(self):

        # Select False if you want to see the browser automatically fill the sheet in
        headless = True

        options = Options()
        options.headless = headless
        self.browser = webdriver.Firefox(options=options)

        # Open url
        self.browser.get("https://secure3.entertimeonline.com/ta/6119326.login?rnd=AAD")

        self.wait = WebDriverWait(self.browser, 10)

        if os.path.isfile(COOKIES_FILE):
            cookies = pickle.load(open(COOKIES_FILE, "rb"))
            for cookie in cookies:
                self.browser.add_cookie(cookie)

    def login(self, silent=False):

        if not silent:
            print('Logging in...')

        

        # Get login elements
        username_element = self.browser.find_element_by_name("Username")
        password_element = self.browser.find_element_by_name("PasswordView")
        submit_element   = self.browser.find_element_by_name("LoginButton")

        with open (LOGIN_FILE, "r") as login_file:
            username = login_file.readline()[:-1]
            password = login_file.readline()

        # Submit username and password
        username_element.send_keys(username)
        password_element.send_keys(password)

        submit_element.click()

        if self.incorrect_login():
            print('\nIncorrect login.\n')
            sys.exit(2)

        if self.reached_virtual_code():
            if not self.fill_virtual_code():
                sys.exit(3)

        if not silent:
            print('Logged in successfully.')

        pickle.dump( self.browser.get_cookies() , open(COOKIES_FILE,"wb"))

    def incorrect_login(self):

        time.sleep(1)

        errors = self.browser.find_elements_by_class_name("validationMessageError")
        if len(errors) != 0:
            return True
        return False

    def reached_virtual_code(self):

        time.sleep(1)

        return "Configure Virtual Code Settings" in self.browser.page_source

    def fill_virtual_code(self):

        time_taken = 120

        email = self.browser.find_elements_by_class_name("txtLabel")[10].text

        print("\n-VIRTUAL CODE REACHED-")
        print("----------------------")
        print("A code has been sent the email: " + email)

        send_email_element = self.browser.find_element_by_name("SendEmailButton")
        send_email_element.click()

        print("Enter the code here (" + str(time_taken) + "s): ", end = '')
        print()
        
        i, o, e = select.select( [sys.stdin], [], [], time_taken )

        if (i):
            code = sys.stdin.readline().strip()
        else:
            print ("Code not entered...")
            return False

        remember_device_element = self.browser.find_element_by_id("MFARememberDevice")
        remember_device_element.click()

        code_input_element = self.browser.find_element_by_name("TokenValueEmail")
        code_input_element.send_keys(code)

        submit_element = self.browser.find_element_by_id("AuthenticateMFAButton")
        submit_element.click()

        time.sleep(2)

        error_message = self.browser.find_elements_by_class_name("validationMessageError")

        if len(error_message) != 0:
            print("Incorrect Error Code")
            return False

        time.sleep(5)

        return True

    def fill_timesheet(self):

        time.sleep(1)

        self.fill_ts("resultRow1")
        self.fill_ts("resultRow0")

        self.submit_timesheet()

    def fill_ts(self, rows_name):

        row_no = 0

        rows = self.browser.find_elements_by_class_name(rows_name)

        while row_no < len(rows):

            if self.invalid_row(rows[row_no]):
                row_no += 2
                continue

            add_row = rows[row_no].find_element_by_class_name("icon-plus_circle_16")
            add_row.click()

            time.sleep(0.5)

            rows = self.browser.find_elements_by_class_name(rows_name)

            self.fill_row(rows[row_no], "am")

            row_no += 1

            self.fill_row(rows[row_no], "pm")

            row_no += 2

    def invalid_row(self, row):

        date = row.find_element_by_class_name("dateLabel").find_elements_by_tag_name("div")[0].text

        if date[0:3] == "SAT" or date[0:3] == "SUN":
            return True

        self.browser

        if "Holiday" in row.text:
            return True

        if "PTO" in row.text:
            return True

        return False

    def fill_row(self, row, time):

        if time == "am":
            time_in = "9:00"
            time_out = "12:00"
        else:
            time_in = "13:00"
            time_out = "18:00"


        from_time = row.find_elements_by_class_name("inputElementMarker")[0].find_element_by_class_name("editFormText")
        from_time.send_keys(time_in)

        to_time = row.find_elements_by_class_name("inputElementMarker")[1].find_element_by_class_name("editFormText")
        to_time.send_keys(time_out)

    def submit_timesheet(self):

        print('Submitting timesheet...')

        submit = self.browser.find_element_by_class_name("commandBar").find_elements_by_tag_name("a")[2]
        submit.click()

        time.sleep(2)

        ok = self.browser.find_element_by_class_name("primaryButton")
        ok.click()

    def is_timesheet_filled(self):

        time.sleep(1)

        self.browser.switch_to.frame("ADMIN_CENTER")

        get_timesheet = self.browser.find_element_by_link_text("My Current Timesheet")
        get_timesheet.click()

        time.sleep(1)

        total = self.browser.find_element_by_class_name("pageTotalLabelRow").find_elements_by_tag_name("td")[2].find_elements_by_tag_name("input")[0].get_attribute("value")

        if total == "0:00":
            return False

        return True

def main():

    print('\nKronos Filler')
    print('-----------------\n')

    kronos = Kronos()

    kronos.login()

    if kronos.is_timesheet_filled():
        print('\nTimesheet already completed, exiting...\n')
        sys.exit(1)

    print('Complete timesheet...')

    kronos.fill_timesheet()

    print('Checking if timesheet successfully completed...')

    test_kronos = Kronos()
    test_kronos.login(True)

    if test_kronos.is_timesheet_filled():
        print('\nSuccessfully filled in timesheet.\n')
        sys.exit(0)
    else:
        print('\nFailed to complete timesheet.\n')
        sys.exit(4)

main()
