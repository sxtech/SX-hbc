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
        self.hpzl  = {'01':u'����','02':u'����','06':u'����','16':u'ѧ','15':u'��'}
        self.hpys  = {'0':u'����','1':u'����','2':u'����','3':u'����','4':u'����'}
        self.hpys2 = {'0':u'�׵׺���','1':u'�Ƶ׺���','2':u'���װ���','3':u'�ڵװ���','4':u'����'}
        self.hpys3 = {'0':'00','1':'01','2':'02','3':'06','4':'00'}
        self.address = {'00000084':u'���ݻݳ�����������','00000096':u'���ݻݳ�������֧��','00000094':u'���ݻݳ�������·'}
        self.floder = {'00000084':u'303','00000096':u'302','00000094':u'301'}
        self.fxbh = {'SN':u'����','NS':u'������','EW':u'������','WE':u'����','IN':u'����','OT':u'����'}
        self.fxbh2 = {'00000084':{'SN':u'����','NS':u'������','EW':u'������','WE':u'����','IN':u'������','OT':u'����'},
                     '00000096':{'SN':u'����','NS':u'������','EW':u'������','WE':u'����','IN':u'������','OT':u'����'},
                     '00000094':{'SN':u'����','NS':u'������','EW':u'������','WE':u'����','IN':u'������','OT':u'����'}}        
        self.whitelist = set(['��AE3Q73','��LB1813','��AW8G49','��LXX266'])
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

    #�����ļ���
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
        
    #����URL��ַ��ȡͼƬ������
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
                    if s['HPHM'] != None and s['HPHM'][:2]== '��' and s['HPHM'] not in self.whitelist:
                        trim_h = ''
                        union_h = s['HPHM'].decode('gbk')
                        if union_h[-1] == u'ѧ':
                            trim_h = union_h[1:-1]
                            hbchpzl = '16'
                        elif union_h[-1] == u'��':
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
                                if s['HPHM'].decode('gbk')[-1] == u'ѧ' or s['HPHM'].decode('gbk')[-1] == u'��':
                                    cpzl2 = u'��׼����'
                                elif s['HPYS'] == '1':
                                    cpzl2 = u'˫�㳵��'
                                elif s['HPYS'] == '0':
                                    cpzl2 = u'��������'
                                else:
                                    cpzl2 = u'��׼����'

                                self.name = u'����'+self.floder[s['BZWZDM']]+u'����A'+str(s['CDBH'])+s['JGSJ'].strftime('%Y��%m��%d��%Hʱ%M��%S��').decode('gbk')+u'R454DOK3T'+u'T'+cpzl2+u'C'+self.hpys2[s['HPYS']]+u'P'+s['HPHM'].decode('gbk')+u'ʻ��'+self.fxbh2.get(s['BZWZDM'],'00').get(s['FXBH'],u'��')+u'Υ�´����'
                                self.path = self.imgpath+'/'+s['JGSJ'].strftime('%Y��%m��%d��').decode('gbk')+'/'+u'Υ��ͼƬĿ¼'
                                imgpath = os.path.join(self.path.encode('utf8'),self.name.encode('utf8')+'.jpg')
                                self.getImgByUrl(url,self.path,self.name)
                            
                            values.append((self.address[s['BZWZDM']].encode('utf8'),s['JGSJ'],str(s['HPZL']).encode('utf8'),s['HPHM'].decode('gbk').encode('utf8'),self.fxbh2.get(s['BZWZDM'],'00').get(s['FXBH'],u'��').encode('utf8'),s['CLSD'],self.hpys[s['HPYS']].encode('utf8'),s['CDBH'],h[0]['FDJH'].decode('gbk').encode('utf8'),h[0]['CLSBDH'].decode('gbk').encode('utf8'),url,imgpath))
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
    path = 'f:/imgs/'+u'���ݻݳ�����������/'+datetime.datetime.now().strftime('%Y%m%d')
    path2 = 'd:/hbcimgs/test/'
    url = 'http://10.47.189.30:8088/04/vhipict/201405/21/02/000752075104-20140521025658-5-1.jpg'
    hc.getImgByUrl(url,path2,'���ݻݳ����������ų���8ʱ��2014��05��21��02ʱ57��11��69020150������LX1365�������.jpg')
    #hc.setData()
        
##    dataCenter = DataCenter()
##    dataCenter.setupOrc()
##    dataCenter.getBkcp()
##    print dataCenter.bkcp
##    print dataCenter.bkcp_list
##    print dataCenter.checkBkcpPlate('��23423')

    
##    #dataCenter.setupMysql()
##    dataCenter.setupOrc()
##    s = dataCenter.getSiteID()
##    print s['��ˮ�����꿨��']
##    dataCenter = DataCenter()
##    dataCenter.setupMysql()
##    dataCenter.setupOrc()
##    dataCenter.main()
##
##    del dataCenter

