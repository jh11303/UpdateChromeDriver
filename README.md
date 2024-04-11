# Update Driver

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

## 协作方法

1、项目负责人分配编写任务（在[议题](http://192.168.72.242/testscriptUpdateDriver/-/issues)中，按周设置时间点）

2、任务执行人通过议题新建对应分支，在分支中完成任务代码编写，编写完成后提交合并至develop分支

    在`develop`分支上，新增 `feature_<人名>_<要编写的功能>`分支，例：`feature_ljl_addgroup`。
    再将分支代码拉取到本地

3、项目负责人每周完成分支合并审核，包括语法、规范

4、里程碑周期结束后，将develop分支合并至master分支，并验收代码

5、验收完成后通过master分支新建release分支，发布自动化测试代码版本

## 相关文档

- [ ] [Git拉取和上传方法](http://192.168.72.242/gitlab-instance-805f9c92/Monitoring/-/wikis/%E4%B8%8A%E4%BC%A0%E4%BB%A3%E7%A0%81%E5%88%B0%E6%8C%87%E5%AE%9A%E5%88%86%E6%94%AF)
- [ ] [Git回滚分支代码方法](http://192.168.72.242/gitlab-instance-805f9c92/Monitoring/-/wikis/%E5%9B%9E%E6%BB%9A%E6%8C%87%E5%AE%9A%E5%88%86%E6%94%AF%E4%BB%A3%E7%A0%81)
- [ ] [Git本地解决代码冲突问题](http://192.168.72.242/gitlab-instance-805f9c92/Monitoring/-/wikis/%E6%9C%AC%E5%9C%B0%E8%A7%A3%E5%86%B3%E4%BB%A3%E7%A0%81%E5%86%B2%E7%AA%81%E9%97%AE%E9%A2%98)
