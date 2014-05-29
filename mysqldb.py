# -*- coding: cp936 -*-
import os
import sys
import glob
import time
import datetime
import MySQLdb
#import _mysql

def getTime():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

class ImgMysql:
    def __init__(self,host = 'localhost',user = 'root', passwd = '',ip='127.0.0.1'):
        self.host    = host
        self.user    = user
        self.passwd  = passwd
        self.port    = 3306
        self.db      = 'hbc'
        self.charset = 'utf8'
        self.ip = ip
        self.initime = None
        self.imgtime = None
        self.cur = None
        self.conn = None
        
    def __del__(self):
        if self.cur != None:
            self.cur.close()
        if self.conn != None:
            self.conn.close()

    def login(self):
        try:
            self.conn = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,
                                        port=self.port,charset=self.charset,db=self.db)
            self.cur = self.conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        except Exception,e:
            raise

    def setupMysql(self):
        now = getTime()
        try:
            self.login()
        except Exception,e:
            #print now,e
            #print now,'Reconn after 15 seconds'
            time.sleep(15)
            self.setupMysql()
        else:
            pass
        
    def addHbc(self,values):
        try:
            self.cur.executemany("insert into hbc(address,passtime,hpzl,hphm,fxbh,clsd,color,cdbh,fdjh,clsbdh,urlpath,imgpath) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",values)
        except MySQLdb.Error,e:
            self.conn.rollback()
            raise
        else:
            self.conn.commit()

    def getHbc(self,p1,p2):
        try:
            self.cur.execute("select * from hbc where passtime>='%s' and passtime<='%s'"%(p1,p2))
            self.conn.commit()
            s = self.cur.fetchall()
        except MySQLdb.Error,e:
            raise
        else:
            return s

    def getHbcByHphm(self,p1,p2,hphm):
        #print "select * from hbc where passtime>='%s' and passtime<='%s' and hphm='%s'"%(p1,p2,hphm)
        self.cur.execute("select * from hbc where passtime>='%s' and passtime<='%s' and hphm='%s'"%(p1,p2,hphm))
        s = self.cur.fetchall()
        self.conn.commit()
        return s
 
    #main
    def getPlateInfo(self,limit=10):
        try:
            if self.imgtime == None:
                self.getLastFlagTime()
            self.cur.execute("select i.*,d.d_ip,d.disk from indexcenter as i left join disk as d on i.disk_id=d.id where (i.captime>=%s or (i.captime>=%s and i.captime<=%s)) and i.iniflag=0 ORDER BY i.passdatetime DESC limit 0,%s",(datetime.datetime.now()-datetime.timedelta(minutes=10),self.initime,self.initime+datetime.timedelta(minutes=30),limit))
            s = self.cur.fetchall()
        except MySQLdb.Error,e:
            raise
        else:
            self.conn.commit()
            return s


        
    def endOfCur(self):
        self.conn.commit()
        
    def sqlCommit(self):
        self.conn.commit()
        
    def sqlRollback(self):
        self.conn.rollback()
            
if __name__ == "__main__":
    imgMysql = ImgMysql('localhost','root','','127.0.0.1')
    #address,passtime,hpzl,hphm,fxbh
    p1 = datetime.datetime(2014, 5, 18, 20, 20, 33, 734000)
    new_time = datetime.datetime.now()
    imgMysql.login()
    print imgMysql.getHbcByHphm(p1,new_time,u'粤L1234'.encode('utf8'))
    #s = imgMysql.addHbc([(u'江北'.encode('utf8'),new_time,u'黄牌'.encode('utf8'),u'粤L1235'.encode('utf8'),u'进城'.encode('utf8'))])
    #print s
    #imgMysql.setNewFlagTime()
    #s = imgMysql.getImgInfoByIPList(10,['127.0.0.1'])
    #print imgMysql.getDisk()['id']
    #imgMysql.setDisk('192.168.1.12','E')
    #ip = ['192.168.1.1','127.0.0.1']
    #s = imgMysql.getImgInfoByIPList(10,ip)
    #print s
    
    del imgMysql

