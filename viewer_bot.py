import asyncio
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
import zipfile
import os
import time
import sys

proxies = open("/Users/timstellar/Documents/Projects/StreamForge/proxies.txt").readlines()
target_channel = 'timstellar'
amount = len(proxies)

def create_proxy_extension(proxy, plugin_path):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (proxy[0], int(proxy[1]), proxy[2], (proxy[3])[:-1])

    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr('manifest.json', manifest_json)
        zp.writestr('background.js', background_js)

def get_chromedriver(proxy, user_agent=None):
    chrome_options = webdriver.ChromeOptions()

    # Create proxy extension
    plugin_file = f'proxy_auth_plugin_{proxy[0]}_{proxy[1]}.zip'
    create_proxy_extension(proxy, plugin_file)
    chrome_options.add_extension(plugin_file)
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--mute-audio")

    # Set user agent if provided
    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    return driver

def run_selenium_with_proxy(proxy):
    arr = proxy.split(":")
    print(f"Using proxy: {arr[0]}:{arr[1]}")
    driver = get_chromedriver(arr, user_agent='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    driver.get(f'https://www.twitch.tv/{target_channel}')
    time.sleep(100) 
    driver.quit()

async def main():
    loop = asyncio.get_running_loop()
    
    with ThreadPoolExecutor(max_workers=amount) as executor:
        tasks = [loop.run_in_executor(executor, run_selenium_with_proxy, proxies[i]) for i in range(amount)]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    if len(sys.argv) != 1:
        target_channel = sys.argv[1]
        amount = min(amount, int(sys.argv[2]))
    asyncio.run(main())
    

