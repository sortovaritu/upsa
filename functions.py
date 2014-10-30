
import voip_db

import logging

import mail

import password

import requests

import json

def Copy_From_Old_Db():
    Database = voip_db.VoIP_DB()
    logging.info( u'Copy Database from Old to the New...' )
    try:
        Database.Send_Old_To_New()                                                                                  #send user info from old database to the new
        logging.info( u'Copy Database from Old to the New...Completed' )
    except Exception as ex:
        logging.info( u'Copy Database from Old to the New...Failed' + str(ex.args))
        return








def PMCID_Renew():
    Database = voip_db.VoIP_DB()
    logging.info( u'PMCID Renew...' )
    try:
        Database.PMCID_Renew()                                                                                      #renew PMC ID
        logging.info( u'PMCID Renew...Completed' )
    except Exception as ex:
        logging.info('PMCID Renew...Failed: ' + str(ex.args))
        return











def Get_Extension_For_User(locid):
    Database = voip_db.VoIP_DB()
    try:
        logging.debug('Get Number Ranges for Location: ' + str(locid))
        ranges = Database.Get_Number_Ranges_For_Loc(locid)                                                          #get number ranges for Location by Location ID
        logging.debug('Get Number Ranges for Location...Completed')
    except Exception as ex:
        logging.debug('Get Number Ranges for Location...Failed ')
    if (len(ranges)>0):                                                                                             #number ranges are found for present Location
        logging.debug('Number Ranges are Found')
        for Range in ranges:    
            logging.debug('Get Busy Numbers for Range: '+str(Range[1])+' - '+str(Range[2]))                         #search free number in every Location
            busy = Database.Get_Busy_Numbers(str(Range[1]),str(Range[2]))                                           #get busy numbers for range                      
            busyList = []
            for Busy in busy:
                busyList.append(Busy[0])                                                                            #add to list of busy numbers
            r = range(Range[1], Range[2])
            logging.debug('Search Free Numbers for Range: '+str(Range[1])+' - '+str(Range[2]))
            free = [e for e in r if not e in busyList]                                                              #search free number in selected range
            if (len(free)>0):                                                                                       #free numbers are found
                logging.debug('Free Number is Found: '+free[0])  
                return free[0]                                                                                      #return first free number in list
    else:
        logging.debug('Number Ranges are not Found')
        return -1




def Get_REST_Token():
    postData = {'grant_type': 'client_credentials'}
    cred = {'auto_epm_voip_user', '1@qWaS34'}
    logging.info( u'Send token request...' )
    response = requests.post('https://upsa.epam.com/workload/rest/oauth/token', auth=('auto_epm_voip_user', '1@qWaS34'), data=postData)
    data = response.json()
    try:
        token = data['value']
    except Exception:
        logging.info( u'Error...' + str(response.text) )
        return
    logging.info( u'Token recieved: ' + str(token) )
    return token


def Get_UPSA_Locations():
    token = Get_REST_Token()                                                                                        #get token for request
    headers = {'Authorization': 'Bearer ' + token}                                                                  #header for request    
    logging.info( u'Clean Database Temp Tables...' )
    Database = voip_db.VoIP_DB()                                                                                    
    try:
        Database.Clean_Temp_Tables()                                                                                #delete all records in upsaloc and upsausr tables
        logging.info( u'Clean Database Temp Tables...Completed' )                                                          
    except Exception as ex:
        logging.info( u'Clean Database Temp Tables...Failed: ' + str(ex.args))
        return
    logging.info( u'Get Locations From UPSA Database...' )
    response = requests.get('https://upsa.epam.com/workload/rest/v3/locations/cities', headers=headers)             #send request to UPSA
    data = response.json()                                                                                          #parse response
    count = 0                                                                                                       #counter of founded Locations
    locations = []
    for row in data:
        locations.append([row['id'],row['name']])                                                                   #append Location id and name to the list
        count = count + 1                                                                                           #increment counter
    logging.info( str(count) +' Locations Recieved') 
    logging.info( u'Write Recieved Locations to the Temp Database...' )
    try:
        Database.Send_Locations(locations)                                                                          #write recieved Locations to the upsaloc temp table
        logging.info( u'Write Recieved Locations to the Temp Database...Completed' )
    except Exception as ex:
        logging.info( u'Write Recieved Locations to the Temp Database...Failed: ' + str(ex.args)   ) 
        return



def Add_New_Locations():
    Database = voip_db.VoIP_DB()
    logging.info( u'Add New Locations To the Database...' )
    try:
        logging.info( u'Search New Locations...' )
        newLocations = Database.Get_New_Locations()                                                                 #get new locations if exist
        logging.info( u'Search New Locations...Completed' )
    except Exception as ex:
        logging.info( 'Search New Locations...Failed: ' + str(ex.args))
        return
    if (len(newLocations)>0):                                                                                       #if count of new locations > 0 - new locations founded
        logging.info('New ' + str(len(newLocations)) + ' Locations founded:')
        for Location in newLocations:
            logging.info( u' New Location: %s',str(Location[1]) )
        try:
            logging.info( u'Write New Locations to the Database...' )
            Database.Update_Locations(newLocations)                                                                 #write new locations to the database
            logging.info( u'Write New Locations to the Database...Completed' )
        except Exception as ex:
            logging.info( u'Write New Locations to the Database...Failed:' + str(ex.args))
            return
        mail.Send_Email('New UPSA Locations Founded:',newLocations,'')                                              #<--- Send information about new locations to e-mail list 
    else:
        logging.info( u'New Locations not Founded' )
    logging.info( u'Add New Locations To the Database...Completed' )






def Get_UPSA_Users():
    Database = voip_db.VoIP_DB()
    token = Get_REST_Token()                                                                                        #get token for request
    headers = {'Authorization': 'Bearer ' + token}                                                                  #header for request
    logging.info( u'Get Users From UPSA Database...' )
    response = requests.get('https://upsa.epam.com/workload/rest/v3/employees', headers=headers)                    #send request to UPSA
    data = response.json()                                                                                          #parse response
    count=0                                                                                                         #counter of founded Users
    users = []
    for row in data:   
        if (row['locationId'] is not None):
            users.append([row['employeeId'],row['fullName'],row['locationId'],row['title'],row['hired'],row['isActive'],row['fired']])          #append User empoyeeId,fullName,locationId,title,hired,isActive and fired to the list
            count=count+1                                                                                           #increment counter
    logging.info( str(count) +' Users Recieved')
    logging.info( u'Write Recieved Users to the Temp Database...' )
    try:
        Database.Send_Users(users)                                                                                  #write recieved Users to the upsausr temp table
        logging.info( u'Write Recieved Users to the Temp Database...Completed' )
    except Exception as ex:
        logging.info( u'Write Recieved Users to the Temp Database...Failed: ' + str(ex.args))
        return



def Add_New_Users():
    Database = voip_db.VoIP_DB()
    logging.info( u'Add New Users To the Database...' )
    try:
        logging.info( u'Search New Users...' )
        newUsers = Database.Get_New_Users()                                                                         #get new users if exist
        logging.info( u'Search New Users...Completed' )
    except Exception as ex:
        logging.info( u'Search New Users...Failed: '  + str(ex.args))
        return
    if (len(newUsers)>0):                                                                                           #if count of new users > 0 - new users founded
        logging.info( u'New Users founded:' )
        mailAddedUsers = []
        mailFailedUsers = []
        logging.info( 'New ' + str(len(newUsers)) + ' Users founded:')
        for User in newUsers:                                                                                       #for every founded user
            logging.info( ' New User:' + User[1] + ', Location: ' + str(User[5]))
            extension = Get_Extension_For_User(str(User[4]))                                                        #get extension for user according with his location. User[4] - location id
            if (extension == -1):                                                                                   #if extension not found for user
                logging.info( 'Extension not found')
                mailFailedUsers.append([User[1],User[5]])                                                           #add such user to special failed list
            else:                                                                                                   #extension is found for user
                username = User[1]
                pmcid = User[0]
                locid = User[4]
                location = User[5]
                pas = password.randompassword(10)                                                                   #get random password for user
                vmpas = password.randompassword(9)                                                                  #get random vmpassword for user
                try:
                    logging.info( u'Write New User to the Database...' )
                    Database.Add_New_User(username,extension,locid,pas,vmpas,pmcid)                                 #write new user to the database
                    logging.info( u'Write New User to the Database...Complete' )
                    logging.info('Assigned Extension:' + str(extension))
                    mailAddedUsers.append([username,location,extension])                   
                except Exception as ex:
                    logging.info( u'Write New User to the Database...Failed' + str(ex.args))
        if (len(mailAddedUsers)>0):
            mail.Send_Email('New Users was added:',mailAddedUsers,'')                                               #<--- Send information about new users to e-mail list 
        if (len(mailFailedUsers)>0):
            mail.Send_Email('New Users was NOT added:',mailFailedUsers,'')                                          #<--- Send information about new users, who was not added to the database, to e-mail list 
    else:
        logging.info( u'No New Users' )
        print 'No New Users'

    logging.info( u'Update Users...Completed' )
    print 'Update Users...Completed'



def Remove_Fired_Users():
    Database = voip_db.VoIP_DB()
    logging.info( u'Remove Fired Users...' )
    print 'Remove Fired Users...'
    try:
        firedUsers = Database.Get_Fired_Users()
    except Exception as ex:
        print 'Connection with Database failed: ' + str(ex.args)
        return
    if (len(firedUsers)>0):
        logging.info( u'Fired Users founded:' )
        mailRemovedUsers = []
        mailFailedUsers = []
        print 'Fired ' + str(len(firedUsers)) + ' Users founded:'
        for User in firedUsers:
            extension = User[2]
            if (extension is None):
                print 'Extension is not found'
                mailFailedUsers.append([User[1],User[2]])
            else:
                try:
                    #Database.Del_Fired_User(User[0])
                    mailRemovedUsers.append([User[1],User[2]])
                    logging.info( u'Fired User: %s',str(User[1]))
                    print '-Fired User:' + User[1] + ', Extension: ' + str(User[2])
                except Exception as ex:
                    print 'Connection with Database failed: ' + str(ex.args)
        if (len(mailRemovedUsers)>0):
            mail.Send_Email('Fired Users was removed:',mailRemovedUsers,'')                                          #<--- Send information about new locations to e-mail list 
        if (len(mailFailedUsers)>0):
            mail.Send_Email('Fired Users was NOT removed:',mailFailedUsers,'')
    else:
        logging.info( u'No Fired Users' )
        print 'No Fired Users'

    logging.info( u'Remove Fired Users...Completed' )
    print 'Remove Fired Users...Completed'