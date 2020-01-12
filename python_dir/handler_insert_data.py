from create_lagou_table import Lagoutables
from create_lagou_table import Session
import time
class HandlerLagouData(object):
    def __init__(self):
        self.mysql_session = Session()
    def insert_item(self,item):
        date = time.strftime("%Y-%m-%d",time.localtime())
        data = Lagoutables(
            # 岗位ID
            positionID=item['positionId'],
            # 经度
            longitude=item['longitude'],
            # 纬度
            latitude=item['latitude'],
            # 岗位名称
            positionName=item['positionName'],
            # 工作年限
            workYear=item['workYear'],
            # 学历
            education=item['education'],
            # 岗位性质
            jobNature=item['jobNature'],
            # 公司类型
            financeStage=item['financeStage'],
            # 公司规模
            companySize=item['companySize'],
            # 业务方向
            industryField=item['industryField'],
            # 所在城市
            city=item['city'],
            # 岗位标签
            positionAdvantage=item['positionAdvantage'],
            # 公司简称
            companyShortName=item['companyShortName'],
            # 公司全称
            companyFullName=item['companyFullName'],
            # 公司所在区
            district=item['district'],
            # 公司福利标签
            companyLabelList=','.join(item['companyLabelList']),
            salary=item['salary'],
            # 抓取日期
            crawl_date=date
        )
        query_result = self.mysql_session.query(Lagoutables).filter(Lagoutables.crawl_date==date,Lagoutables.positionID==item['positionId']).first()
        if query_result:
            print('该岗位信息已经存在%s:%s:%s'%item['positionId'],item['city'],item['positionId'])
        else:
            self.mysql_session.add(data)
            print('insert:%s'%item['positionId'])
            self.mysql_session.commit()
lagou_mysql=HandlerLagouData()