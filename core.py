#!/bin/python
import subprocess
import json


# Variables (Constants)
DEFAULT_VIDEO = 'totem'
DEFAULT_MUSIC = 'spotify'
APPS = ('totem', 'vlc', 'xbmc', 'rhythmbox')


def try_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return json_object


# Kill all running aps
def killApps():

    # Loop through them and kill them as we go along
    for APP in APPS:
        pid = subprocess.check_output("ps -e | grep " + APP +
                                         " | awk {'print $1'}")
        #print "ps -e | grep " + APP + " | awk {'print $1'} , PID: " + pid

        # If there is a PID, then the application is running and we can kill it
        if pid != '':
            subprocess.check_output('kill ' + pid)
            print('Killing ' + APP + ", VIA: " + 'kill ' + pid)


# This function will be used to confirm whether an application is running
def appRunning(APP):

    # Get the PID, if it exists then the app is running
    pid = subprocess.check_output("ps -e | grep " + APP +
                                     " | awk {'print $1'}")

    # If there is a PID, then the application is indeed running
    return pid != ''


# The dictionary with the commands and switches to be run
DEFAULTS = {
    'up': ['xdotool', 'key', "Up"],
    'down': ['xdotool', 'key', "Down"],
    'left': ['xdotool', 'key', "Left"],
    'right': ['xdotool', 'key', "Right"],
    'ok': ['xdotool', 'key', "KP_Enter"],
    'play': ['xdotool', 'key', "XF86AudioPlay"],
    'info': ['xdotool', 'key', 'Menu'],
    'back': ['xdotool', 'key', "Escape"],
    'next': ['xdotool', 'key', "XF86AudioNext"],
    'prev': ['xdotool', 'key', "XF86AudioPrev"],
    'video': [DEFAULT_VIDEO],
    'stop': ['xdotool', 'key', "XF86AudioStop"],
    'music': [DEFAULT_MUSIC],
    'vol-up': ['xdotool', 'key', "XF86AudioRaiseVolume"],
    'vol-down': ['xdotool', 'key', "XF86AudioLowerVolume"],
    'click': ['xdotool', 'click', "1"],
    'rclick': ['xdotool', 'click', "3"],
    'lock': [
        "dbus-send", "--type=method_call", "--dest=org.gnome.ScreenSaver",
        "/org/gnome/ScreenSaver", "org.gnome.ScreenSaver.Lock"
    ]
}


# This will perform the actions
def commandKeys(pressed):
    verbose = True
    # Did we receive a data string?
    data = try_json(pressed)
    if data:
        # Currently we are only concerned with moving the mouse
        if data['action'] == "mouse-move":

            x = data['x']
            y = data['y']

            if not x or not y:
                mouse_command = ["xdotool", "click", "click"]
            else:
                x = int(x)
                y = int(y)

                # Handle negative values
                if x < 0 or y < 0:
                    mouse_command = [
                        'xdotool', 'mousemove_relative', '--',
                        str(x),
                        str(y)
                    ]
                else:
                    mouse_command = [
                        'xdotool', 'mousemove_relative',
                        str(x), str(y)
                    ]

            # Dispatch the mouse move event
            output = subprocess.check_output(mouse_command)
            if verbose:
                print(mouse_command)
                print(output)

    # Was the keypress valid? If so, run the relevant command
    elif pressed == "power":
        killApps()

    elif pressed == "fullscreen":
        output = subprocess.check_output(DEFAULTS['click'])

    # The media launchers are a bit different, we need to check that the application is not already fired up
    elif pressed in ("video", "music"):

        # Check if it's already running, if not kill all other players listed in apps and open this one
        if not appRunning(str(DEFAULTS[pressed])):
            #killApps()
            appLaunch(DEFAULTS[pressed], True)
            print("Launching " + str(DEFAULTS[pressed]))
        else:
            print(str(DEFAULTS[pressed]) + " is already running")

    # Othewise lets check the action to be run, based on the key pressed
    elif pressed in DEFAULTS.keys():
        output = subprocess.check_output(DEFAULTS[pressed])
        if verbose:
            print(DEFAULTS[pressed], output)

    # Command not found sadly
    else:
        print(pressed, "command not found")


# Applications should be done a bit differently
def appLaunch(action, surpress=False):
    FNULL = open('/dev/null', 'w')
    subprocess.Popen(action, shell=True, stderr=FNULL)
    if not surpress:
        print(action)
