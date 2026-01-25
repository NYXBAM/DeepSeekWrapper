import os
from dotenv import load_dotenv


load_dotenv()
BROWSER_TYPE = "firefox" # or chromium 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    "storage_state_path": os.path.join(BASE_DIR, "storage", "storage_state.json"),
    "protected_page_url": "https://chat.deepseek.com/",
    "paragraph_selector": ".ds-markdown-paragraph, pre",
    "last_paragraph_selector": ".ds-markdown-paragraph, pre",
    "input_placeholder": "Message DeepSeek",
    "button_combo_selector": "._7436101.ds-icon-button"
}

auth_config = {
    "storage_state_path": os.path.join(BASE_DIR, "storage", "storage_state.json"),
    'login_url': 'https://chat.deepseek.com/sign_in',
    'login': os.getenv("DEEPSEEK_LOGIN"),
    'password': os.getenv("DEEPSEEK_PASSWORD"),
    'user_input_placeholder': "Phone number / email address",
    'password_input_placeholder': "Password",
    'unique_class': 'button:has-text("Log in")'
}


