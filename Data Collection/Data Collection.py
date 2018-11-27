
# coding: utf-8

# In[4]:


import argparse
import codecs
import logging
import os
import random
import re
import signal
import socket
import string
import subprocess
import time
from datetime import datetime
from enum import Enum

import uiautomator
from uiautomator import Device


# In[32]:


def start_emulator(avdnum, emuname, window_sel):
    android_home = os.environ['ANDROID_HOME'] + '/'
    while True:
        msg = subprocess.Popen(
            [android_home + 'platform-tools/adb', '-s', emuname, 'shell', 'getprop', 'init.svc.bootanim'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        bootmsg = msg.communicate()
        if bootmsg[0] == b'stopped\n':
            time.sleep(3)
            subprocess.Popen([android_home + 'platform-tools/adb', '-s', emuname, 'shell', 'rm', '-r', '/mnt/sdcard/*'])
            return 1
        elif len(re.findall('not found', bootmsg[1].decode('utf-8'))) >= 1:
            print(re.findall('not found', bootmsg[1].decode('utf-8')))
            if window_sel:
                subprocess.Popen(
                    [android_home + 'emulator/emulator', '-avd', avdnum, '-wipe-data', '-skin', '1080x1920', '-port',
                     emuname[-4:], '-no-snapstorage'], stderr=subprocess.DEVNULL)
            elif not window_sel:
                subprocess.Popen(
                    [android_home + 'emulator/emulator', '-avd', avdnum, '-wipe-data', '-skin', '1080x1920', '-no-audio',
                     '-no-window', '-port', emuname[-4:], '-no-snapstorage'], stderr=subprocess.DEVNULL)
            time.sleep(10)
        else:
            time.sleep(5)


# In[34]:


def install(apkdir):

    dir = apkdir
    android_home = os.environ['ANDROID_HOME'] + '/'

    with open(apkdir + 'apklist.txt', 'r') as f:
        apks_to_test = [line.rstrip() for line in f]
        
    for i in apks_to_test:
        x = subprocess.Popen([android_home + 'platform-tools/adb', '-s', device_name, 'install', dir + i],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    

try:
    device_name = "emulator-5554"
    avdname = "Nexus_5X_API_28"
    d = Device(device_name)
    start_emulator(avdname, device_name, window_sel=True)
    install('/Users/xikaioliver/Desktop/APKDir/')

except Exception as e:
    print(e)


# In[ ]:


activities = {}
clickables = {}
click_hash = {}
scores = {}
visited = {}
parent_map = {}
zero_counter = 0
horizontal_counter = 0
no_clickable_btns_counter = 0
sequence = []

def official(_apkdir):
    global no_clickable_btns_counter

    dir = _apkdir

    with open(apklist, 'r') as f:
        apks_to_test = [line.rstrip() for line in f]
    timestr = time.strftime("%Y%m%d%H%M%S")

    info_location = Config.info_location
    if not os.path.exists(info_location):
        os.makedirs(info_location)
    file = codecs.open(info_location + '/information-' + timestr + '.txt', 'w', 'utf-8')

    no_apks_tested = 0
    start_time = datetime.now()
    for i in apks_to_test:
        english = True
        attempts = 0
        m = re.findall('^(.*)_.*\.apk', i)
        apk_packname = m[0]

        ''' Get the application name from badge. '''
        try:
            ps = subprocess.Popen([android_home + 'build-tools/26.0.1/aapt', 'dump', 'badging', dir + i],
                                  stdout=subprocess.PIPE)
            output = subprocess.check_output(('grep', 'application-label:'), stdin=ps.stdout)
            label = output.decode('utf-8')
        except subprocess.CalledProcessError:
            print("No android application available.")
            label = 'application-label: unknown APK.'

        m = re.findall('^application-label:(.*)$', label)
        appname = m[0][1:-1]

        Config.app_name = appname

        ''' Check if there is non-ASCII character. '''
        for scii in m[0]:
            if scii not in string.printable:
                print('There is a non-ASCII character in application name. Stop immediately.\n')
                file.write('|' + apk_packname + '|' + 'Non-ASCII character detected in appname.' '\n')
                english = False
                break

        if english:
            if not os.path.exists(Config.seqq_location + apk_packname):
                os.makedirs(Config.seqq_location + apk_packname)

            ''' Start installation of the APK '''
            x = subprocess.Popen([android_home + 'platform-tools/adb', '-s', device_name, 'install', dir + i],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            installmsg = x.communicate()[1].decode('utf-8')
            if len(re.findall('Success', installmsg)) > 0:
                print("Installed success: " + apk_packname + ' APK.')
                pass
            if len(re.findall('INSTALL_FAILED_ALREADY_EXISTS', installmsg)) > 0:
                print("Already exists: " + apk_packname + ' APK.')
                pass
            elif len(re.findall('INSTALL_FAILED_NO_MATCHING_ABIS', installmsg)) > 0:
                print('No Matching ABIs: ' + apk_packname + ' APK.')
                file.write('|' + apk_packname + '|' + 'Failed to install; no matching ABIs' '\n')
                continue
            else:
                pass

            print('\nDoing a UI testing on application ' + appname + '.')

            init()
            if not os.path.exists(Config.seqq_location + apk_packname):
                os.makedirs(Config.seqq_location + apk_packname)
            with open(Config.seqq_location + apk_packname + '/seqq-' + apk_packname + '.txt', 'a') as f:
                f.write('=== BEGIN OF SEQUENCE ===\n')
            no_clickable_btns_counter = 0
            while attempts <= 3:
                signal.alarm(60)
                try:
                    retvalue = main(appname, apk_packname)
                    if retvalue == APP_STATE.FAILTOSTART:
                        logger.info("Fail to start application using monkey.")
                        file.write('|' + apk_packname + '|' + 'Failed to start application using monkey.' '\n')
                        break
                    elif retvalue == APP_STATE.KEYERROR:
                        logger.info("Keyerror crash.")
                        file.write('|' + apk_packname + '|' + 'Crashed - KeyError' '\n')
                    elif retvalue == APP_STATE.INDEXERROR:
                        logger.info("Indexerror crash.")
                        file.write('|' + apk_packname + '|' + 'Crashed - IndexError' '\n')
                    elif retvalue == APP_STATE.CRASHED:
                        logger.info("App crashed")
                        file.write('|' + apk_packname + '|' + 'Crashed - UnknownError' '\n')
                        break
                    elif retvalue == APP_STATE.DEADLOCK:
                        logger.info("Dead lock. Restarting...")
                    elif retvalue == APP_STATE.FAILTOCLICK:
                        logger.info("Fail to click. Restarting...")
                    elif retvalue == APP_STATE.TIMEOUT:
                        logger.info("Timeout. Restarting...")
                    elif retvalue == APP_STATE.JSONRPCERROR:
                        logger.info("JSONRPCError. Restarting...")
                    elif retvalue == APP_STATE.SOCKTIMEOUTERROR:
                        logger.info("Socket timeout. Restarting...")
                    elif retvalue == APP_STATE.KEYBOARDINT:
                        logger.info("keyboard interrupt. Restarting...")
                except BaseException as e:
                    if re.match('timeout', str(e), re.IGNORECASE):
                        logger.info("Timeout from nothing happening. Restarting... ")
                    else:
                        logger.info("Unknown exception." + str(e))
                        # raise Exception(e)
                finally:
                    signal.alarm(0)
                    attempts += 1
                    logger.info('==========================================')
                    new_time = datetime.now()
                    logger.info('Current time is ' + str(new_time))
                    logger.info('Time elapsed: ' + str(new_time - start_time))
                    logger.info('Last APK tested is: {}'.format(apk_packname))
                    logger.info('==========================================')
                    with open(Config.seqq_location + apk_packname + '/seqq-' + apk_packname + '.txt', 'a') as f:
                        while sequence:
                            i = sequence.pop()
                            f.write('{}\t{}\n'.format(i[0], i[1]))
                        f.write('=== END ATTEMPT {} ===\n'.format(attempts))

            with open(Config.seqq_location + apk_packname + '/seqq-' + apk_packname + '.txt', 'a') as f:
                while sequence:
                    i = sequence.pop()
                    f.write('{}\t{}\n'.format(i[0], i[1]))
                f.write('=== END OF SEQUENCE\n')
            logger.info('Force stopping ' + apk_packname + ' to end test for the APK')
            subprocess.Popen(
                [android_home + 'platform-tools/adb', '-s', device_name, 'shell', 'am', 'force-stop', apk_packname])

            act_c = mongo.activity.count({"_type": "activity", "parent_app": Config.app_name})
            click_c = mongo.clickable.count({"_type": "clickable", "parent_app_name": Config.app_name})
            file.write(appname + '|' + apk_packname + '|True|' + str(act_c) + '|' + str(click_c) + '\n')
            subprocess.Popen([android_home + 'platform-tools/adb', '-s', device_name, 'uninstall', apk_packname],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info('Uninstalled ' + apk_packname)
            logger.info('@@@@@@@@@@@ End ' + apk_packname + ' APK @@@@@@@@@@@')

        no_apks_tested += 1
        if no_apks_tested % 50 == 0:
            logger.info('Total apks tested: {}'.format(no_apks_tested))
            logger.info('Restarting emulator...')
            Utility.stop_emulator(device_name)
            time.sleep(10)
            Utility.start_emulator(avdname, device_name, window_sel=args.window)

            logger.info('==========================================')
            new_time = datetime.now()
            logger.info('Current time is ' + str(new_time))
            logger.info('Time elapsed: ' + str(new_time - start_time))
            logger.info('Last APK tested is: {}'.format(apk_packname))
            logger.info('==========================================')


# In[ ]:


def init():
    """
    Initializing all global variables back to its original state after every testing is done on APK
    :return:
    """
    global clickables, scores, visited, parent_map, activities, click_hash, zero_counter, sequence
    activities.clear()
    clickables.clear()
    click_hash.clear()
    scores.clear()
    visited.clear()
    parent_map.clear()
    zero_counter = 0
    horizontal_counter = 0
    sequence = []


# In[ ]:


def main(app_name, pack_name):
    global clickables, scores, visited, parent_map, activities, sequence
    d.press('home')

    print('Force stopping ' + pack_name + ' to reset states')
    subprocess.Popen([android_home + 'platform-tools/adb', '-s', device_name, 'shell', 'am', 'force-stop', pack_name])
    print('Starting ' + pack_name + ' using monkey...')
    msg = subprocess.Popen(
        [android_home + '/platform-tools/adb', '-s', device_name, 'shell', 'monkey', '-p', pack_name, '5'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    startmsg = msg.communicate()[0].decode('utf-8')
    if len(re.findall('No activities found to run', startmsg)) > 0:
        return APP_STATE.FAILTOSTART

    learning_data = Data(_appname=app_name,
                         _packname=pack_name,
                         _data_activity=[])

    # To ensure that loading page and everything is done before starting testing
    print('Wait 10 seconds for loading of APK.')
    time.sleep(10)

    old_state = Utility.get_state(d, pack_name)

    def rec(local_state):
        global parent_map

        if Utility.get_package_name(d) == 'com.google.android.apps.nexuslauncher':
            return -2, local_state
        elif Utility.get_package_name(d) != pack_name:
            initstate = Utility.get_state(d, pack_name)
            d.press('back')
            sequence.append(('OUTOFAPK', 'BACK', ''))
            nextstate = Utility.get_state(d, pack_name)
            if nextstate != initstate:
                return -1, nextstate

            # Prepare for the situation of when pressing back button doesn't work
            elif nextstate == initstate:
                localc = 0
                while True:
                    tryclick_btns = d(clickable='true')
                    rand_btn = random.choice(tryclick_btns)
                    rand_btn.click.wait()
                    sequence.append((initstate, 'RAND_BUTTON', ''))
                    nextstate = Utility.get_state(d, pack_name)

                    # Check if app has crashed. If it is, restart
                    crashapp = d(clickable='true', packageName='android')
                    for i in crashapp:
                        if i.info['resourceName'] == 'android:id/aerr_restart'                                 or i.info['resourceName'] == 'android:id/aerr_close':
                            return APP_STATE.CRASHED, nextstate

                    if localc > 2:
                        return APP_STATE.UNK, nextstate
                    if nextstate != initstate:
                        return -1, nextstate
                    localc += 1

        da = DataActivity(_state=local_state,
                          _name=Utility.get_activity_name(d, pack_name, device_name),
                          _parent_app=app_name,
                          _clickables=[])
        activities[local_state] = da
        click_els = d(clickable='true', packageName=pack_name)
        parent_map[local_state] = Utility.create_child_to_parent(dump=d.dump(compressed=False))
        ar = []
        arch = []
        ars = []
        arv = []

        for btn in click_els:
            btn_info = btn.info
            arch.append((Utility.btn_info_to_key(btn_info), btn_info['text']))
        click_hash[local_state] = arch

        for btn in click_hash[local_state]:
            _parent = Utility.get_parent_with_key(btn[0], parent_map[local_state])
            if _parent != -1:
                sibs = Utility.get_siblings(_parent)
                children = Utility.get_children(_parent)
            else:
                sibs = None
                children = None

            ar.append(Clickable(_name=btn[0],
                                _text=btn[1],
                                _parent_activity_state=local_state,
                                _parent_app_name=app_name,
                                _parent=Utility.xml_btn_to_key(_parent),
                                _siblings=[Utility.xml_btn_to_key(sib) for sib in sibs or []],
                                _children=[Utility.xml_btn_to_key(child) for child in children or []]))
            ars.append(-1)
            arv.append([1, 0])

        clickables[local_state] = ar
        scores[local_state] = ars
        visited[local_state] = arv
        Utility.dump_log(d, pack_name, local_state)
        return 1, local_state

    logger.info('Adding new activity.')
    recvalue, new_state = rec(old_state)
    logger.info('Activity has recvalue of ' + str(recvalue))
    if recvalue == APP_STATE.CRASHED:
        return APP_STATE.CRASHED

    new_click_els = None
    counter = 0

    while True:
        signal.alarm(60)
        try:
            edit_btns = d(clickable='true', packageName=pack_name)
            for i in edit_btns:
                i.set_text(Utility.get_text())
            if d(scrollable='true').exists:
                r = random.uniform(0, Config.scroll_probability[2])
                if r < Config.scroll_probability[0]:
                    new_click_els, new_state, state_info = click_button(new_click_els, pack_name, app_name)
                else:
                    logger.info('Scrolling...')
                    if r < Config.scroll_probability[1]:
                        d(scrollable='true').fling()
                        sequence.append((old_state, 'SCROLL DOWN', ''))
                    elif r < Config.scroll_probability[2]:
                        d(scrollable='true').fling.backward()
                        sequence.append((old_state, 'SCROLL UP', ''))

                    new_state = Utility.get_state(d, pack_name)
                    new_click_els = d(clickable='true', packageName=pack_name)
                    state_info = APP_STATE.SCROLLING
            else:
                new_click_els, new_state, state_info = click_button(new_click_els, pack_name, app_name)

            logger.info('Number of iterations: ' + str(counter))
            logger.info('state_info is ' + str(state_info))
            if state_info == APP_STATE.CRASHED:
                return APP_STATE.CRASHED
            elif state_info == APP_STATE.DEADLOCK:
                return APP_STATE.DEADLOCK
            elif state_info == APP_STATE.FAILTOCLICK:
                return APP_STATE.FAILTOCLICK

            if new_state != old_state and (new_state not in scores or new_state not in visited):
                recvalue = -1
                while recvalue == -1:
                    recvalue, new_state = rec(new_state)
                    if new_state in scores:
                        recvalue = 1
                    if recvalue == APP_STATE.UNK:
                        recvalue = 1

            if counter % 30 == 0:
                logger.info('Saving data to database...')
                store_suc = Utility.store_data(learning_data, activities, clickables, mongo)
                logger.info('Data saved to database: {}'.format(store_suc))
                with open(Config.seqq_location + pack_name + '/seqq-' + pack_name + '.txt', 'a') as f:
                    while sequence:
                        i = sequence.pop()
                        f.write('{}\t{}\t{}\n'.format(i[0], i[1], i[2]))
            counter += 1
            if counter >= 300:
                return 1

        except KeyboardInterrupt:
            logger.info('@@@@@@@@@@@@@@@=============================')
            logger.info('KeyboardInterrupt...')
            store_suc = Utility.store_data(learning_data, activities, clickables, mongo)
            logger.info('Data saved to database: {}'.format(store_suc))
            return APP_STATE.KEYBOARDINT
        except KeyError:
            logger.info('@@@@@@@@@@@@@@@=============================')
            logger.info('Crash')
            store_suc = Utility.store_data(learning_data, activities, clickables, mongo)
            logger.info('Data saved to database: {}'.format(store_suc))
            return APP_STATE.KEYERROR
        except IndexError:
            logger.info('@@@@@@@@@@@@@@@=============================')
            logger.info('IndexError...')
            store_suc = Utility.store_data(learning_data, activities, clickables, mongo)
            logger.info('Data saved to database: {}'.format(store_suc))
            return APP_STATE.INDEXERROR
        except TimeoutError:
            logger.info('@@@@@@@@@@@@@@@=============================')
            logger.info('Timeout...')
            store_suc = Utility.store_data(learning_data, activities, clickables, mongo)
            logger.info('Data saved to database: {}'.format(store_suc))
            return APP_STATE.TIMEOUT
        except uiautomator.JsonRPCError:
            logger.info('@@@@@@@@@@@@@@@=============================')
            logger.info('JSONRPCError...')
            store_suc = Utility.store_data(learning_data, activities, clickables, mongo)
            logger.info('Data saved to database: {}'.format(store_suc))
            return APP_STATE.JSONRPCERROR
        except socket.timeout:
            logger.info('@@@@@@@@@@@@@@@=============================')
            logger.info('Socket timeout error...')
            return APP_STATE.SOCKTIMEOUTERROR
        finally:
            signal.alarm(0)
            Utility.dump_log(d, pack_name, Utility.get_state(d, pack_name))
            with open(Config.seqq_location + pack_name + '/seqq-' + pack_name + '.txt', 'a') as f:
                while sequence:
                    i = sequence.pop()
                    f.write('{}\t{}\t{}\n'.format(i[0], i[1], i[2]))


# In[ ]:


import json


class Data(object):
    def __init__(self, _appname, _packname, _app_description=None, _category=None, _data_activity=None):
        self.appname = _appname
        self.packname = _packname
        self.app_description = _app_description
        self.category = _category
        self.data_activity = [] if _data_activity is None else _data_activity

    def __str__(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def encode_data(data):
        return {"_type": "data", "appname": data.appname,
                "packname": data.packname,
                "app_description": data.app_description,
                "category": data.category,
                "data-activity": data.data_activity}

    @staticmethod
    def decode_data(document):
        assert document['_type'] == 'data'
        return Data(_appname=document['appname'],
                    _packname=document['packname'],
                    _app_description=document['app_description'],
                    _category=document['category'],
                    _data_activity=document['data_activity'])

