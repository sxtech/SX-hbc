# -*- coding: cp936 -*-
import cx_Oracle
import datetime
import time

class HbcOrc:
    def __init__(self,host='10.44.253.110',user='hzhbc', passwd='98hbc77',sid='hzjj'):
        self.host    = host
        self.user    = user
        self.passwd  = passwd
        self.port    = 1521
        self.sid     = sid
        self.cur = None
        self.conn = None
        
    def __del__(self):
        if self.cur != None:
            self.cur.close()
        if self.conn != None:
            self.conn.close()
        
    def login(self):
        try:
            self.conn = cx_Oracle.connect(self.user,self.passwd,self.host+':'+str(self.port)+'/'+self.sid)
            self.cur = self.conn.cursor()
            #print self.passwd
        except Exception,e:
            raise

    def getHbc3(self,hphm):
        try:
            self.cur.execute("select v.* from hbc_vehicle v left join hbc_all a on v.fdjh=a.fdjh where v.hphm = '%s' and v.clsbdh = a.clsbdh"%hphm)
        except Exception,e:
            raise
        else:
            return self.rowsToDictList()

    def getHbc(self,hphm,hpzl):
        try:
            self.cur.execute("select v.* from hbc_vehicle v left join hbc_all a on v.xh=a.nxh where a.hphm = v.hphm and v.hpzl='%s' and v.hphm='%s'"%(hpzl,hphm))
        except Exception,e:
            raise
        else:
            return self.rowsToDictList()

    def getHbc2(self,hphm):
        try:
            self.cur.execute("select v.* from hbc_vehicle v left join hbc_all a on v.xh=a.nxh where a.hphm = v.hphm and v.hpzl = '02' and v.hphm='LB1813'")
        except Exception,e:
            raise
        else:
            return self.rowsToDictList()
        
    def getHbc1(self):
        try:
            self.cur.execute("select HPHM,HPZL from hbc_vehicle where rownum>=15")
        except Exception,e:
            raise
        else:
            #return self.cur.fetchall()
            return self.rowsToDictList()

    def test(self):
        try:
            self.cur.execute("select * from v$version")
        except Exception,e:
            raise
        else:
            s = self.cur.fetchall()
            print s
        
    def rowsToDictList(self):
        columns = [i[0] for i in self.cur.description]
        return [dict(zip(columns, row)) for row in self.cur]

    def orcCommit(self):
        self.conn.commit()

if __name__ == "__main__":
    orc = HbcOrc('10.44.253.110','hzhbc','98hbc77','hzjj')
    #values = []
    orc.login()
    s = orc.getHbc2('LXX266')
    print s
    for i in s:
        print i
    #print orc.getHbc1()
    #print a[0]['FDJH']
##    for i in orc.getHbc1():
##        print i
    orc.orcCommit()
    #orc.test()
    del orc
