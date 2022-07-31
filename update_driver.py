# -*- coding: utf-8 -*-
__date__ = '2022/3/4 14:00'
__file__ = 'update_driver.py'

import os
import re
import sys
import zipfile
import platform
import requests
import subprocess
from bs4 import BeautifulSoup


if platform.system() in 'Windows':
    from pathlib import Path


def make_dir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


def set_config():
    name = sys.argv[1] if len(sys.argv) >= 2 else "BaseConf"
    cls_config = {"BaseConf": BaseConf, "SearchConf": TiebaConf}
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
    driver_url = "https://npm.taobao.org/mirrors/chromedriver/"

    # 路径配置
    ROOT = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(ROOT)  # 驱动路径
    driver_dir = os.environ['PYTHON']


class TiebaConf(BaseConf):
    url = "http://tieba.baidu.com"  # 测试百度贴吧配置


class Config(set_config()):
    pass


class Browser(object):
    @classmethod
    def set_browser(cls):
        # 自动检查Chrome版本号
        if Config.SYS == "mac":
            # OS X
            result = subprocess.Popen([r'{}/Google\ Chrome --version'.format(Config.chrome_app)],
                                      stdout=subprocess.PIPE, shell=True)
            version = [x.decode("utf-8") for x in result.stdout][0].strip().split(" ")[-1]
        elif Config.SYS == "win":
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, Config.chrome_reg)
                version = winreg.QueryValueEx(key, "version")[0]  # 查询注册表chrome版本号
            except Exception:
                raise Exception("查询注册表chrome版本失败!")
        else:
            # 设置firefox浏览器信息
            result = subprocess.Popen(['/usr/bin/firefox --version'], stdout=subprocess.PIPE, shell=True)
            version = [x.decode("utf-8") for x in result.stdout][0].strip().split(" ")[-1]
            Config.browser_ver = version
            return
        Config.browser_ver = version
        file_vr = cls.search_ver(version)
        if file_vr is None:
            raise Exception("未获取到chrome版本号! 请检查!")
        status, file = cls.check_driver(file_vr)
        if not status:
            cls.gen_driver(file_vr)
        else:
            print("系统已存在chromedriver, 无需下载!")
            Config.DRIVER_PATH = os.path.join(Config.driver_dir, file)

    @classmethod
    def check_driver(cls, version):
        status, filename = False, None
        make_dir(Config.driver_dir)  # check driver_dir
        for root, dirs, files in os.walk(Config.driver_dir):
            for file in files:
                if version not in file:
                    try:
                        os.remove(os.path.join(root, file))
                    except:
                        pass
                else:
                    status, filename = True, file
        return status, filename

    @classmethod
    def search_ver_v2(cls, version):
        ver = ".".join(version.split(".")[:2])
        r = requests.get(Config.driver_url)
        bs = BeautifulSoup(r.text, features='html.parser')
        rt = [x for x in bs.select("pre a")]
        if not rt:
            raise Exception("可能淘宝镜像挂了，请重试")
        for x in rt:
            if x.text.startswith(ver):
                return x.text.rstrip("/")
        else:
            raise Exception("没有找到当前版本的合适驱动: {}".format(version))

    @classmethod
    def search_ver(cls, version):
        if version != "unknown":
            number = version.split(".")[0]
            file_vr = None
            url = Config.driver_url + "LATEST_RELEASE"
            r = requests.get(url)
            bs = BeautifulSoup(r.text, 'html.parser')
            latest = bs.text.strip()
            record = "{}/{}/notes.txt".format(Config.driver_url, latest)
            info = requests.get(record)
            text = info.text
            vr = re.findall(r"-+ChromeDriver\s+(\d+\.\d+\.\d+\.\d+)", text)
            br = re.findall(r"Supports\s+Chrome\s+version\s+(\d+\d+)", text)
            if not br:
                return cls.search_ver_v2(version)
            # for v, b in zip(vr, br):
            #     small, bigger = b.split("-")
            #     if int(small) <= int(number) <= int(bigger):
            #         # 找到版本号
            #         print("找到浏览器对应驱动版本号: {}".format(v))
            #         file_vr = v
            #         break
            return vr

    @classmethod
    def gen_driver(cls, file_vr):
        if Config.SYS == "mac":
            file = "chromedriver_mac64.zip".format(file_vr)
            driver = "chromedriver"
        elif Config.SYS == "win":
            file = "chromedriver_win32.zip".format(file_vr)
            driver = "chromedriver.exe"
        else:
            file = "chromedriver_linux64.zip".format(file_vr)
            driver = "chromedriver"
        # url = "{}{}/{}".format(Config.driver_url, file_vr[0], file)
        r = requests.get("{}{}/{}".format(Config.driver_url, file_vr[0], file))
        with open(file, "wb") as f:
            f.write(r.content)
        cls.unzip_driver(file)
        # cls.change_driver_name(file_vr, driver)
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
        with zipfile.ZipFile(filename) as f:
            for names in f.namelist():
                f.extract(names, Config.driver_dir)


if __name__ == '__main__':
    browser = Browser()
    vr = browser.search_ver('')
    browser.gen_driver(vr)

