#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import django
import os
import jieba
from jieba import analyse
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weibo_web.settings")
django.setup()
from django.conf import settings as django_settings
from myapp.models import *
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  zhphuang
@data    2018-04-21 
"""
# -*- coding: utf-8 -*-

from selenium import webdriver
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from collections import Counter
import sys
import time
import re
import requests
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
    StaleElementReferenceException,
    InvalidElementStateException
)


def gen_browser(driver_path):
    '''实例化一个driver'''
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('disable-infobars')
    options.add_argument("--disable-plugins-discovery")
    user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"
    options.add_argument('user-agent="{0}"'.format(user_agent))

    def send(driver, cmd, params={}):
        '''
        向调试工具发送指令
        from: https://stackoverflow.com/questions/47297877/to-set-mutationobserver-how-to-inject-javascript-before-page-loading-using-sele/47298910#47298910
        '''
        resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
        url = driver.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = driver.command_executor._request('POST', url, body)
        if response['status']:
            raise Exception(response.get('value'))
        return response.get('value')
    def add_script(driver, script):
        '''在页面加载前执行js'''
        send(driver, "Page.addScriptToEvaluateOnNewDocument", {"source": script})
    # 给 webdriver.Chrome 添加一个名为 add_script 的方法
    webdriver.Chrome.add_script = add_script # 这里（webdriver.Chrome）可能需要改，当调用不同的驱动时

    browser = webdriver.Chrome(
        executable_path=driver_path,
        chrome_options=options
    )
    # ################## 辅助调试 *********************
    existed = {
        'executor_url': browser.command_executor._url,  # 浏览器可被远程连接调用的地址
        'session_id': browser.session_id  # 浏览器会话ID
    }
    # pprint(existed)
    # ********************* 辅助调试 ##################
    # ############### 专业造假 ***************************
    browser.add_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
    });
    window.navigator.chrome = {
        runtime: {},
    };
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-CN', 'zh']
    });
    Object.defineProperty(navigator, 'plugins', {
        get: () => [0, 1, 2],
    });
    """)
    # *************** 专业造假 ###################

    return browser

class Spider(object):
    """
    爬取类
    """
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        # self.browser = webdriver.Chrome(self._getdriverpath(), chrome_options=options)
        driver_path = django_settings.DRIVER_PATH
        self.browser = gen_browser(driver_path)
        # 打开登录页
        self.browser.get(r'https://passport.weibo.cn/signin/login')  # 打开页面
        # 等待页面加载到可以找到元素
        try:
            element = WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#loginName"))
            )
        except:
            # import ipdb; ipdb.set_trace()
            self.browser.quit()
        time.sleep(3)
        # 获取用户名输入框
        e_username = self.browser.find_element_by_id('loginName')
        # 清空现有用户名
        e_username.clear()
        # 输入用户名
        e_username.send_keys("18798306616")

        # 获取密码输入框
        e_password = self.browser.find_element_by_id('loginPassword')
        # 清空现有密码
        e_password.clear()
        # 输入密码
        e_password.send_keys('wnp62682')

        # 触发登录按钮点击
        self.browser.find_element_by_id('loginAction').click()
        self.browser.implicitly_wait(5) # 隐性等待
        self.browser.maximize_window() # 窗口最大化

    def get_data(self):
        while True:
            # 1. 滚动加载完所有页面
            while True:
                self.browser.execute_script('window.scrollTo({top: document.body.scrollHeight + 10, behavior: "smooth"})')
                time.sleep(5)
                if not bool(self.browser.find_elements_by_xpath('//*[@class="text"][text()[contains(.,"正在加载中，请稍候...")]]')):
                    break
            # js文件夹
            js_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_js')
            # 注入jquery
            with open(os.path.join(js_folder, 'jquery-1.12.4.min.js'), 'rt', encoding='utf-8') as jqf:
                self.browser.execute_script(jqf.read())
            time.sleep(0.9)
            # 注入jquery-xpath
            with open(os.path.join(js_folder, 'jquery.xpath.min.js'), 'rt', encoding='utf-8') as jqxf:
                self.browser.execute_script(jqxf.read())
            time.sleep(0.5)
            # 2. 所有折叠的内容展开
            js_code = '''
            var $weibo_area = $('.WB_feed[node-type="feed_list"]');
            $weibo_area.xpath('//*[@class="WB_text_opt"][text()[contains(.,"展开全文")]]').each(function() {
                var $self = $(this);
                $self[0].click(); // 此处, 取到dom元素点击才有效, trigger('click')方式无效
                setTimeout(function() {
                    $self.remove(); // 已经展开，不要了，移除
                }, 250);
            });
            '''
            self.browser.execute_script(js_code)
            time.sleep(1.5)
            # 微博区域
            weibo_area = self.browser.find_element_by_css_selector('.WB_feed[node-type="feed_list"]')
            # 处理每一条微博
            weibos = weibo_area.find_elements_by_css_selector('.WB_feed_detail[node-type="feed_content"]')
             
            # 声明对象
            obj = self.model_name()
            for weibo in weibos:
                # 得到文本内容
                text_list = weibo.find_elements_by_xpath('//*[@class="WB_text W_f14"]')
                # 链接
                link_lst = weibo.find_elements_by_css_selector('a[action-type="feed_list_url"]')
                if bool(link_lst):
                    for link in link_lst:
                        link = link.get_property('href')
                else:
                    continue
                    link_lst = weibo.find_elements_by_css_selector('a[extra-data="type=topic"]')
                    if bool(link_lst):
                        for link in link_lst:
                            link = link.get_property('href')
                            obj.link = link
                    else:
                        continue
                print(link)
                    
            for t in text_list:                       
                # title【匹配规则】
                pattern_title1 = r'【([^】]+)】'
                pattern_title2 = r'#([^#]+)#'

                # 内容的【匹配规则】
                pattern_content = r''
                if t.text.find('#') == 0:
                    t_lst = re.findall(pattern_title2, t.text)
                else:
                    t_lst = re.findall(pattern_title1, t.text)
                if bool(t_lst):
                    title = re.sub(r'#','', t_lst[0])
                    obj.title = title
                    print(title)
                # 内容
                try:
                    content = t.text.split('】')[1]
                    content = content[:content.rfind('。')]
                    obj.content = content
                    print(content)
                    # print(title+content)
                except IndexError:
                    continue
                self.analyze(obj.title+"," + obj.content)
                         
            #　转发量
            ｈ_lst = self.browser.find_elements_by_css_selector('.pos .line[node-type="forward_btn_text"]')
            for h in h_lst:
                h = h.text[1:]
                obj.send_count = h
                # print(h)
                # print('*'*50)
            obj.save()
            # 如果有下一页，进入下一页, 否则就结束循环
            if not self.go_next_if_exists():
                break


    def go_next_if_exists(self):
        '''判断是否存在下一页'''
        try:
            page = self.browser.find_element_by_class_name('W_pages').find_element_by_link_text('下一页')
            page.click()
            time.sleep(3)
            return True
        except NoSuchElementException:
            print("亲！已经是最后一页了")
            return False

    def quit(self):
        self.browser.close()

    def analyze(self, description):
        folder = os.path.dirname(os.path.abspath(__file__))
        # import ipdb;ipdb.set_trace()
        jieba.analyse.set_stop_words(os.path.join(folder, 'stop_words.txt'))
        stop_dict = {}
        content = open("stop_words.txt", "rb").read().decode('utf-8')
        for wd in content.split('\n'):
            stop_dict[wd] = 1
        tk = jieba.cut(description, cut_all=True)
        data = dict(Counter(tk))

        pat = re.compile(r'\d')
        keywords = {}
        for key, value in data.items():
            if key and not pat.search(key) and key not in stop_dict and len(key)>=2:
                if key in keywords:
                    keywords[key] += value
                else:
                    keywords[key] = value
        return keywords

    def _getdriverpath(self):
        # path = 'C://chromedriver.exe'
        path = "F:\数据挖掘技术与应用\智联招聘数据\chromedriver.exe"
        return path


class SpiderFHW(Spider):
    def __init__(self):
        super(SpiderFHW, self).__init__()
        self.url = "https://weibo.com/phoenixnewmedia"
        self.browser.get(self.url)
        time.sleep(5)
        self.model_name = FHWModel

    def analyze(self, description):
        keywords = super(SpiderFHW, self).analyze(description)
        print("keyword:%s\n" % keywords)
        for key, counter in keywords.items():
            obj, is_create = FHWKeyWordsModel.objects.get_or_create(keyword=key, defaults = {"weight_count": counter})
            if not is_create:
                obj.weight_count += counter
                obj.save()


class SpiderZhihu(Spider):
    def __init__(self):
        super(SpiderZhihu, self).__init__()

        self.url = "https://weibo.com/zhihu" 
        self.browser.get(self.url)
        time.sleep(20)
        self.model_name = ZhihuModel

    def analyze(self, description):
        keywords = super(SpiderZhihu, self).analyze(description)
        print("keyword:%s\n" % keywords)
        for key, counter in keywords.items():
            obj, is_create = ZhihuKeyWordsModel.objects.get_or_create(keyword=key, defaults = {"weight_count": counter})
            if not is_create:
                obj.weight_count += counter
                obj.save()


class SpiderSinapapers(Spider):
    def __init__(self):
        super(SpiderSinapapers, self).__init__()
        self.url = "https://weibo.com/sinapapers" 
        self.browser.get(self.url)
        time.sleep(20)
        self.model_name =SinapapersModel

    def analyze(self, description):
        keywords = super(SpiderSinapapers, self).analyze(description)
        print("keyword:%s\n" % keywords)
        for key, counter in keywords.items():
            obj, is_create = SinapapersKeyWordsModel.objects.get_or_create(keyword=key, defaults = {"weight_count": counter})
            if not is_create:
                obj.weight_count += counter
                obj.save()


class SpiderCCTVxinwen(Spider):
    def __init__(self):
        super(SpiderCCTVxinwen, self).__init__()
        self.url = "https://weibo.com/cctvxinwen"
        self.browser.get(self.url)
        time.sleep(20)
        self.model_name = CCTVxinwenModel

    def analyze(self, description):
        keywords = super(SpiderCCTVxinwen, self).analyze(description)
        print("keyword:%s\n" % keywords)
        for key, counter in keywords.items():
            obj, is_create = CCTVxinwenKeyWordsModel.objects.get_or_create(keyword=key, defaults = {"weight_count": counter})
            if not is_create:
                obj.weight_count += counter
                obj.save()


class SpiderFHWFans(Spider):
    def __init__(self):
        # analogLogin()
        super(SpiderFHWFans, self).__init__()
        self.url = "https://weibo.cn/2803301701/fans"
        self.browser.get(self.url)
        time.sleep(20)

        self.cookie = {}
        for item2 in self.browser.get_cookies():
            self.cookie[item2["name"]] = item2["value"]

    def get_data(self):
        current_page = 1
        while current_page < 20:
            self.browser.get("%s?page=%s" % (self.url, current_page))
            bs = BeautifulSoup(self.browser.page_source, "html.parser")
            table_list = bs.select("div.c table tbody")
            for item in table_list:
                try:
                    href = item.select("tr td")[0].select("a")[0].attrs["href"]
                    group = re.search(r'https://weibo.cn/u/(.*)', href)
                    try:
                        fan_id = group.group(1)
                        href = "https://weibo.cn/{0}/info".format(fan_id)
                    except AttributeError:
                        pass
                    headers = {
                            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                            "Accept-Encoding":"gzip, deflate, sdch, br",
                            "Accept-Language":"zh-CN,zh;q=0.8",
                            "Referer":href,
                            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
                    }
                    print(href)
                    res = requests.get(href, headers=headers, cookies = self.cookie)
                    bs2 = BeautifulSoup(res.text, "html.parser")
                    # import ipdb; ipdb.set_trace()
                    try:
                        info = bs2.select("body div.c")[3].text
                    except IndexError:
                        pass
                    print(info)
                    group = re.search(r'昵称:(.*?)性别:(.*?)地区:(.*)', info)
                    # print(info)
                    obj = FHWFansModel()
                    obj.nickname = group.group(1)
                    obj.sex = group.group(2)
                    obj.location = group.group(3)[:5]
                    obj.save()
                except AttributeError:
                    pass
                    # print(traceback.format_exc())
                    # print(e)
            current_page += 1



if __name__ == '__main__':
    SpiderFHW().get_data()
    SpiderZhihu().get_data()
    SpiderSinapapers().get_data()
    SpiderCCTVxinwen().get_data()
    a = SpiderFHWFans()
    a.get_data()
    a.browser.close()
    # i = 0
    # while i < 10:
    #     a.get_data()
    #     i += 1
    # a.browser.close()