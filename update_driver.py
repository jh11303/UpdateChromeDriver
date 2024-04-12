# -*- coding: utf-8 -*-


import os
import json
import shutil
import winreg
import platform
import requests
import subprocess


class BaseConf:
    SYS = platform.system().lower() # Get the system type
    chrome_reg = r"SOFTWARE\Google\Chrome\BLBeacon" # Chrome registry path
    driver_url = "https://registry.npmmirror.com/-/binary/chrome-for-testing/"  # Chromedriver download URL
    ROOT = os.path.dirname(os.path.abspath(__file__))   # Get the root directory
    root_dir = os.path.join(ROOT)   # Get the root directory
    driver_name = "chromedriver.exe"    # Chromedriver name
    driver_dir = os.environ.get('python', '')   # Chromedriver directory
    driver_path = os.path.join(driver_dir, driver_name)  # Chromedriver path
    system_type = "win64"   # System type


class Browser:
    @staticmethod
    def get_browser_version():
        # Get the version of the installed Chrome browser
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, BaseConf.chrome_reg)
            chrome_version = winreg.QueryValueEx(key, "version")[0]
        except Exception:
            raise Exception("Failed to query chrome version from registry!")

        # Return the version of the installed Chrome browser
        return chrome_version

    @staticmethod
    def get_chromedriver_version(chromedriver_path):
        # Get the version of the installed chromedriver
        if not os.path.exists(chromedriver_path):
            return None

        # Get the version of the installed chromedriver
        result = subprocess.run([chromedriver_path, "--version"], capture_output=True, text=True)
        chromedriver_version = result.stdout.split(' ')[1]

        # Return the version of the installed chromedriver
        return chromedriver_version

    @staticmethod
    def check_version(chrome_version, chromedriver_version):
        # Check if the chromedriver is up to date
        if chromedriver_version is None:
            return False
        chrome_major_version = chrome_version.split('.')[:-1]
        chromedriver_major_version = chromedriver_version.split('.')[:-1]

        # Check if the major version of the chromedriver is the same as the installed Chrome browser
        return chrome_major_version == chromedriver_major_version

    @staticmethod
    def search_latest_chromedriver_version():
        # Get the version of the installed Chrome browser
        version = Browser.get_browser_version()

        # Get the latest version of the chromedriver
        r = requests.get(BaseConf.driver_url)
        data = json.loads(r.text)
        target_version = tuple(map(int, version.split('.')))
        versions = [tuple(map(int, item['name'].rstrip('/').split('.'))) for item in data]

        # Filter out the versions that are not compatible with the installed Chrome browser
        filtered_versions = [version for version in versions if version[:3] == target_version[:3] and version[3] < target_version[3]]

        # If no version is found, return None
        if not filtered_versions:
            return None
        else:
            closest_version = max(filtered_versions, key=lambda version: version[3])
            return '.'.join(map(str, closest_version))


    @staticmethod
    def get_driver(file_vr):
        # Download the chromedriver
        zip_file = f"chromedriver-{BaseConf.system_type}.zip"
        url = f"{BaseConf.driver_url}{file_vr}/{BaseConf.system_type}/{zip_file}"
        r = requests.get(url)
        with open(zip_file, "wb") as f:
            f.write(r.content)

        # Unzip the chromedriver
        Browser.unzip_driver(os.path.join(BaseConf.root_dir, zip_file))
        os.remove(zip_file)

    @staticmethod
    def unzip_driver(filename):
        # Unzip the chromedriver
        shutil.unpack_archive(filename, extract_dir=BaseConf.driver_dir)
        src_file = os.path.join(BaseConf.driver_dir, f'chromedriver-{BaseConf.system_type}', BaseConf.driver_name)
        dst_file = os.path.join(BaseConf.driver_dir, BaseConf.driver_name)

        # Move the chromedriver to the driver directory
        shutil.move(src_file, dst_file)
        dir_to_remove = os.path.join(BaseConf.driver_dir, f'chromedriver-{BaseConf.system_type}')

        # Remove the extracted directory
        shutil.rmtree(dir_to_remove)


if __name__ == '__main__':
    # Check if the chromedriver is up to date
    browser = Browser()
    local_driver_version = browser.get_chromedriver_version(BaseConf.driver_path)
    latest_driver_version = browser.search_latest_chromedriver_version()
    if browser.check_version(latest_driver_version, local_driver_version):
        print("Driver is up to date!")
    else:
        print("Driver is outdated! Updating...")
        browser.get_driver(latest_driver_version)
        print("Driver updated successfully!")
