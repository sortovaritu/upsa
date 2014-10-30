from os import getenv

from contextlib import contextmanager

import pymssql

import logging


DB_host = 'EVBYMINSD7900\\UCDEV'
DB_user = 'Python'
DB_password = 'Python#1'
DB_database = 'voip_new'


def xstr(s):
    if s is None:
        return 'NULL'
    else:
        return '\'' + s + '\''


@contextmanager
def get_connection(cmd):
    try:
        logging.info('Connection with Database %s\%s', DB_host, DB_database)
        connection = pymssql.connect(DB_host, DB_user, DB_password, DB_database,login_timeout=10)
        logging.info('Connection with Database OK')
    except Exception as ex:
        logging.error('Connection with Database failed: ' + ex.args)
    yield connection
    connection.close()
    logging.info('Connection with Database Closed')

def send_select(conn,cmd,sender):
    cursor = conn.cursor()
    ret = []
    try:
        logging.debug('SQL SELECT request: ' + sender)
        logging.debug(cmd)
        cursor.execute(cmd)
    except Exception:
        logging.error('SQL bad request: ' + sender)
    for row in cursor:
        ret.append(row)
    return ret


def send_update(conn,cmd,sender):
    cursor = conn.cursor()
    try:
        logging.debug('SQL UPDATE request: ' + sender)
        logging.debug(cmd)
        cursor.execute(cmd)
        conn.commit()
    except Exception:
        logging.error('SQL bad request: ' + sender)


def send_insert(conn,cmd,sender):
    cursor = conn.cursor()
    try:
        logging.debug('SQL INSERT request: ' + sender)
        logging.debug(cmd)
        cursor.execute(cmd)
        conn.commit()
    except Exception as ex:
        logging.error('SQL bad request: ' + sender + str(ex.args))


def send_delete(conn,cmd,sender):
    cursor = conn.cursor()
    try:
        logging.debug('SQL DELETE request: ' + sender)
        logging.debug(cmd)
        cursor.execute(cmd)
        conn.commit()
    except Exception:
        logging.error('SQL bad request: ' + sender)




class VoIP_DB:  
        

    def Clean_Temp_Tables(self):
        cmd = 'DELETE FROM [voip_new].[dbo].[upsausr] DELETE FROM [voip_new].[dbo].[upsaloc]'
        with get_connection(cmd) as conn:
            try:
                send_delete(conn,cmd,self.Clean_Temp_Tables.__name__)
            except Exception as e:
                logging.error(e.args)




    def Send_Locations(self,locations):
        cmd = ''
        for location in locations:
            cmd+='INSERT INTO [voip_new].[dbo].[upsaloc] VALUES(%s,\'%s\') ' % (location[0], location[1])
        with get_connection(cmd) as conn:
            try:
                send_insert(conn,cmd,self.Send_Locations.__name__)
            except Exception as e:
                logging.error(e.args)


    def Send_Users(self,users):
        cmd=''
        
        with get_connection(cmd) as conn:
            for user in users:
                try:
                    cmd=u"""INSERT INTO [voip_new].[dbo].[upsausr] 
                    VALUES(%s,\'%s\',%s,\'%s\',\'%s\',%d,%s); """ % (user[0], user[1].replace("'","''"), user[2], user[3], user[4],int(user[5]),xstr(user[6]))
                    send_insert(conn,cmd,self.Send_Users.__name__)
                except Exception as e:
                    logging.error(e.args)


    def Get_Old_DB_Users(self):
        cmd = 'SELECT [UserName]\
                        ,[Extension]\
                        ,[voip_new].[dbo].[locations].[ID]\
                        ,[tech] as Protocol\
                        ,[Password]\
                        ,[VmPassword]\
                        ,[cur_date] as DateOfAddition\
                        ,[gab]\
                        ,[privateline]\
                        ,[PMC_ID]\
                FROM [voip_db].[dbo].[users]\
                left join [voip_db].[dbo].[Location] on [voip_db].[dbo].[users].Location = [voip_db].[dbo].[Location].[ID_loc]\
                left join [voip_new].[dbo].[locations] on [voip_new].[dbo].[locations].Location = [voip_db].[dbo].[Location].[Location]'

        with get_connection(cmd) as conn:
            try:
                data = send_select(conn,cmd,self.Get_Old_DB_Users.__name__)
                return data
            except Exception as e:
                logging.error(e.args)


    def Send_Old_To_New(self):
        cmd='INSERT INTO [voip_new].[dbo].[users]\
                SELECT [UserName]\
                      ,[Extension]\
                      ,[voip_new].[dbo].[locations].[ID] as [Location]\
                      ,[tech] as [Protocol]\
                      ,[Password]\
                      ,[VmPassword]\
                      ,[cur_date] as [DateOfAddition]\
                      ,[gab]\
                      ,[privateline]\
                      ,[PMC_ID]\
                  FROM [voip_db].[dbo].[users]\
                  left join [voip_db].[dbo].[location] on [voip_db].[dbo].[location].[ID_loc] = [voip_db].[dbo].[users].Location\
                  left join [voip_new].[dbo].[locations] on [voip_new].[dbo].[locations].[Location] = [voip_db].[dbo].[location].Location'
        with get_connection(cmd) as conn:
            try:
                send_insert(conn,cmd,self.Send_Old_To_New.__name__)
            except Exception as e:
                logging.error(e.args)



    def Get_New_Locations(self):
        cmd = 'SELECT [voip_new].[dbo].[upsaloc].[ID]\
                        ,[name]\
                FROM [voip_new].[dbo].[upsaloc]\
                LEFT JOIN [voip_new].[dbo].[locations] ON [voip_new].[dbo].[locations].Location = [voip_new].[dbo].[upsaloc].[name]\
                WHERE [voip_new].[dbo].[locations].[Location] IS NULL'

        with get_connection(cmd) as conn:
            try:
                data = send_select(conn,cmd,self.Get_New_Locations.__name__)
                return data
            except Exception as e:
                logging.error(e.args)



    def Get_New_Users(self):
        cmd = """SELECT [voip_new].[dbo].[upsausr].[ID]
                        ,[fullName]
                        ,[title]
                        ,[hired]
                        ,[voip_new].[dbo].[upsausr].[location]
                        ,[voip_new].[dbo].[locations].Location
                    FROM [voip_new].[dbo].[upsausr]
                    left join [voip_new].[dbo].[users] on [voip_new].[dbo].[upsausr].fullName = [voip_new].[dbo].[users].UserName
                    left join [voip_new].[dbo].[locations] on [voip_new].[dbo].[locations].ID = [voip_new].[dbo].[upsausr].location
                    where [voip_new].[dbo].[users].UserName is NULL
                    and [active] = 1
                    and [title] <>'Office cleaner'
                    and [title] <>'Physical Security Guard'
                    and [title] <>'Student'
                    and [hired] > GetDate() - 7"""

        with get_connection(cmd) as conn:
            try:
                data = send_select(conn,cmd,self.Get_New_Users.__name__)
                return data
            except Exception as e:
                logging.error(e.args)



    def Get_Fired_Users(self):
        cmd = """SELECT 
                    [voip_new].[dbo].[users].[ID]
                    ,[voip_new].[dbo].[users].UserName
                    ,[voip_new].[dbo].[users].extension
                    ,[voip_new].[dbo].[users].Location
                    ,[voip_new].[dbo].[upsausr].[fired]
                FROM [voip_new].[dbo].[upsausr]
                  left join [voip_new].[dbo].[users] on [voip_new].[dbo].[upsausr].fullName = [voip_new].[dbo].[users].UserName and [voip_new].[dbo].[upsausr].ID = [voip_new].[dbo].[users].PMC_ID
                where [voip_new].[dbo].[users].UserName is not null
                        and active = 0
                        and fired > GetDate() - 14"""
        with get_connection(cmd) as conn:
            try:
                data = send_select(conn,cmd,self.Get_Fired_Users.__name__)
                return data
            except Exception as e:
                logging.error(e.args)




    def Update_Locations(self,locations):
        cmd = ''
        for row in locations:
            cmd+='INSERT INTO [voip_new].[dbo].[locations] VALUES(%s,\'%s\',255,\'\') ' % (row[0], row[1])
        with get_connection(cmd) as conn:
            try:
                send_insert(conn,cmd,self.Update_Locations.__name__)
            except Exception as e:
                logging.error(e.args)


    def Update_Users(self,users):
        return


    def PMCID_Renew(self):
        cmd='UPDATE [voip_new].[dbo].[users]\
                    Set [voip_new].[dbo].[users].PMC_ID = (select [voip_new].[dbo].[upsausr].[ID] \
                    from [voip_new].[dbo].[upsausr] where [voip_new].[dbo].[upsausr].fullName = [voip_new].[dbo].[users].UserName )'
        with get_connection(cmd) as conn:
            try:
                send_update(conn,cmd,self.PMCID_Renew.__name__)
            except Exception as e:
                logging.error(e.args)


    def Get_Number_Ranges_For_Loc(self,locid):
        cmd = """SELECT [Location]
                    ,[Start]
                    ,[Stop]
                FROM [voip_new].[dbo].[numranges] where [Location]=%s""" % (locid)

        with get_connection(cmd) as conn:
            try:
                data = send_select(conn,cmd,self.Get_New_Users.__name__)
                return data
            except Exception as e:
                logging.error(e.args)


    def Get_Busy_Numbers(self,start,stop):
        cmd = """SELECT[Extension]
                    FROM [voip_new].[dbo].[users]
                where [Extension]>=%s and Extension<=%s""" % (start, stop)

        with get_connection(cmd) as conn:
            try:
                data = send_select(conn,cmd,self.Get_New_Users.__name__)
                return data
            except Exception as e:
                logging.error(e.args)


    def Add_New_User(self,username,extension,locid,pas,vmpas,pmcid):
        cmd="""INSERT INTO [voip_new].[dbo].[users] 
                    VALUES(\'%s\',%s,%s,'sip',\'%s\',\'%s\',GetDate(),1,NULL,\'%s\') """ % (username, str(extension),str(locid), pas, vmpas, pmcid)
        with get_connection(cmd) as conn:
            try:
                send_insert(conn,cmd,self.Send_Users.__name__)
            except Exception as e:
                logging.error(e.args)

    def Del_Fired_User(self,id):
        cmd="""DELETE FROM [voip_new].[dbo].[users] 
                    WHERE [ID] = %s) """ % (str(id))
        with get_connection(cmd) as conn:
            try:
                send_insert(conn,cmd,self.Send_Users.__name__)
            except Exception as e:
                logging.error(e.args)