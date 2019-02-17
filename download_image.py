# -*- coding: utf-8 -*-
import requests
import time
import os
import random
import json
import multiprocessing
import threading


class DownloadImage(object):

    def __init__(self):
        # 图片地址所在路径
        self.root_path = os.path.join(os.getcwd(), "img_url")
        # 图片保存的路径
        self.save_path = os.path.join(r"F:\MM131", "img")
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)

    def set_headers(self, referer):
        """
        设置请求头信息
        :param referer:请求头添加referer信息
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
            'Referer': referer
        }
        return headers

    def get_img_url(self, path):
        """
        获取图集信息
        :param path: 图片网址信息所在路径
        :return: 图片信息列表
        """
        img_info = []
        with open(path, 'r', encoding='utf-8') as img_file:
            for img_str in img_file.readlines():
                img_info.append(json.loads(img_str))
        return img_info

    def get_response(self, url, headers):
        """
        获取图片
        :param url:图片地址
        :param headers: 请求头
        :return: 图片
        """
        try:
            response = requests.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                return response
            else:
                print("图片：" + url + "下载错误")
                return None
        except Exception as e:
            print("图片：" + url + "下载异常")
            print(e)
            return None

    def save_img(self, path, pic):
        """
        保存图片
        :param path:图片保存的路径
        :param pic: 图片
        :return:
        """
        if not os.path.exists(path):
            with open(path, 'wb') as img:
                img.write(pic)
            print("图片" + path + "保存成功")
        else:
            print("图片" + path + "已存在")

    def download_img(self, pic_url, save_html_path, headers):
        """
        下载图片，并保存
        :param pic_url: 图片地址列表
        :param save_html_path: 图集路径
        :param headers: 请求头
        :return:
        """
        if not os.path.exists(save_html_path):
            os.mkdir(save_html_path)
        for img_url in pic_url:
            response = self.get_response(img_url, headers)
            if response:
                img_path = os.path.join(save_html_path, img_url.split('/')[-1])
                self.save_img(img_path, response.content)

    def get_html_name(self, html_names, class_path, class_name):
        """
        获取图片信息，并下载图片
        :param html_names:图集名称
        :param class_path:类别路径
        :param class_name:类别名称
        :return:
        """
        thread = []
        for html_name in html_names:
            img_info = self.get_img_url(os.path.join(class_path, html_name))[0]
            # print(img_info)
            num = img_info['num']
            title = img_info['title']
            referer = img_info['referer']
            pic_url = img_info['pic_url']
            headers = self.set_headers(referer)
            save_class_path = os.path.join(self.save_path, class_name)
            if not os.path.exists(save_class_path):
                os.mkdir(save_class_path)
            save_html_path = os.path.join(save_class_path, num + '、' + title)
            t = threading.Thread(target=self.download_img, args=(pic_url, save_html_path, headers,))
            thread.append(t)

        for t in thread:
            t.start()
        for t in thread:
            t.join()

    def main(self):
        """
        主函数
        :return:
        """
        class_names = os.listdir(self.root_path)
        print(class_names)
        pool = multiprocessing.Pool()
        for class_name in class_names:
            class_path = os.path.join(self.root_path, class_name)
            html_names = os.listdir(class_path)
            pool.apply_async(func=self.get_html_name, args=(html_names, class_path, class_name,))
        pool.close()
        pool.join()


if __name__ == '__main__':
    print(time.clock())
    xx = DownloadImage()
    xx.main()
    import datetime
    print(datetime.timedelta(seconds=time.clock()))
