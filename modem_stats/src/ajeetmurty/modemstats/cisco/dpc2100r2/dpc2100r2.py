import logging.config
import os
import platform
import re
from datetime import datetime
from requests import Request, Session
from bs4 import BeautifulSoup
import json
import time
from tinydb import TinyDB

logging.config.fileConfig('logging.conf')
logr = logging.getLogger('pylog')
modem_status_url = 'http://192.168.100.1'
stats_output_db_file = 'dpc2100r2_db.json'
#regex
pwr_regex = '[(dw\(vdbmv\);)(\s)]+'
snr_regex = '[(dw\(vdb\);)(\s)]+'
space_regex = '[(\n)(\s)]+'
#labels
label_modem_request_epoch_time = 'request_epoch_time'
label_modem_request_timestamp = 'request_timestamp'
label_modem_url = 'url'

def main():
    logr.info('start modem')
    try:
        print_sys_info()
        parsing_output_dict = do_parsing()
        logr.info('parsing output: ' + str(parsing_output_dict))
        logr.info("pretty print dump: \n" + json.dumps(parsing_output_dict, indent=4))
        output_csv(parsing_output_dict)
    except Exception: 
        logr.exception('Exception')
    logr.info('stop')

def print_sys_info():
    logr.info('login|hostname|os|python : {0}|{1}|{2}|{3}.'.format(os.getlogin(), platform.node() , platform.system() + '-' + platform.release() , platform.python_version()))

def output_csv(input_dict):
    logr.info('input values for csv: ' + str(input_dict))
    db = TinyDB(stats_output_db_file)
    db.insert(input_dict)
    

def do_parsing():
    logr.info('get info from: ' + modem_status_url)
    session = Session()
    prepped = Request('GET', modem_status_url).prepare()
    response = session.send(prepped, stream=True, verify=False, timeout=10)
    content = response.raw.read().decode()

    if response:
        if(response.status_code == 200):
            logr.info('response: ' + content.replace('\n', ' '))
            soup = BeautifulSoup(content, "html5lib")
            output_dict = {}
            output_dict[label_modem_request_epoch_time] = str(time.time())
            output_dict[label_modem_request_timestamp] = str(datetime.utcnow())
            output_dict[label_modem_url] = modem_status_url
            return output_dict
        else:
            raise Exception('fail http response code: ' + str(response.status_code))
    else:
        raise Exception('null response object')        
    
    
if __name__ == '__main__':
    main()
