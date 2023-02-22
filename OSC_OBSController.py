import json
import os
import re
import time
import sys
import subprocess
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
import obsws_python as obs
from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder

#global
syncing = False
startuping = False
obsConfig = 0
oscConfig = 0
oscServer = 0
ErrorType = 0
ErrorMessages = 0
parameters = 0
devices = 0
scenes = 0
sync_delay = 0
scene_str  = 0
volume_str = 0
success = 0
setup = 0
synced = 0
sync_complete = 0
mute_str = 0
record_str = 0
replay_str = 0
client = 0
cl = 0

LatestVideosPath = ""

def startup(v):
    global syncing,client,cl,oscConfig,ErrorType,ErrorMessages,parameters
    global devices,scenes,sync_delay,scene_str,volume_str,success
    global setup,synced,synced,sync_complete,mute_str,record_str
    global replay_str,oscServer

    if v == 1:
        syncing = True
        sync_parameter(True,"/avatar/parameters/syncing")

    #jsons
    setting_json = json.load(open('config/config.json', 'r',encoding="utf-8"))
    locales_json = json.load(open(setting_json['locales'], 'r',encoding="utf-8"))

    obsConfig = [
        setting_json['connection']["OBS"]['host'],
        setting_json['connection']["OBS"]['port'],
        setting_json['connection']["OBS"]['password'],
    ]

    Client = [
        setting_json['connection']["Client"]['IP'],
        setting_json['connection']["Client"]['Port']
    ]

    oscConfig = [
        setting_json['connection']["Server"]['IP'],
        setting_json['connection']["Server"]['Port']
    ]

    ErrorType = locales_json['messages']['error']['type']
    ErrorMessages = [
        ErrorType[0] + ": " + locales_json['messages']['error']['strings']['InvalidName'],
        ErrorType[0] + ": " + locales_json['messages']['error']['strings']['InvalidScene'],
        ErrorType[0] + ": " + locales_json['messages']['error']['strings']['ConnectionError']
    ]

    parameters = [
        setting_json['parameters']['volumes'],
        setting_json['parameters']['mutes'],
        setting_json['parameters']['controls']
    ]
    devices = []
    scenes = []
    sync_delay = setting_json['sync_delay']


    scene_str  = locales_json['messages']['scene_str']['set']
    volume_str = locales_json['messages']['volume_str']['set']
    success = locales_json['messages']['success']
    setup = locales_json['messages']['setup']
    synced = locales_json['messages']['synced']

    sync_complete = locales_json['messages']['sync_complete']

    mute_str = [
        locales_json['messages']['mute_str']['unmuted'],
        locales_json['messages']['mute_str']['muted'],
    ]
    record_str = locales_json['messages']['record_str']
    replay_str = locales_json['messages']['replay_str']

    client = udp_client.UDPClient(Client[0], Client[1])
    try:
        cl = obs.ReqClient(host=obsConfig[0], port=obsConfig[1], password=obsConfig[2])

    except ConnectionRefusedError:
        print(ErrorMessages[2])
        sys.exit()

    array_scene = cl.get_scene_list().scenes
    scene_item_list = []
    scene_name = []

    for _scenes in array_scene:
        scene_name.append(_scenes['sceneName'])
        print("Scene found: %s" % (_scenes['sceneName']))
        scene_item_list.append(cl.get_scene_item_list(_scenes['sceneName']).scene_items)
        scenes.append([0]*len(scene_item_list[array_scene.index(_scenes)]))

    l = cl.get_input_list().inputs

    for x in reversed(l):
        if x['inputKind'] == "wasapi_output_capture" or x['inputKind'] == "wasapi_input_capture":
            devices.append(x['inputName'])
            print("Device found: %s" % (x['inputName']))
        else:
            for q in scene_item_list:
                for scene in q:
                    if x['inputName'] == scene['sourceName']:
                        scenes[scene_item_list.index(q)][scene['sceneItemIndex']] = x['inputName']
                        print("Item found: %s" % (scenes[scene_item_list.index(q)][scene['sceneItemIndex']]))
    
    for scene in scenes:
        scene.reverse()
    
    scene_name.reverse()
    scenes.reverse()

    if v == 1:
        syncing = False
        sync_parameter(False,"/avatar/parameters/syncing")
        oscServer.server_address = (oscConfig[0], oscConfig[1])

def set_current_scene(unused_addr, i):
    if syncing: return
    if scenes[i] == "":
        print(ErrorMessages[1])
        return
    scene = scenes[i]
    print(scene_str % (scene))
    cl.set_current_program_scene(scene)


def set_device_volume(unused_addr, f):
    if syncing: return
    i = int(re.sub(r"\D", "",unused_addr))
    if devices[i] == "":
        print(ErrorMessages[0])
        return
    device = devices[i]
    print(volume_str % (device, f))
    cl.set_input_volume(device,vol_db=(f-1)*100)

def set_device_mute(unused_addr, b):
    if syncing: return
    i = int(re.sub(r"\D", "",unused_addr)) #多分コレやめた方がいい
    if devices[i] == "":    
        print(ErrorMessages[0])
        return
    device = devices[i]
    print(mute_str[int(b)] % (device))
    cl.set_input_mute(device,b)
    
def StartStopRecord(unused_addr, b):
    if syncing: return
    records(int(b))

def PauseResumeRecord(unused_addr, b):
    if syncing: return
    records((int(b)+2))

def records(i):
    global LatestVideosPath
    print(record_str[i])
    if i == 0:
        LatestVideosPath = cl.stop_record().output_path
    elif i == 1:
        cl.start_record()
    elif i == 2:
        cl.resume_record()
    elif i == 3:
        cl.pause_record()


def StartStopReplay(unused_addr, b):
    if syncing: return
    replays(int(b))

def SaveReplay(unused_addr, b):
    if syncing: return
    if b:
        replays(2)

def replays(i):
    global LatestVideosPath
    if i == 0: 
        cl.stop_replay_buffer()
    elif i == 1:
        cl.start_replay_buffer()
    elif i== 2:
        cl.save_replay_buffer()
        LatestVideosPath = cl.get_last_replay_buffer_replay().saved_replay_path
    print(replay_str[i])

def StartStopStreaming(unused_addr, b):
    if syncing: return
    if b:
        cl.start_stream()
    else:
        cl.stop_stream()

def OpenLatestVideo(unused_addr, b):
    if b:
        subprocess.Popen(LatestVideosPath, shell=True)
    
def OpenVideoFolder(unused_addr, b):
    if b:
        os.system('explorer.exe %s' % ((os.path.dirname(LatestVideosPath)).replace("/","\\")))

def StopServer(unused_addr, b):
    if b:
        oscServer.shutdown()
        sys.exit()

def Reload(unused_addr, b):
    if b:
        startup(1)
        sync_values(unused_addr, b)


def sync_parameter(v,address):
        time.sleep(sync_delay)
        msg = OscMessageBuilder(address)
        msg.add_arg(v)
        m = msg.build()
        client.send(m)
        print(synced % (address,str(v)))

def sync_values(unused_addr, b):
    if b:
        global syncing
        syncing = True
        sync_parameter(True,"/avatar/parameters/syncing")
        i = 0
        for device in devices:
            if parameters[0][i] == 0:
                break
            if device == 0 or device == "":
                i+=1
                continue    
            f = cl.get_input_volume(devices[i]).input_volume_db
            sync_parameter((f+100)/100,parameters[0][i])
            i+=1

        i = 0
        for device in devices:
            if parameters[1][i] == 0:
                break
            if device == 0 or device == "":
                i+=1
                continue
            sync_parameter(cl.get_input_mute(devices[i]).input_muted,parameters[1][i])
            i+=1

        sync_parameter(cl.get_record_status().output_active,parameters[2][1])
        sync_parameter(cl.get_record_status().output_paused,parameters[2][2])
        sync_parameter(cl.get_replay_buffer_status().output_active,parameters[2][3])
        sync_parameter(cl.get_stream_status().output_active,parameters[2][5])
        

        syncing = False
        sync_parameter(False,"/avatar/parameters/syncing")
        print(sync_complete)

startup(0)

dispatcher = Dispatcher()

i = 0
for device in devices:
    if parameters[0][i] == 0:
        break
    if device == 0 or device == "":
        i+=1
        continue
    dispatcher.map(parameters[0][i], set_device_volume)
    print(setup % (parameters[0][i]))
    i+=1

i = 0
for device in devices:
    if parameters[1][i] == 0:
        break
    if device == 0 or device == "":
        i+=1
        continue
    dispatcher.map(parameters[1][i], set_device_mute)
    print(setup % (parameters[1][i]))
    i+=1

dispatcher.map("/avatar/change", sync_values)                           # boolean
dispatcher.map(parameters[2][0], sync_values)                           # boolean but used like a Trigger
print(setup % (parameters[2][0]))
dispatcher.map(parameters[2][1], StartStopRecord)                       # boolean
print(setup % (parameters[2][1]))
dispatcher.map(parameters[2][2], PauseResumeRecord)                     # boolean
print(setup % (parameters[2][2]))
dispatcher.map(parameters[2][3], StartStopReplay)                       # boolean
print(setup % (parameters[2][3]))
dispatcher.map(parameters[2][4], SaveReplay)                            # boolean but used like a Trigger
print(setup % (parameters[2][4]))
dispatcher.map(parameters[2][5], StartStopStreaming)                    # boolean
print(setup % (parameters[2][5]))
dispatcher.map(parameters[2][6], OpenLatestVideo)                       # boolean but used like a Trigger
print(setup % (parameters[2][6]))
dispatcher.map(parameters[2][7], OpenVideoFolder)                       # boolean but used like a Trigger
print(setup % (parameters[2][7]))
dispatcher.map(parameters[2][8], StopServer)                            # boolean but used like a Trigger
print(setup % (parameters[2][8]))
dispatcher.map(parameters[2][9], Reload)                            # boolean but used like a Trigger
print(setup % (parameters[2][9]))

sync_values("", True)

oscServer = osc_server.ThreadingOSCUDPServer((oscConfig[0], oscConfig[1]), dispatcher)
print(success % (str(oscServer.server_address)))
oscServer.serve_forever()