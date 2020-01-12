import json
import multiprocessing #引入多进程加快抓取
import requests
import re
import urllib3
import time
from handler_insert_data import lagou_mysql
urllib3.disable_warnings()
class Handler_Lagou(object):
    def __init__(self):
        self.lagou_session=requests.session()
        self.header={
             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }
        self.city_list=""
    def handle_city(self):
        city_search=re.compile(r'www\.lagou\.com\/.*\/">(.*?)</a>')
        city_url='https://www.lagou.com/jobs/allCity.html'
        city_result=self.handle_request(method='GET',url=city_url)
        self.city_list=city_search.findall(city_result)
        self.lagou_session.cookies.clear()
    def handle_job(self,city):
        first_request_url="https://www.lagou.com/jobs/list_python?&px=default&city=%s"%city
        first_respose=self.handle_request(method='GET',url=first_request_url)
        totol_page_search=re.compile(r'class="span\stotalNum">(\d+)</span>')
        try:
            totol_page=totol_page_search.findall(first_respose)[0]
        except:
            return
        else:
            for i in range(1,int(totol_page)+1):
                data = {
                    "pn":i,
                    "kd":"python"
                }
                page_url="https://www.lagou.com/jobs/positionAjax.json?city=%s&needAddtionalResult=false"%city
                referer_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput=" % city
                # referer的URL需要进行encode
                self.header['Referer'] = referer_url.encode()
                response =self.handle_request(method='POST',url=page_url,data=data,info=city)
                lagou_data = json.loads(response)
                job_list = lagou_data['content']['positionResult']['result']
                for job in job_list:
                    lagou_mysql.insert_item(job)

    def handle_request(self,method,url,data=None,info=None):
        while True:
            try:
                if method == 'GET':
                  response = self.lagou_session.get(url=url, headers=self.header, verify=False,timeout=6)
                elif method == 'POST':
                  response = self.lagou_session.post(url=url, headers=self.header, verify=False, data=data,timeout=6)
                response.encoding = 'utf-8'
            except:
                self.lagou_session.cookies.clear()
                first_request_url = "https://www.lagou.com/jobs/list_python?&px=default&city=%s HTTP/1.1" % info
                self.handle_request(method="GET", url=first_request_url)
                time.sleep(10)
                continue
            if '频繁' in response.text:
                self.lagou_session.cookies.clear()
                first_request_url = "https://www.lagou.com/jobs/list_python?&px=default&city=%s HTTP/1.1" % info
                self.handle_request(method="GET", url=first_request_url)
                time.sleep(10)
                continue
            return response.text

if __name__ == '__main__':
    lagou=Handler_Lagou()
    lagou.handle_city()
    pool = multiprocessing.Pool(3)
    for city in lagou.city_list:
        pool.apply_async(lagou.handle_job,args=(city,))
    pool.close()
    pool.join()
