# lvl_1.py

import RPi.GPIO as GPIO
import time
import random
import mido
import sys
from rpi_ws281x import Color

NEO_COLORS = {
    'red': Color(255, 0, 0),
    'green': Color(0, 255, 0),
    'blue': Color(0, 0, 255),
    'yellow': Color(255, 255, 0)
}

COLOR_MAP = {
    'red': 5,
    'green': 21,
    'blue': 78,
    'yellow': 13,
    'cyan': 3,
    'orange': 37,
    'magenta': 54,
    'yellowgreen': 91,
    'white': 122,
    'brown': 127,
    'off': 0
}

inport1 = mido.open_input("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 20:0")
outport1 = mido.open_output("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 20:0")
inport2 = mido.open_input("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 24:0")
outport2 = mido.open_output("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 24:0")

launchpad_grid = [[81 - 10 * r + c for c in range(8)] for r in range(8)]

def clear_pixels(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

def clear_board(outport):
    for row in launchpad_grid:
        for n in row:
            outport.send(mido.Message('note_on', note=n, velocity=0))

def show_sequence_on_strip(strip, sequence):
    num_colors = len(sequence)
    pixels_per_color = strip.numPixels() // num_colors
    index = 0
    for color in sequence:
        c = NEO_COLORS[color]
        for _ in range(pixels_per_color):
            if index < strip.numPixels():
                strip.setPixelColor(index, c)
                index += 1
    while index < strip.numPixels():
        strip.setPixelColor(index, Color(0, 0, 0))
        index += 1
    strip.show()

def get_unique_sequence(length):
    base = ['red', 'green', 'blue', 'yellow']
    pool = [random.choice(base) for _ in range(length)]
    while any(pool[i] == pool[i + 1] for i in range(len(pool) - 1)):
        pool = [random.choice(base) for _ in range(length)]
    return pool

def get_2x2_block(x, y):
    return [launchpad_grid[y + dy][x + dx] for dy in range(2) for dx in range(2)]

def light_block(outport, block, color):
    vel = COLOR_MAP[color]
    for n in block:
        outport.send(mido.Message('note_on', note=n, velocity=vel))

def flush_midi_input(inport):
    while inport.poll():
        pass

def setup_blocks():
    all_positions = [(x, y) for x in range(0, 7, 2) for y in range(0, 7, 2)]
    random.shuffle(all_positions)
    return [get_2x2_block(x, y) for x, y in all_positions]

def draw_blocks(player, sequence):
    player['note_map'].clear()
    for i in range(player['index'], len(sequence)):
        blk = player['blocks'][i]
        color = sequence[i]
        light_block(player['outport'], blk, color)
        for n in blk:
            player['note_map'][n] = (blk, color)

def restart_sequence(player, sequence):
    player['index'] = 0
    clear_board(player['outport'])
    draw_blocks(player, sequence)

def flash_winner(winner):
    for _ in range(3):
        for row in launchpad_grid:
            for n in row:
                outport1.send(mido.Message('note_on', note=n, velocity=COLOR_MAP['green' if winner == 1 else 'red']))
                outport2.send(mido.Message('note_on', note=n, velocity=COLOR_MAP['green' if winner == 2 else 'red']))
        time.sleep(0.2)
        clear_board(outport1)
        clear_board(outport2)
        time.sleep(0.1)

def run_level_1(reaper_client, light_client, strip):
    try:
        print("[OSC] REAPER: /marker/26")
        reaper_client.send_message("/marker/26", 1.0)

        print("[OSC] LIGHT: Off Sequence thru Please")
        light_client.send_message("/gma3/cmd", "Off Sequence thru Please")
        print("[OSC] LIGHT: Go+ Sequence 55")
        light_client.send_message("/gma3/cmd", "Go+ Sequence 55")
        time.sleep(2)
        print("[OSC] LIGHT: Off Sequence thru Please")
        light_client.send_message("/gma3/cmd", "Off Sequence thru Please")
        print("[OSC] LIGHT: Go+ Sequence 54")
        light_client.send_message("/gma3/cmd", "Go+ Sequence 54")

        seq_len = 4
        sequence = get_unique_sequence(seq_len)
        show_sequence_on_strip(strip, sequence)
        clear_board(outport1)
        clear_board(outport2)

        last_press_time = [0, 0]
        debounce_threshold = 0.25

        flush_midi_input(inport1)
        flush_midi_input(inport2)
        time.sleep(0.5)

        player_data = [
            {'inport': inport1, 'outport': outport1, 'state': 'PLAY', 'red_end': 0, 'index': 0, 'note_map': {}, 'blocks': setup_blocks()},
            {'inport': inport2, 'outport': outport2, 'state': 'PLAY', 'red_end': 0, 'index': 0, 'note_map': {}, 'blocks': setup_blocks()}
        ]

        for player in player_data:
            draw_blocks(player, sequence)

        flush_midi_input(inport1)
        flush_midi_input(inport2)

        winner_found = False

        while not winner_found:
            now = time.time()
            for i, player in enumerate(player_data):
                if player['state'] == 'RED':
                    if now >= player['red_end']:
                        restart_sequence(player, sequence)
                        flush_midi_input(player['inport'])
                        player['state'] = 'PLAY'
                    continue

                msg = player['inport'].receive(block=False)
                if msg and msg.type == 'note_on' and msg.velocity > 0:
                    if now - last_press_time[i] < debounce_threshold:
                        continue
                    last_press_time[i] = now

                    note = msg.note
                    if note in player['note_map']:
                        blk, pressed = player['note_map'][note]
                        expected = sequence[player['index']]
                        if pressed == expected:
                            for n in blk:
                                player['note_map'].pop(n, None)
                            light_block(player['outport'], blk, 'off')
                            player['index'] += 1
                            if player['index'] == len(sequence):
                                flash_winner(i + 1)

                                if i == 0:
                                    print("[OSC] REAPER: /marker/27 + /action/1007")
                                    reaper_client.send_message("/marker", 27)
                                    reaper_client.send_message("/action", 1007)
                                else:
                                    print("[OSC] REAPER: /marker/29 + /action/1007")
                                    reaper_client.send_message("/marker", 29)
                                    reaper_client.send_message("/action", 1007)

                                flush_midi_input(player['inport'])
                                clear_board(outport1)
                                clear_board(outport2)
                                clear_pixels(strip)
                                winner_found = True
                                break
                        else:
                            print("[OSC] REAPER: /marker/30 (wrong press)")
                            reaper_client.send_message("/marker/30", 1.0)
                            print("[OSC] LIGHT: Off Sequence thru Please")
                            light_client.send_message("/gma3/cmd", "Off Sequence thru Please")
                            print("[OSC] LIGHT: Go+ Sequence 58")
                            light_client.send_message("/gma3/cmd", "Go+ Sequence 58")

                            for row in launchpad_grid:
                                for n in row:
                                    player['outport'].send(mido.Message('note_on', note=n, velocity=COLOR_MAP['red']))
                            flush_midi_input(player['inport'])
                            player['state'] = 'RED'
                            player['red_end'] = now + 1.5
            time.sleep(0.005)

    except KeyboardInterrupt:
        clear_board(outport1)
        clear_board(outport2)
        clear_pixels(strip)
        GPIO.cleanup()
        sys.exit(0)
