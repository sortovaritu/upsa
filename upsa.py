

import logging

import sys

import voip_db

import functions

import mail



logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.DEBUG,filename = u'log.log')

root = logging.getLogger()
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
root.addHandler(ch)




functions.Get_UPSA_Locations()

functions.Add_New_Locations()

functions.Get_UPSA_Users()

functions.Copy_From_Old_Db()

functions.PMCID_Renew()

functions.Add_New_Users()

#functions.Remove_Fired_Users()





