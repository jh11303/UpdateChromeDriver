# -*- coding: utf-8 -*-
__date__ = '2024/4/1 14:00'
__file__ = 'update_driver.py'

import os
import sys
import json
import shutil
import platform
import requests
import subprocess


if platform.system() in 'Windows':
    from pathlib import Path


def make_dir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


def set_config():
    name = sys.argv[1] if len(sys.argv) >= 2 else "BaseConf"
    cls_config = {"BaseConf": BaseConf}
    return cls_config.get(name, BaseConf)


def path_join(folder, file):
    """路径拼接

    :param folder: 目录
    :param file: 文件名
    :return: 拼接后的路径
    """
    if platform.system() in 'Windows':
        res_path = Path(os.path.join(folder, file)).as_posix()
    else:
        res_path = os.path.join(folder, file)

    return res_path

class BaseConf(object):
    # 系统类型
    if platform.system().lower() == "darwin":
        SYS = "mac"
    elif platform.system().lower() == "windows":
        SYS = "win"
    else:
        SYS = "linux"

    # MAC os
    chrome_app = r"/Applications/Google\ Chrome.app/Contents/MacOS/"  # mac os chrome安装地址

    # Win
    chrome_reg = r"SOFTWARE\Google\Chrome\BLBeacon"  # win chrome注册表地址
    driver_url = "https://registry.npmmirror.com/-/binary/chrome-for-testing/"
    browser_ver = ''  # 浏览器版本号

    # 路径配置
    ROOT = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(ROOT)  # 驱动路径
    driver_dir = os.environ['python']
    driver_path = os.path.join(driver_dir, 'chromedriver.exe')
    system_type = "win64"


class Config(set_config()):
    pass


class Browser(object):
    @classmethod
    def get_browser_version(cls):
        # 自动检查Chrome版本号
        if Config.SYS == "mac":
            # OS X
            result = subprocess.Popen([r'{}/Google\ Chrome --version'.format(Config.chrome_app)],
                                      stdout=subprocess.PIPE, shell=True)
            chrome_version = [x.decode("utf-8") for x in result.stdout][0].strip().split(" ")[-1]
        elif Config.SYS == "win":
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, Config.chrome_reg)
                chrome_version = winreg.QueryValueEx(key, "version")[0]  # 查询注册表chrome版本号
            except Exception:
                raise Exception("查询注册表chrome版本失败!")
        else:
            # 设置firefox浏览器信息
            result = subprocess.Popen(['/usr/bin/firefox --version'], stdout=subprocess.PIPE, shell=True)
            chrome_version = [x.decode("utf-8") for x in result.stdout][0].strip().split(" ")[-1]
            Config.browser_ver = chrome_version
            return
        Config.browser_ver = chrome_version
        return chrome_version

    @classmethod
    def get_chromedriver_version(cls, chromedriver_path):
        if not os.path.exists(chromedriver_path):
            return None
        
        result = subprocess.run([chromedriver_path, "--version"], capture_output=True, text=True)
        chromedriver_version = result.stdout.split(' ')[1]
        return chromedriver_version

    @classmethod
    def check_version(cls, chrome_version, chromedriver_version):
        if chromedriver_version is None:
            return False
        chrome_major_version = chrome_version.split('.')[:-1]
        chromedriver_major_version = chromedriver_version.split('.')[:-1]
        return chrome_major_version == chromedriver_major_version

    @classmethod
    def search_ver(cls, version):
        if version == '':
            version = cls.get_browser_version()

        if version != "unknown":
            r = requests.get(Config.driver_url)
            data = json.loads(r.text)   # 获取所有版本号
            target_version = tuple(map(int, version.split('.')))
            versions = [tuple(map(int, item['name'].rstrip('/').split('.'))) for item in data]

            # 过滤出前三个部分与目标版本号一致，且最后一个部分小于目标版本号的版本
            filtered_versions = [version for version in versions if version[:3] == target_version[:3] and version[3] < target_version[3]]

            # 如果没有符合条件的版本，返回 None
            if not filtered_versions:
                return None
            else:
                # 在符合条件的版本中，找到最后一个部分最接近目标版本号的版本
                closest_version = max(filtered_versions, key=lambda version: version[3])
                return '.'.join(map(str, closest_version))

        return None

    @classmethod
    def gen_driver(cls, file_vr):
        file = f"chromedriver-{Config.system_type}.zip"
        url = f"{Config.driver_url}{file_vr}/{Config.system_type}/{file}"
        r = requests.get(url)
        with open(file, "wb") as f:
            f.write(r.content)
        cls.unzip_driver(file)
        os.remove(file)


    @classmethod
    def unzip_driver(cls, filename):
        if Config.SYS == "mac":
            # 解压zip
            os.system('cd {};unzip {}'.format(Config.root_dir, filename))
        elif Config.SYS == "win":
            cls.unzip_win(os.path.join(Config.root_dir, filename))
        else:
            pass

    @classmethod
    def change_driver_name(cls, version, filename):
        if Config.SYS == "mac":
            new_file = "{}_{}".format(filename, version)
        elif Config.SYS == "win":
            L = filename.split(".")
            new_file = "{}_{}.{}".format("".join(L[:-1]), version[0], L[-1])
        else:
            new_file = ""  # TODO
        os.rename(os.path.join(Config.driver_dir, filename),
                  os.path.join(Config.driver_dir, new_file))
        Config.DRIVER_PATH = os.path.join(Config.driver_dir, new_file)

    @classmethod
    def unzip_win(cls, filename):
        """unzip zip file"""
        # 解压文件
        shutil.unpack_archive(filename, extract_dir=Config.driver_dir)

        # 移动文件
        src_file = os.path.join(Config.driver_dir, f'chromedriver-{Config.system_type}', 'chromedriver.exe')
        dst_file = os.path.join(Config.driver_dir, 'chromedriver.exe')
        shutil.move(src_file, dst_file)

        # 删除目录
        dir_to_remove = os.path.join(Config.driver_dir, 'chromedriver-win64')
        shutil.rmtree(dir_to_remove)


if __name__ == '__main__':
    browser = Browser()
    driver_version = browser.get_chromedriver_version(Config.driver_path)
    browser_version = browser.search_ver('')
    if browser.check_version(browser_version, driver_version):
        print("Driver is up to date!")
    else:
        print("Driver is outdated! Updating...")
        browser.gen_driver(browser_version)
        print("Driver updated successfully!")
