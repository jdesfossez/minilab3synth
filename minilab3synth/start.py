#!/usr/bin/env python3

import time
import rtmidi
import logging
from minilab import Minilab3
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, CONTROL_CHANGE
from time import sleep
from rtmidi.midiutil import open_midiinput

import fluidsynth

logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def list_midi_ports():
    midi_in = rtmidi.MidiIn()
    ports = midi_in.get_ports()
    for i, port in enumerate(ports):
        print(f"{i}: {port}")
    return ports


class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, synth):
        message, deltatime = event
        self._wallclock += deltatime
        logger.info("[%s] @%0.6f %s" % (self.port, self._wallclock, message))
        try:
            synth.process_message(message)
        except Exception:
            logger.exception("processing message")


class Synth:
    def __init__(self):
        self.current_bank = 0
        self.current_preset = 0
        self.inst_id = None
        self.drum_id = None
        self.default_inst_bank = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
        self.default_drum_bank = "minilabsynth/PNS_Drim_Kit.SF2"
        self.inst_midi_channel = 0
        self.drum_midi_channel = 9
        self.mlab = Minilab3()
        self.start_fs()
        self.midi_port_name = "Minilab3:Minilab3 Minilab3 MIDI"
        self.connect_midi()

    def start_fs(self):
        self.fs = fluidsynth.Synth()
        self.fs.start()

        self.inst_id = self.fs.sfload(self.default_inst_bank)
        if self.inst_id < 0:
            logger.error("Failed to load soundbank")
            return False
        self.drum_id = self.fs.sfload(self.default_drum_bank)
        if self.drum_id < 0:
            logger.error("Failed to load soundbank")
            return False
        self.program_select(
            self.inst_midi_channel, self.inst_id, self.current_bank, self.current_preset
        )
        self.program_select(self.drum_midi_channel, self.drum_id, 0, 0)
        return True

    def prev_program(self):
        if self.current_preset == 0 and self.current_bank == 0:
            return
        elif self.current_preset > 0:
            self.current_preset -= 1
        elif self.current_preset == 0 and self.current_bank == 1:
            self.current_preset = 128
            self.current_bank = 0
        self.program_select(
            self.inst_midi_channel, self.inst_id, self.current_bank, self.current_preset
        )

    def next_program(self):
        if self.current_preset == 128 and self.current_bank == 1:
            return
        elif self.current_preset < 128:
            self.current_preset += 1
        elif self.current_preset == 128 and self.current_bank == 0:
            self.current_preset = 0
            self.current_bank = 1
        self.program_select(
            self.inst_midi_channel, self.inst_id, self.current_bank, self.current_preset
        )

    def program_select(self, channel, inst_id, bank, preset):
        self.fs.program_select(channel, inst_id, bank, preset)
        name = self.fs.sfpreset_name(self.inst_id, bank, preset)
        self.mlab.show_prog_name(name)
        logger.info(
            f"Channel {channel}, inst {inst_id}, bank {bank}, preset {preset}, name {name}"
        )

    def process_message(self, message):
        if message[0] & 0xF0 == NOTE_ON:
            status, note, velocity = message
            channel = status & 0xF  # + 1
            self.fs.noteon(channel, note, velocity)
        elif message[0] & 0xF0 == NOTE_OFF:
            status, note, velocity = message
            channel = status & 0xF  # + 1
            self.fs.noteoff(channel, note)
        elif message[0] & 0xF0 == CONTROL_CHANGE:
            status, number, value = message
            if number == 28 and value == 65:
                print("UP")
                self.next_program()
            elif number == 28 and value == 62:
                print("DOWN")
                self.prev_program()
            elif number == 118 and value == 127:
                print("OK down")
            elif number == 118 and value == 0:
                print("OK up")

    def connect_midi(self):
        print("Available MIDI input ports:")
        list_midi_ports()

        self.midi_in, self.port_name = open_midiinput(self.midi_port_name)
        logger.info(f"Midi connected {self.port_name}")
        self.midi_in.set_callback(MidiInputHandler(self.port_name), self)


if __name__ == "__main__":
    a = Synth()
    while True:
        sleep(1)
