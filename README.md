# Update Chrome Driver

可直接更新当前用户下Python目录的浏览器驱动文件（目前支持Chrome）

## 使用方法

1. 通过python运行
   1. 双击运行 `active.bat`，自动部署python虚拟环境
   2. 运行 `update_driver.py`
      ```python
      venv/Scripts/python.exe python update_driver.py
      ```
2. 通过exe运行
   1. 双击运行 `dist/update_driver.exe`

## 打包方法

通过pyinstaller打包，需要预安装pyinstaller
``pip install pyinstaller``

在项目目录下，指定库目录，指定打包图标，打包exe
``pyinstaller --onefile --icon=chrome.ico -p venv\Lib\site-packages update_driver.py``
