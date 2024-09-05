from rtmidi.midiutil import open_midioutput

connection_daw = [0xF0, 0x0, 0x20, 0x6B, 0x7F, 0x42, 0x2, 0x2, 0x40, 0x6A, 0x21, 0xF7]
L_VALUE = None
L_PARAM_NAME = None
L_CENTERED_VALUE = None
L_MIN_VALUE = None
L_MAX_VALUE = None
L_HW_VALUE = 1
L_HW_CONTROL_ID = 1
LAST_VALUE_NUMBER = 42  # this was undefined
LAST_CONTROL_ID = 42
PARAM_STATUS = [
    LAST_VALUE_NUMBER,
    LAST_CONTROL_ID,
    L_CENTERED_VALUE,
    L_MIN_VALUE,
    L_MAX_VALUE,
    L_HW_VALUE,
    L_HW_CONTROL_ID,
]
REC = "00"
PLAY = "00"


class Minilab3:
    def __init__(self):
        self.midi_out, self.port_name = open_midioutput(
            "Minilab3:Minilab3 Minilab3 MIDI"
        )
        self.midi_out.send_message(connection_daw)
        self.midi_out.send_message(self.make_lcd_midi_message("pisynth", "ready !", 10))

    def show_prog_name(self, name):
        name1 = name[0:16]
        name2 = name[16:]
        self.midi_out.send_message(self.make_lcd_midi_message(name1, name2, 10))

    def string_to_hex(self, text):
        # Convert a string to a list of hexadecimal numbers (useful for SysEx messages)
        hex_string_to_return = ""
        for i in range(len(text)):
            if hex_string_to_return:
                hex_string_to_return += " "
            hex_string_to_return += hex(ord(text[i]))[2:].upper()
        return hex_string_to_return

    def string_to_table(self, string):
        out = []
        for i in string.split(" "):
            if len(i) < 1:
                continue
            out.append(int(i, 16))
        return out

    def make_lcd_midi_message(self, line1, line2, page_type):
        # Returns a list containing the SysEx message to display on the MiniLab3 screen
        data_control = ""

        if page_type == 1:
            data_control = ""
        if page_type == 2:
            data_control = "1F 02 01"
        if page_type == 3:
            print(PARAM_STATUS[6])
            if len(hex(PARAM_STATUS[6])[2:]) == 1:
                data_control = "1F 03 01 0" + hex(PARAM_STATUS[6])[2:]
            else:
                data_control = "1F 03 01 " + hex(PARAM_STATUS[6])[2:]
        if page_type == 4:
            if len(hex(PARAM_STATUS[6])[2:]) == 1:
                data_control = "1F 04 01 0" + hex(PARAM_STATUS[6])[2:]
            else:
                data_control = "1F 04 01 " + hex(PARAM_STATUS[6])[2:]
        if page_type == 5:
            data_control = "1F 05 01 00"

        if page_type == 10:
            data_control = "1F 07 01 " + REC + " " + PLAY + " 01"

        sysex = (
            "f0 00 20 6b 7f 42 04 02 60 "
            + data_control
            + " 00 00 01 "
            + self.string_to_hex(line1[:31])
            + " 00 02 "
            + self.string_to_hex(line2[:31])
            + " 00 f7 "
        )
        result_table = self.string_to_table(sysex)

        return result_table
