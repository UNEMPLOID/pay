import subprocess
import sys
import asyncio
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from webdriver_manager.chrome import ChromeDriverManager

# Define necessary packages
packages = [
    'selenium',
    'python-telegram-bot',
    'webdriver-manager'
]

def install_packages():
    """Install necessary packages."""
    subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)

def fetch_page(url: str) -> str:
    """Fetch page content using Selenium with Chromium."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')  # Disables GPU hardware acceleration
    options.add_argument('--remote-debugging-port=9222')  # Optional for debugging

    # Use Chromium buildpack
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        content = driver.page_source
    except Exception as e:
        content = str(e)
    finally:
        driver.quit()
    return content

def detect_payment_gateways(url: str) -> str:
    """Detect payment gateways on the provided URL."""
    PAYMENT_GATEWAYS = {
        'PayPal': re.compile(r'paypal\.com', re.IGNORECASE),
        'Stripe': re.compile(r'stripe\.com', re.IGNORECASE),
        'Square': re.compile(r'square\.com', re.IGNORECASE),
        'Authorize.Net': re.compile(r'authorize\.net', re.IGNORECASE),
        'Braintree': re.compile(r'braintreegateway\.com', re.IGNORECASE),
        'Worldpay': re.compile(r'worldpay\.com', re.IGNORECASE),
        'Adyen': re.compile(r'adyen\.com', re.IGNORECASE),
        'Alipay': re.compile(r'alipay\.com', re.IGNORECASE),
        'WePay': re.compile(r'wepay\.com', re.IGNORECASE),
        'Skrill': re.compile(r'skrill\.com', re.IGNORECASE),
        'Payza': re.compile(r'payza\.com', re.IGNORECASE),
        '2Checkout': re.compile(r'2checkout\.com', re.IGNORECASE),
        'Klarna': re.compile(r'klarna\.com', re.IGNORECASE),
        'Dwolla': re.compile(r'dwolla\.com', re.IGNORECASE),
        'Revolut': re.compile(r'revolut\.com', re.IGNORECASE),
        'Apple Pay': re.compile(r'apple\.com/apple-pay', re.IGNORECASE),
        'Google Pay': re.compile(r'pay\.google\.com', re.IGNORECASE),
        'Samsung Pay': re.compile(r'samsung\.com/samsung-pay', re.IGNORECASE),
        'Zelle': re.compile(r'zellepay\.com', re.IGNORECASE),
        'Mollie': re.compile(r'mollie\.com', re.IGNORECASE),
        'PaymentSense': re.compile(r'paymentsense\.co\.uk', re.IGNORECASE),
        'Sage Pay': re.compile(r'sagepay\.com', re.IGNORECASE),
        'BlueSnap': re.compile(r'bluesnap\.com', re.IGNORECASE),
        'WeChat Pay': re.compile(r'wechat\.com', re.IGNORECASE),
        'Paysafe': re.compile(r'paysafe\.com', re.IGNORECASE),
        'ProPay': re.compile(r'propay\.com', re.IGNORECASE),
        'Ingenico': re.compile(r'ingenico\.com', re.IGNORECASE),
        'GoCardless': re.compile(r'gocardless\.com', re.IGNORECASE),
        'BluePay': re.compile(r'bluepay\.com', re.IGNORECASE),
        'Eway': re.compile(r'eway\.com\.au', re.IGNORECASE),
        'CyberSource': re.compile(r'cybersource\.com', re.IGNORECASE),
        'First Data': re.compile(r'firstdata\.com', re.IGNORECASE),
        'Elavon': re.compile(r'elavon\.com', re.IGNORECASE),
        'Neteller': re.compile(r'neteller\.com', re.IGNORECASE),
        'Sofort': re.compile(r'sofort\.com', re.IGNORECASE),
        'Sezzle': re.compile(r'sezzle\.com', re.IGNORECASE),
        'Affirm': re.compile(r'affirm\.com', re.IGNORECASE),
        'Laybuy': re.compile(r'laybuy\.com', re.IGNORECASE),
        'Splitit': re.compile(r'splitit\.com', re.IGNORECASE),
        'RapidPay': re.compile(r'rapidpay\.com', re.IGNORECASE),
        'TriPOS': re.compile(r'tripos\.com', re.IGNORECASE)
    }

    page_content = fetch_page(url)
    if not page_content:
        return 'Failed to fetch the URL or the URL is not reachable.'

    detected_gateways = []
    for name, pattern in PAYMENT_GATEWAYS.items():
        if pattern.search(page_content):
            detected_gateways.append(name)

    if detected_gateways:
        return f'Payment gateways detected on {url}: {", ".join(detected_gateways)}'
    else:
        return f'No known payment gateways detected on {url}.'

async def start(update: Update, context: CallbackContext) -> None:
    """Handle the /start command."""
    await update.message.reply_text('Send me a website URL to check for payment gateways.')

async def check_payment_gateway(update: Update, context: CallbackContext) -> None:
    """Handle the /check command."""
    url = context.args[0] if context.args else None
    if not url:
        await update.message.reply_text('Please provide a URL.')
        return

    await update.message.reply_text(f'Scanning {url} for payment gateways. Please wait...')
    result_message = await asyncio.to_thread(detect_payment_gateways, url)
    await update.message.reply_text(result_message)

async def main() -> None:
    """Run the Telegram bot."""
    install_packages()  # Install packages if not already installed
    token = '7379729141:AAFYATc4MLO6ZMoq3E4eikHc_DBCjO53apQ'  # Hardcoded bot token
    application = ApplicationBuilder().token(token).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('check', check_payment_gateway))

    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
