import time
import pyperclip
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

SEND_MESSAGE_BOX_XPATH = '/html/body/div[1]/div/div/div/div/div[3]/div/div[5]/div/footer/div[1]/div/span/div/div/div/div[3]/div[1]/p'


class WhatsApp(object):
    """
    Inspired from https://github.com/Kalebu/alright
    """

    def __init__(self, logger, browser=None, time_out=600):
        self.BASE_URL = "https://web.whatsapp.com/"
        self.suffix_link = "https://web.whatsapp.com/send?phone={mobile}&text&type=phone_number&app_absent=1"

        self.browser = browser
        self.logger = logger
        self.wait = WebDriverWait(self.browser, time_out)
        self.browser.maximize_window()
        self.mobile = ""

    def wait_for_login(self):
        WebDriverWait(self.browser, 120).until_not(
            EC.presence_of_element_located(
                (By.ID, "link-device-phone-number-code-screen-instructions")
            )
        )
        WebDriverWait(self.browser, 60).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-icon^='new-chat']")
            )
        )

    def get_phone_link(self, mobile) -> str:
        """get_phone_link (), create a link based on whatsapp (wa.me) api
        """
        return self.suffix_link.format(mobile=mobile)

    def find_user(self, mobile) -> None:
        """find_user()
        Makes a user with a given mobile a current target for the wrapper
        """
        self.mobile = mobile
        link = self.get_phone_link(mobile)
        self.browser.get(link)
        self.wait_for_login()
        WebDriverWait(self.browser, 15).until(
            EC.element_to_be_clickable((By.XPATH, SEND_MESSAGE_BOX_XPATH))
        )

    def send_message(self, message, timeout=0.0):
        """send_message ()
        Sends a message to a target user
        """
        try:
            input_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, SEND_MESSAGE_BOX_XPATH))
            )
            for line in message.split("\n"):
                pyperclip.copy(line)
                input_box.send_keys(Keys.CONTROL+"v")
                ActionChains(self.browser).key_down(Keys.SHIFT).key_down(
                    Keys.ENTER
                ).key_up(Keys.ENTER).key_up(Keys.SHIFT).perform()
            if timeout:
                time.sleep(timeout)
            input_box.send_keys(Keys.ENTER)
            return True
        except (NoSuchElementException, Exception) as e:
            self.logger.exception(
                f"Failed to send a message to {self.mobile} - {e}")
            return False

    def send_direct_message(self, mobile: str, message: str):
        self.find_user(mobile)
        return self.send_message(message)
