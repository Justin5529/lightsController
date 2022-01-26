#!/usr/bin/env python3
import sys
import time
sys.path.append('/home/justin/pytradfri')
import sys
import os

folder = os.path.dirname(os.path.abspath(__file__))  # noqa
sys.path.insert(0, os.path.normpath("%s/.." % folder))  # noqa

from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json

import uuid
import argparse
import threading
import time

CONFIG_FILE = "tradfri_standalone_psk.conf"


parser = argparse.ArgumentParser()
parser.add_argument(
    "host", metavar="IP", type=str, help=""
)
parser.add_argument(
    "-K",
    "--key",
    dest="key",
    required=False,
    help="",
)
args = parser.parse_args()

key = "F0s2m2PbIna8dj4E"
ip = "192.168.1.129"


if args.host not in load_json(CONFIG_FILE) and args.key is None:
    print(
        "Please provide the 'Security Code' on the back of your " "Tradfri gateway:",
        end=" ",
    )
    
    if len(key) != 16:
        raise PytradfriError("Invalid 'Security Code' provided.")
    else:
        args.key = key


def observe(api, device):
    def callback(updated_device):
        light = updated_device.light_control.lights[0]
        print("Received message for: %s" % light)

    def err_callback(err):
        print(err)

    def worker():
        api(device.observe(callback, err_callback, duration=120))

    threading.Thread(target=worker, daemon=True).start()
    print("Sleeping to start observation task")
    time.sleep(1)


def run():
    conf = load_json(CONFIG_FILE)

    try:
        identity = conf[args.host].get("identity")
        psk = conf[args.host].get("key")
        api_factory = APIFactory(host=args.host, psk_id=identity, psk=psk)
    except KeyError:
        identity = uuid.uuid4().hex
        api_factory = APIFactory(host=args.host, psk_id=identity)

        try:
            psk = api_factory.generate_psk(args.key)
            print("Generated PSK: ", psk)

            conf[args.host] = {"identity": identity, "key": psk}
            save_json(CONFIG_FILE, conf)
        except AttributeError:
            raise PytradfriError(
                "Please provide the 'Security Code' on the "
                "back of your Tradfri gateway using the "
                "-K flag."
            )

    api = api_factory.request

    gateway = Gateway()

    devices_command = gateway.get_devices()
    devices_commands = api(devices_command)
    devices = api(devices_commands)

    lights = [dev for dev in devices if dev.has_light_control]

    # Print all lights
    print(lights)

    # Lights can be accessed by its index, so lights[1] is the second light
    if lights:
        panel = lights[0]
        bulb = lights[1]
    else:
        print("No lights found!")
        light = None

    if lights:
        def turn_on_lights():
            turn_on_panel = panel.light_control.set_dimmer(100)
            turn_on_bulb = bulb.light_control.set_dimmer(100)
            api(turn_on_panel)
            api(turn_on_bulb)
 
        def turn_off_lights():
            turn_on_panel = panel.light_control.set_dimmer(000)
            turn_on_bulb = bulb.light_control.set_dimmer(000)
            api(turn_on_panel)
            api(turn_on_bulb)

        turn_off_lights()

run()
