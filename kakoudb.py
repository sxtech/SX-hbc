# -*- coding: cp936 -*-
import cx_Oracle
import time

class KakouOrc:
    def __init__(self,host='10.44.237.93',user='hzjj', passwd='hzjj#data',sid='baokang'):
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

    def setupOrc(self):
        try:
            self.login()
        except Exception,e:
            #print now,e
            #logging.exception(e)
            #print now,'Reconn after 15 seconds'
            time.sleep(15)
            self.setupOrc()
        else:
            pass

    def test(self):
        self.cur.execute("select hphm from vw_hzjj_jgcl where JGSJ>=to_date('2014-05-20 7:30:00','yyyy-mm-dd hh24:mi:ss') and JGSJ<=to_date('2014-05-20 7:35:00','yyyy-mm-dd hh24:mi:ss') ")
        s = self.cur.fetchall()
        return s
        #return self.rowsToDictList

    def test3(self):
        self.cur.execute("select * from vw_hzjj_jgcl where JGSJ>to_date('2014-05-20 12:08:01','yyyy-mm-dd hh24:mi:ss') and hphm=''")
        s = self.cur.fetchall()
        return s

    def test2(self):
        self.cur.execute("select * from user_tab_columns where table_name='VW_HZJJ_JGCL'")
        s = self.cur.fetchall()
        return s
    
    def getPlateInfo(self,t1,t2):
        try:
            self.cur.execute("select * from vw_hzjj_jgcl where JGSJ>to_date('%s','yyyy-mm-dd hh24:mi:ss') and JGSJ<=to_date('%s','yyyy-mm-dd hh24:mi:ss')"%(str(t1),str(t2)))
        except Exception,e:
            print e
            raise
        else:
            return self.rowsToDictList()
        
    def rowsToDictList(self):
        columns = [i[0] for i in self.cur.description]
        return [dict(zip(columns, row)) for row in self.cur]

    def orcCommit(self):
        self.conn.commit()

if __name__ == "__main__":
    import datetime
    orc = KakouOrc()
    #values = []
    orc.setupOrc()
    #print orc.test()
    for i in orc.test():
        #url = "http://"+'10.47.189.30:8088/'+i[0][10:12]+'/'+'vhipict'+'/'+i[0][12:18]+'/'+i[0][18:20]+'/'+i[0][20:22]+'/'+i[0][0:12]+'-'+i[0][12:26]+'-'+i[0][26:27]+'-1.jpg'
        #print url
        if i[0] == None:
            print i[0]

    del orc
