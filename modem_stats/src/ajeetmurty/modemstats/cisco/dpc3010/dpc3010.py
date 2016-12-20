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
modem_status_url = 'http://192.168.100.1/Docsis_system.asp'
stats_output_db_file = 'dpc3010_db.json'
#regex
pwr_regex = '[(dw\(vdbmv\);)(\s)]+'
snr_regex = '[(dw\(vdb\);)(\s)]+'
space_regex = '[(\n)(\s)]+'
#labels
label_modem_request_epoch_time = 'request_epoch_time'
label_modem_request_timestamp = 'request_timestamp'
label_modem_url = 'url'
label_modem_model = 'Model'
label_modem_vendor = 'Vendor'
label_modem_hardware_revision = 'HardwareRevision'
label_modem_mac_address = 'MACAddress'
label_modem_bootloader_revision = 'BootloaderRevision'
label_modem_current_software_revision = 'CurrentSoftwareRevision'
label_modem_firmware_name = 'FirmwareName'
label_modem_firmware_built_time = 'FirmwareBuildTime'
label_modem_cable_modem_status = 'CableModemStatus'
label_modem_downstream_channel_01_power = 'channel_1 ch_pwr'
label_modem_downstream_channel_01_signal = 'channel_1 ch_snr'
label_modem_downstream_channel_02_power = 'channel_2 ch_pwr'
label_modem_downstream_channel_02_signal = 'channel_2 ch_snr'
label_modem_downstream_channel_03_power = 'channel_3 ch_pwr'
label_modem_downstream_channel_03_signal = 'channel_3 ch_snr'
label_modem_downstream_channel_04_power = 'channel_4 ch_pwr'
label_modem_downstream_channel_04_signal = 'channel_4 ch_snr'
label_modem_downstream_channel_05_power = 'channel_5 ch_pwr'
label_modem_downstream_channel_05_signal = 'channel_5 ch_snr'
label_modem_downstream_channel_06_power = 'channel_6 ch_pwr'
label_modem_downstream_channel_06_signal = 'channel_6 ch_snr'
label_modem_downstream_channel_07_power = 'channel_7 ch_pwr'
label_modem_downstream_channel_07_signal = 'channel_7 ch_snr'
label_modem_downstream_channel_08_power = 'channel_8 ch_pwr'
label_modem_downstream_channel_08_signal = 'channel_8 ch_snr'
label_modem_upstream_channel_01_power = 'up_channel_1 up_pwr'
label_modem_upstream_channel_02_power = 'up_channel_2 up_pwr'
label_modem_upstream_channel_03_power = 'up_channel_3 up_pwr'
label_modem_upstream_channel_04_power = 'up_channel_4 up_pwr'

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
            output_dict[label_modem_model] = re.sub(space_regex, '', str(soup.find('td', headers=label_modem_model).text))
            output_dict[label_modem_vendor] = re.sub(space_regex, '', str(soup.find('td', headers=label_modem_vendor).text))
            output_dict[label_modem_hardware_revision] = re.sub(space_regex, '', str(soup.find('td', headers=label_modem_hardware_revision).text))
            output_dict[label_modem_mac_address] = re.sub(space_regex, '', str(soup.find('td', headers=label_modem_mac_address).text))
            output_dict[label_modem_bootloader_revision] = re.sub(space_regex, '', str(soup.find('td', headers=label_modem_bootloader_revision).text))
            output_dict[label_modem_current_software_revision] = re.sub(space_regex, '', str(soup.find('td', headers=label_modem_current_software_revision).text))
            output_dict[label_modem_firmware_name] = re.sub(space_regex, '', str(soup.find('td', headers=label_modem_firmware_name).text))
            output_dict[label_modem_firmware_built_time] = re.sub(space_regex, '', str(soup.find('td', headers=label_modem_firmware_built_time).text))
            output_dict[label_modem_cable_modem_status] = re.sub(space_regex, '', str(soup.find('td', headers=label_modem_cable_modem_status).text))
            output_dict[label_modem_downstream_channel_01_power] = re.sub(pwr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_01_power).text))
            output_dict[label_modem_downstream_channel_01_signal] = re.sub(snr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_01_signal).text))
            output_dict[label_modem_downstream_channel_02_power] = re.sub(pwr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_02_power).text))
            output_dict[label_modem_downstream_channel_02_signal] = re.sub(snr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_02_signal).text))
            output_dict[label_modem_downstream_channel_03_power] = re.sub(pwr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_03_power).text))
            output_dict[label_modem_downstream_channel_03_signal] = re.sub(snr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_03_signal).text))
            output_dict[label_modem_downstream_channel_04_power] = re.sub(pwr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_04_power).text))
            output_dict[label_modem_downstream_channel_04_signal] = re.sub(snr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_04_signal).text))
            output_dict[label_modem_downstream_channel_05_power] = re.sub(pwr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_05_power).text))
            output_dict[label_modem_downstream_channel_05_signal] = re.sub(snr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_05_signal).text))
            output_dict[label_modem_downstream_channel_06_power] = re.sub(pwr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_06_power).text))
            output_dict[label_modem_downstream_channel_06_signal] = re.sub(snr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_06_signal).text))
            output_dict[label_modem_downstream_channel_07_power] = re.sub(pwr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_07_power).text))
            output_dict[label_modem_downstream_channel_07_signal] = re.sub(snr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_07_signal).text))
            output_dict[label_modem_downstream_channel_08_power] = re.sub(pwr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_08_power).text))
            output_dict[label_modem_downstream_channel_08_signal] = re.sub(snr_regex, '', str(soup.find('td', headers=label_modem_downstream_channel_08_signal).text))
            output_dict[label_modem_upstream_channel_01_power] = re.sub(pwr_regex, '', str(soup.find('td', headers=label_modem_upstream_channel_01_power).text))
            output_dict[label_modem_upstream_channel_02_power] = re.sub(pwr_regex, '', str(soup.find('td', headers=label_modem_upstream_channel_02_power).text))
            output_dict[label_modem_upstream_channel_03_power] = re.sub(pwr_regex, '', str(soup.find('td', headers=label_modem_upstream_channel_03_power).text))
            output_dict[label_modem_upstream_channel_04_power] = re.sub(pwr_regex, '', str(soup.find('td', headers=label_modem_upstream_channel_04_power).text))
            return output_dict
        else:
            raise Exception('fail http response code: ' + str(response.status_code))
    else:
        raise Exception('null response object')        
    
    
if __name__ == '__main__':
    main()
