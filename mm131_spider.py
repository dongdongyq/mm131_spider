# -*- coding: utf-8 -*-
import requests
import time
import os
import random
import json
import threading
from bs4 import BeautifulSoup


class MM131Spider(object):

    def __init__(self):
        self.headers = self.set_headers()
        self.url = 'http://www.mm131.com/'
        # 图片信息保存的地址
        self.img_url_path = os.path.join(os.getcwd(), "img_url")
        if not os.path.exists(self.img_url_path):
            os.mkdir(self.img_url_path)

    def set_headers(self):
        """
        设置请求头信息
        :return:请求头
        """
        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        ]
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
        }
        return headers

    def get_page(self, url=None):
        """
        发起请求并返回页面
        :param url: 要爬取得网站
        :return: 网页源码
        """
        if not url:
            url = self.url
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                response.encoding = 'gb2312'
                return response
            else:
                print("返回异常网址：", url)
                print("返回异常：", response.status_code)
                return None
        except Exception as e:
            print("请求异常网址：", url)
            print(e)
            return None

    def get_soup_content(self, response):
        """
        获取网页源码，并使用bs4解析
        :param response:响应
        :return:解析后的网页
        """
        content = response.text
        soup_content = BeautifulSoup(content, 'lxml')
        return soup_content

    def get_all_class(self, soup_content):
        """
        获取所有类别名称和地址
        :param soup_content:解析后的网页源码
        :return:分类信息列表
        """
        class_info = []
        class_div = soup_content.find('div', {'class': 'nav'})
        class_list = class_div.find_all('a')
        for cl in class_list[1:]:
            class_info.append([cl.text, cl.get('href')])
        return class_info

    def get_num(self, cl_info):
        """
        获取图集总页数及所对应的类别编号、名称及网址，保存到字典中
        :param cl_info:分类信息列表
        :return:
        """
        class_info = {}
        response = self.get_page(cl_info[1])
        soup_content = self.get_soup_content(response)
        dl = soup_content.find("dl", {"class": "list-left"})
        dd_list = dl.find_all("dd")
        page_str = dd_list[-1].find_all('a')[-1].get('href')
        class_num = page_str.split('_')[1]
        class_page = int(page_str.split('.')[0].split('_')[-1])
        class_info['class_num'] = class_num
        class_info['class_name'] = cl_info[0]
        class_info['class_url'] = cl_info[1]
        class_info['class_page'] = class_page
        class_path = os.path.join(self.img_url_path, class_num + '、' + cl_info[0])
        if not os.path.exists(class_path):
            os.mkdir(class_path)
        print(class_info)
        self.get_all_html(class_info)

    def get_one_html(self, next_html_url, class_info):
        """
        获取某个类别下的某页所有图集地址
        :param next_html_url: 某类下的下一页网址
        :param class_info: 某类的详细信息
        :return:
        """
        thread = []
        response = self.get_page(next_html_url)
        soup_content = self.get_soup_content(response)
        dl = soup_content.find("dl", {"class": "list-left"})
        dd_list = dl.find_all("dd")
        for dd in dd_list[:-1]:
            html_url = dd.find('a').get('href')
            print(html_url)
            t = threading.Thread(target=self.save_img_info, args=(html_url, class_info,))
            thread.append(t)
        for t in thread:
            t.start()
        for t in thread:
            t.join()

    def get_all_html(self, class_info):
        """
        获取某个类别下的所有图集信息
        :param class_info: 某类下的详细信息
        :return:
        """
        thread = []
        class_page = class_info['class_page']
        class_url = class_info['class_url']
        class_num = class_info['class_num']
        for page in range(1, class_page):
            if page == 1:
                next_html_url = class_url
            else:
                next_html_url = class_url + "list_" + class_num + "_" + str(page) + ".html"
            t = threading.Thread(target=self.get_one_html, args=(next_html_url, class_info,))
            thread.append(t)
        for t in thread:
            t.start()
        for t in thread:
            t.join()

    def get_all_pic(self, soup_content, url):
        """
        获取图集下所有图片信息，并写入文件
        :param url: 图集地址
        :param soup_content: 图集所对应的解析后源码
        :return:图片地址等信息
        """
        # 图片信息
        pic_info = {}
        pic_url = []
        pic_info['num'] = url.split('/')[-1].split('.')[0]
        title = soup_content.find('h5').text
        pic_div = soup_content.find('div', {'class': 'content-pic'})
        img_url = pic_div.find('img').get('src').split('/')[:-1]
        img_url = ('/').join(img_url)
        # print(img_url)
        page_div = soup_content.find('div', {'class': 'content-page'})
        pic_num = int(page_div.find('span').text[1:-1])
        # print(pic_num)
        for i in range(1, pic_num+1):
            pic_url.append(img_url + '/' + str(i) + '.jpg')
        # print(pic_url)
        pic_info['title'] = title
        pic_info['referer'] = url
        pic_info['pic_url'] = pic_url
        # print(pic_info)
        return pic_info

    def save_pic_url(self, pic_info, class_info):
        """
        保存图片信息到文件
        :param pic_info: 图片信息
        :param class_info: 类别信息
        :return:
        """
        img_path = os.path.join(os.getcwd(), "img_url")
        if not os.path.exists(img_path):
            os.mkdir(img_path)
        class_path = os.path.join(img_path, class_info['class_num'] + '、' + class_info['class_name'])
        if not os.path.exists(class_path):
            os.mkdir(class_path)
        html_path = os.path.join(class_path, str(pic_info['num']) + '、' + pic_info['title'] + '.txt')
        with open(html_path, 'w', encoding='utf-8') as pic_file:
            pic_str = json.dumps(pic_info, ensure_ascii=False)
            # print(pic_str)
            pic_file.write(pic_str + '\n')

    def save_img_info(self, html_url, class_info):
        """
        获取图集下的所有图片地址，并保存到文件
        :param html_url: 图集网址
        :param class_info: 类别信息
        :return:
        """
        response = self.get_page(html_url)
        soup_content = self.get_soup_content(response)
        pic_info = self.get_all_pic(soup_content, html_url)
        self.save_pic_url(pic_info, class_info)

    def main(self):
        """
        主函数
        :return:
        """
        thread = []
        # 获取首页内容
        response = self.get_page()
        # 解析首页内容
        soup_content = self.get_soup_content(response)
        # 获取首页下分类信息
        cl_info = self.get_all_class(soup_content)
        print(cl_info)
        for i in range(6):
            print(cl_info[i])
            # 获取每一类下的所有图集信息
            t = threading.Thread(target=self.get_num, args=(cl_info[i],))
            thread.append(t)
        for t in thread:
            t.start()
        for t in thread:
            t.join()


# mm131_spider = MM131Spider()
#
#
# def main(i):
#     # 获取首页内容
#     response = mm131_spider.get_page()
#     # 解析首页内容
#     soup_content = mm131_spider.get_soup_content(response)
#     # 获取首页下分类信息
#     cl_info = mm131_spider.get_all_class(soup_content)
#     # 获取每一类下的所有图集信息
#     mm131_spider.get_num(cl_info[i])


if __name__ == '__main__':
    print(time.clock())
    xx = MM131Spider()
    xx.main()
    import datetime
    print(datetime.timedelta(seconds=time.clock()))

