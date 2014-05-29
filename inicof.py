#-*- encoding: gb2312 -*-
import ConfigParser
import string, os, sys
import datetime
import time

class HbcIni:
    def __init__(self,confpath = 'hbc.conf'):
        self.confpath = confpath
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(self.confpath)

    def str2time(self,timestr):
        t = time.strptime(timestr,'%Y-%m-%d %H:%M:%S')
        return datetime.datetime(*t[:6])
    
    def getKakou(self):
        kakouconf = {}
        kakouconf['host']   = self.cf.get('KAKOU','host')
        kakouconf['user']   = self.cf.get('KAKOU','user')
        kakouconf['passwd'] = self.cf.get('KAKOU','passwd')
        kakouconf['port']   = self.cf.get('KAKOU','port')
        kakouconf['sid']    = self.cf.get('KAKOU','sid')
        return kakouconf
    
    def getHbc(self):
        hbcconf = {}
        hbcconf['host']   = self.cf.get('HBC','host')
        hbcconf['user']   = self.cf.get('HBC','user')
        hbcconf['passwd'] = self.cf.get('HBC','passwd')
        hbcconf['port']   = self.cf.get('HBC','port')
        hbcconf['sid']    = self.cf.get('HBC','sid')
        return hbcconf

    def getMysql(self):
        mysqlconf = {}
        mysqlconf['host']    = self.cf.get('MYSQLSET','host')
        mysqlconf['user']    = self.cf.get('MYSQLSET','user')
        mysqlconf['passwd']  = self.cf.get('MYSQLSET','passwd')
        mysqlconf['port']    = self.cf.getint('MYSQLSET','port')
        mysqlconf['db']      = self.cf.get('MYSQLSET','db')
        mysqlconf['charset'] = self.cf.get('MYSQLSET','charset')
        return mysqlconf

    def getSyst(self):
        systconf = {}
        systconf['time']    = self.str2time(self.cf.get('SYSTSET','time'))
        systconf['imgpath'] = self.cf.get('SYSTSET','imgpath')
        return systconf

    def setSyst(self,c_time):
        self.cf.set('SYSTSET', 'time', c_time)
        fh = open(self.confpath, 'w')
        self.cf.write(fh)
        fh.close()
 
if __name__ == "__main__":
    try:
        hbcini = HbcIni()
        print hbcini.getSyst()
        #s = imgIni.getPlateInfo(PATH2)

    except ConfigParser.NoOptionError,e:
        print e
        time.sleep(10)

