# -*- coding: cp936 -*-
import MySQLdb
from mysqldb import ImgMysql
from hbcdb import HbcOrc
from kakoudb import KakouOrc
from inicof import HbcIni
##from disk import DiskState
import logging
import logging.handlers
import time,datetime,os
import re
import gl
import urllib

def getTime():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def initLogging(logFilename):
    """Init for logging"""
    path = os.path.split(logFilename)
    if os.path.isdir(path[0]):
        pass
    else:
        os.makedirs(path[0])
    logging.basicConfig(
                    level    = logging.DEBUG,
                    format   = '%(asctime)s %(filename)s[line:%(lineno)d] [%(levelname)s] %(message)s',
                    datefmt  = '%Y-%m-%d %H:%M:%S',
                    filename = logFilename,
                    filemode = 'a');
    
class HbcCenter:
    def __init__(self,trigger=('',1)):
        #print 'Welcome to %s'%version()
        self.trigger = trigger
        self.style_red = 'size=4 face=arial color=red'
        self.style_blue = 'size=4 face=arial color=blue'
        self.style_green = 'size=4 face=arial color=green'
        initLogging(r'log\hbcview.log')
        
        self.hbcIni = HbcIni()
        mysqlset = self.hbcIni.getMysql()
        hbcset   = self.hbcIni.getHbc()
        kakouset = self.hbcIni.getKakou()
        systset  = self.hbcIni.getSyst()
        
        self.imgMysql = ImgMysql(mysqlset['host'],mysqlset['user'],mysqlset['passwd'])
        self.kakouorc = KakouOrc(kakouset['host'],kakouset['user'],kakouset['passwd'],kakouset['sid'])
        self.hbcorc = HbcOrc(hbcset['host'],hbcset['user'],hbcset['passwd'],hbcset['sid'])
        self.hpzl  = {'01':u'黄牌','02':u'蓝牌','06':u'黑牌','16':u'学','15':u'挂'}
        self.hpys  = {'0':u'白牌','1':u'黄牌','2':u'蓝牌','3':u'黑牌','4':u'其他'}
        self.hpys2 = {'0':u'白底黑字','1':u'黄底黑字','2':u'蓝底白字','3':u'黑底白字','4':u'其他'}
        self.hpys3 = {'0':'00','1':'01','2':'02','3':'06','4':'00'}
        self.address = {'00000084':u'惠州惠城区东江大桥','00000096':u'惠州惠城区交警支队','00000094':u'惠州惠城区东湖路'}
        self.floder = {'00000084':u'303','00000096':u'302','00000094':u'301'}
        self.fxbh = {'SN':u'南向北','NS':u'北向南','EW':u'东向西','WE':u'西向东','IN':u'进城','OT':u'出城'}
        self.fxbh2 = {'00000084':{'SN':u'南向北','NS':u'北向南','EW':u'东向西','WE':u'西向东','IN':u'东向西','OT':u'西向东'},
                     '00000096':{'SN':u'南向北','NS':u'北向南','EW':u'东向西','WE':u'西向东','IN':u'东向西','OT':u'西向东'},
                     '00000094':{'SN':u'南向北','NS':u'北向南','EW':u'东向西','WE':u'西向东','IN':u'东向西','OT':u'西向东'}}        
        self.whitelist = set(['粤AE3Q73','粤LB1813','粤AW8G49','粤LXX266'])
        self.imgpath  = systset['imgpath']
        self.timeflag = systset['time']
        
        self.loginmysqlflag = True
        self.loginhbcorcflag = True
        self.loginkakouorcflag = True
        self.loginmysqlcount = 0
        self.loginhbccount = 0
        self.loginkakoucount = 0
        self.path = ''
        self.name = ''
            
    def __del__(self):
        del self.imgMysql
        del self.kakouorc
        del self.hbcorc

    def loginMysql(self):
        self.imgMysql.login()    
            
    def loginKakouOrc(self):
        self.kakouorc.login()

    def loginHbcOrc(self):
        self.hbcorc.login()

    #创建文件夹
    def makedirs(self,path):
        try:
            if os.path.isdir(path):
                pass
            else:
                os.makedirs(path)
        except IOError,e:
            print e
            logging.exception(e)
            raise
        
    #根据URL地址获取图片到本地
    def getImgByUrl(self,url,path,name):
        try:
            local = os.path.join(self.path,self.name+'.jpg')
            urllib.urlretrieve(url,local)
        except IOError,e:
            print e
            if e[0]== 2 or e[0]==22:
                self.name = self.name.replace('*','_').replace('?','_').replace('|','_').replace('<','_').replace('>','_').replace('/','_').replace('\\','_')
                self.makedirs(path)
                local = os.path.join(self.path,self.name+'.jpg')
                urllib.urlretrieve(url,local)
            else:
                raise

    def addHbc(self,values):
        try:
            self.imgMysql.addHbc(values)
        except MySQLdb.Error,e:
            self.loginmysqlflag = True
            self.loginmysqlcount = 0
            raise

    def getPlateInfo(self,t1,t2):
        try:
            return self.kakouorc.getPlateInfo(t1,t2)
        except Exception,e:
            self.loginhbcorcflag = True
            self.loginhbccount = 0
            raise

    def getHbcFromKakou(self,hphm,hpzl):
        try:
            return self.hbcorc.getHbc(hphm,hpzl)
        except Exception,e:
            self.loginkakouorcflag = True
            self.loginkakoucount = 0
            raise
##            if str(e)[:3] == 'ORA':
##                pass

    def getHbcByHphm(self,t1,t2,hphm):
        try:
            return self.imgMysql.getHbcByHphm(t1,t2,hphm)
        except MySQLdb.Error,e:
            #logging.exception(e)
            self.loginmysqlflag = True
            self.loginmysqlcount = 0
            raise

    def getUrl(self,jlbh):
        url = "http://"+'10.47.189.30:8088/'+jlbh[10:12]+'/'+'vhipict'+'/'+jlbh[12:18]+'/'+jlbh[18:20]+'/'+jlbh[20:22]+'/'+jlbh[0:12]+'-'+jlbh[12:26]+'-'+jlbh[26:27]+'-1.jpg'
        return url

    def getImgName(self,jlbh):
        pass
         
    def test(self):
        print 'hour1',gl.hour1
        print 'min1',gl.min1
        print 'sec1',gl.sec1

    def setData(self):
        try:
            next_time = self.timeflag+datetime.timedelta(minutes = 1)
            plateinfo = self.getPlateInfo(self.timeflag,next_time)
            num = len(plateinfo)
            #print 'num',num
            if num > 0:
                for s in plateinfo:
                    hbchpzl = '00'
                    if s['HPHM'] != None and s['HPHM'][:2]== '粤' and s['HPHM'] not in self.whitelist:
                        trim_h = ''
                        union_h = s['HPHM'].decode('gbk')
                        if union_h[-1] == u'学':
                            trim_h = union_h[1:-1]
                            hbchpzl = '16'
                        elif union_h[-1] == u'挂':
                            trim_h = union_h[1:-1]
                            hbchpzl = '15'
                        else:
                            trim_h = union_h[1:]
                        if hbchpzl == '00':
                            hbchpzl = self.hpys3.get(s['HPYS'],'00')

                        h = self.getHbcFromKakou(trim_h,hbchpzl)
                        
                        if h != []:
                            imgpath = ''
                            s_time = datetime.datetime(s['JGSJ'].year,s['JGSJ'].month,s['JGSJ'].day,gl.hour1,gl.min1,gl.sec1)
                            e_time = datetime.datetime(s['JGSJ'].year,s['JGSJ'].month,s['JGSJ'].day,gl.hour2,gl.min2,gl.sec2)
                            
                            h_hphm = self.getHbcByHphm(s_time,e_time,union_h.encode('utf8'))
                            values = []
                            url = self.getUrl(s['JLBH'])
                            if len(h_hphm) == 0 and s['JGSJ']>=s_time and s['JGSJ']<=e_time:
                                #print 'test'
                                cpzl2 = ''
                                if s['HPHM'].decode('gbk')[-1] == u'学' or s['HPHM'].decode('gbk')[-1] == u'挂':
                                    cpzl2 = u'标准车牌'
                                elif s['HPYS'] == '1':
                                    cpzl2 = u'双层车牌'
                                elif s['HPYS'] == '0':
                                    cpzl2 = u'军车车牌'
                                else:
                                    cpzl2 = u'标准车牌'

                                self.name = u'机号'+self.floder[s['BZWZDM']]+u'车道A'+str(s['CDBH'])+s['JGSJ'].strftime('%Y年%m月%d日%H时%M分%S秒').decode('gbk')+u'R454DOK3T'+u'T'+cpzl2+u'C'+self.hpys2[s['HPYS']]+u'P'+s['HPHM'].decode('gbk')+u'驶向'+self.fxbh2.get(s['BZWZDM'],'00').get(s['FXBH'],u'无')+u'违章闯红灯'
                                self.path = self.imgpath+'/'+s['JGSJ'].strftime('%Y年%m月%d日').decode('gbk')+'/'+u'违章图片目录'
                                imgpath = os.path.join(self.path.encode('utf8'),self.name.encode('utf8')+'.jpg')
                                self.getImgByUrl(url,self.path,self.name)
                            
                            values.append((self.address[s['BZWZDM']].encode('utf8'),s['JGSJ'],str(s['HPZL']).encode('utf8'),s['HPHM'].decode('gbk').encode('utf8'),self.fxbh2.get(s['BZWZDM'],'00').get(s['FXBH'],u'无').encode('utf8'),s['CLSD'],self.hpys[s['HPYS']].encode('utf8'),s['CDBH'],h[0]['FDJH'].decode('gbk').encode('utf8'),h[0]['CLSBDH'].decode('gbk').encode('utf8'),url,imgpath))
                            self.addHbc(values)
                            self.trigger.emit('<table><tr style="font-family:arial;font-size:14px;color:blue"><td>[%s]</td><td width="100">%s</td><td width="160">%s</td></tr></table>'%(s['JGSJ'],s['HPHM'],self.address[s['BZWZDM']].encode('gbk')),1)
            else:
                time.sleep(1)
            self.timeflag = next_time
            self.hbcIni.setSyst(next_time.strftime('%Y-%m-%d %H:%M:%S'))
##        except MySQLdb.Error,e:
##            logging.exception(e)
##            time.sleep(15)
##            pass
        except Exception,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)),1)
            #print e
            logging.exception(e)
            time.sleep(15)
            if str(e)[:3] == 'ORA':
                pass
       
if __name__ == "__main__":
    #main()
    #ds = DiskState()
    #print ds.checkDisk()

    hc = HbcCenter()
    #hc.loginKakouOrc()
    #hc.loginHbcOrc()
    #hc.loginMysql()
    path = 'f:/imgs/'+u'惠州惠城区东江大桥/'+datetime.datetime.now().strftime('%Y%m%d')
    path2 = 'd:/hbcimgs/test/'
    url = 'http://10.47.189.30:8088/04/vhipict/201405/21/02/000752075104-20140521025658-5-1.jpg'
    hc.getImgByUrl(url,path2,'惠州惠城区东江大桥车道8时间2014年05月21日02时57分11秒69020150黄牌粤LX1365方向进城.jpg')
    #hc.setData()
        
##    dataCenter = DataCenter()
##    dataCenter.setupOrc()
##    dataCenter.getBkcp()
##    print dataCenter.bkcp
##    print dataCenter.bkcp_list
##    print dataCenter.checkBkcpPlate('粤23423')

    
##    #dataCenter.setupMysql()
##    dataCenter.setupOrc()
##    s = dataCenter.getSiteID()
##    print s['淡水伯公坳卡口']
##    dataCenter = DataCenter()
##    dataCenter.setupMysql()
##    dataCenter.setupOrc()
##    dataCenter.main()
##
##    del dataCenter

