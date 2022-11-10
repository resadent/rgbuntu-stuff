#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Eduardo Serralvo Gil <resadent@gmail.com>
from asyncore import read
from binascii import a2b_hex
import sys, re
import os, logging, subprocess
import uuid
sys.path.append('/opt/RGBux/bin/python')
from core.core_choices_dynamic_bg import DEFAULT_CFG, choices_bg, pygame
import menu_utils
from menu_utils import get_basecfg_var,get_config,run_cmd,get_num_lines
from os import listdir
from os.path import isfile, join

#VARIABLE NAME in system config file pointing to menu config file 
ORIENTATION = get_basecfg_var('ORIENTATION')
if ORIENTATION=='normal': menu_cfg_file_var="MENU_CFG_NORMAL_FILE"
if ORIENTATION=='left'  : menu_cfg_file_var="MENU_CFG_LEFT_FILE"
if ORIENTATION=='right' : menu_cfg_file_var="MENU_CFG_RIGHT_FILE"

results = subprocess.run(['sudo', 'blkid'], stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
results.remove(results[len(results) - 1])   # last line is a false positive

FSTAB_PATH="/etc/fstab"
MENU_ON = False
clock = pygame.time.Clock();
clock.tick(30)

def show_info(ch,title,msg):
    ch.set_title(title)
    ch.reset_data()
    ch.load_choices({str(msg) : -1})
    ch.show(False)
    ch.run()[0]

def update_menu_handler(new_handler=False):
    global menu_h
    global MENU_ON
    try:
        lines = get_num_lines()
        if lines=="240":  
            DEFAULT_CFG['font_size'] = 16 
            image_file         = str(get_config('MENU_ANTIMICRO_PROFILE_240_BG'    ,menu_cfg_file_var))  
            image_title_file   = str(get_config('MENU_ANTIMICRO_PROFILE_240_TITLE' ,menu_cfg_file_var))  
        else:                                                                                  
            image_file         = str(get_config('MENU_ANTIMICRO_PROFILE_480_BG'    ,menu_cfg_file_var))  
            image_title_file   = str(get_config('MENU_ANTIMICRO_PROFILE_480_TITLE' ,menu_cfg_file_var))  

        DEFAULT_CFG['image_file'        ] = image_file
        DEFAULT_CFG['image_title_file'  ] = image_title_file 
    except:
        print(" ERROR : Getting configuration ")

    DEFAULT_CFG['cursor'       ] = "cursor.png"
    DEFAULT_CFG['snd_cursor'   ] = "cursor.wav"
    DEFAULT_CFG['snd_load'     ] = "load.wav"  
    DEFAULT_CFG['style'        ] = "choice_rgbuntu"  
    #print(DEFAULT_CFG['image_file'        ] )
    #print(DEFAULT_CFG['image_title_file'  ] )
    if MENU_ON:
        if new_handler:
            # Cambio de resolucion y destruccion del menu
            menu_h.cleanup()
            del menu_h
            menu_h = choices_bg(DEFAULT_CFG) 
    else:                        
        # Creacion del primer menu handler en la resolucion que sea
        MENU_ON=True
        menu_h = choices_bg(DEFAULT_CFG) 
    return
                          
##############################################
## Main
##############################################
class Disk:
    def __init__(self, uuid, parttype, label, device):
        self.uuid = uuid
        self.parttype = parttype
        self.label = label
        self.device = device
    def returnstring(self):
        return self.device + " " + self.label + " " + self.parttype + " " + self.uuid

update_menu_handler() 
Disks = []
i = 0
for lines in results:
    if lines.split('"')[3] != '9fc5f5a9-ee53-47cb-adad-39a84b9f9714':
        Disks.append(Disk(lines.split('"')[3], lines.split('"')[5], lines.split('"')[1], lines.split(':')[0]))

#for disk in Disks:
#    print(disk)

menu_h.set_title("SYSTEMS DISK: ")
menu_h.reset_data()
opts = {}
n = 0

for disk in Disks:
    opts[Disk.returnstring(disk)] = n
    n=n+1
    # print(str(item)+ " : " +str(opts[item]))

menu_h.load_choices(opts)
menu_h.show()
selected_option= menu_h.run()[0]
print("Selected option: " + str(selected_option))
print("Selected option: " + Disk.returnstring(Disks[selected_option]))

## SET CURSOR ON in base config

cmd="sudo sed -i '/\/opt\/systems/d' " + FSTAB_PATH  
print(cmd)
run_cmd(cmd)

newline = "UUID=" + Disks[selected_option].uuid + " /opt/systems " + Disks[selected_option].parttype + " defaults 0 2"
cmd = "sudo sed -i '$ a " + newline + "' " + FSTAB_PATH  
print(cmd)
run_cmd(cmd)

print("New drive is set to: " + Disk.returnstring(Disks[selected_option]))

cmd="cat " + FSTAB_PATH + " | grep /opt/systems"  
output = run_cmd(cmd)
show_info(menu_h,"SYSTEMS DISK HAS BEEN UPDATED", "/opt/RGBux/configs/base-system.conf")

print("Closing menu ...")
menu_h.cleanup()
del menu_h

print("Exit to system ...")
pygame.display.quit()
pygame.quit()
sys.exit(0)
exit()

 
