import random
import sys
from typing import Callable

import cwiid

import threading


class Wiimote:
    def __init__(self, wiiId: int):
        self.wiiId = wiiId
        self.subscriber: list[Callable[[int, list[tuple[float, float]]], None]] = []

        counter = 0
        while True:
            try:
                print('Put Wiimote in discoverable mode now (press 1+2)...')
                self.wiimote = cwiid.Wiimote()
                print(2, self.wiimote)
                if not self.wiimote:
                    raise (Exception('No Wiimote'))
                break
            except:
                print(counter, 'Registration failed')
                counter += 1
                if counter > 10:
                    raise (Exception('Failed'))

        self.wiimote.mesg_callback = self.callback

        rpt_mode = 0
        rpt_mode ^= cwiid.RPT_IR
        led = 0
        if self.wiiId == 4:
            led ^= cwiid.LED4_ON
        if self.wiiId == 3:
            led ^= cwiid.LED3_ON
        if self.wiiId == 2:
            led ^= cwiid.LED2_ON
        if self.wiiId == 1:
            led ^= cwiid.LED1_ON
        # if self.wiiId & 1 > 0:
        #     led ^= cwiid.LED4_ON
        # if self.wiiId & 2 > 0:
        #     led ^= cwiid.LED3_ON
        # if self.wiiId & 4 > 0:
        #     led ^= cwiid.LED2_ON
        # if self.wiiId & 8 > 0:
        #     led ^= cwiid.LED1_ON
        self.wiimote.led = led
        self.wiimote.rpt_mode = rpt_mode
        self.wiimote.enable(cwiid.FLAG_MESG_IFC)
        print(f'Wiimote {wiiId} initialized')

    def subscribe(self, callback: Callable[[int, list[tuple[float, float]]], None]):
        self.subscriber.append(callback)

    def notify(self, data: list[tuple[float, float]]):
        for sub in self.subscriber:
            sub(self.wiiId - 1, data)

    def callback(self, mesg_list, time):
        data: list[tuple[float, float]] = []
        for mesg in mesg_list:
            if mesg[0] == cwiid.MESG_IR:
                valid_src = False
                # print('IR Report: ', end=' ')
                # x = [p['pos'][0] for p in mesg[1] if p and p['pos']]
                # y = [p['pos'][1] for p in mesg[1] if p and p['pos']]
                for src in mesg[1]:
                    if src:
                        data.append(src['pos'])
                        print(data)
        self.notify(data)


class Fakemote:
    def __init__(self, wiiId: int):
        self.wiiId = wiiId
        self.subscriber: list[Callable[[int, list[tuple[float, float]]], None]] = []
        threading.Timer(1, self.callback).start()
        print(f'Wiimote {wiiId} initialized')

    def subscribe(self, callback: Callable[[int, list[tuple[float, float]]], None]):
        self.subscriber.append(callback)
        # self.callback()

    def notify(self, data: list[tuple[float, float]]):
        for sub in self.subscriber:
            sub(self.wiiId - 1, data)

    def callback(self):
        data: list[tuple[float, float]] = []

        for _ in range(random.randint(0, 3)):
            data.append((random.uniform(0, 1024), random.uniform(0, 768)))
        self.notify(data)
        threading.Timer(1, self.callback).start()
