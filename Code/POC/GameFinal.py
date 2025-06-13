from rpi_ws281x import *
import mido
import time
import random
import signal
import sys

# === LED CONFIG ===
LED_COUNT = 120
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 128
LED_INVERT = False

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

NEO_COLORS = {
    'red': Color(255, 0, 0),
    'green': Color(0, 255, 0),
    'blue': Color(0, 0, 255),
    'yellow': Color(128, 51, 0)
}

COLOR_MAP = {
    'red':    5,
    'green': 21,
    'blue':  78,
    'yellow':13,
    'off':    0,
}

# === MIDI SETUP ===
inport1 = mido.open_input("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 20:0")
outport1 = mido.open_output("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 20:0")
inport2 = mido.open_input("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 24:0")
outport2 = mido.open_output("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 24:0")

launchpad_grid = [[81 - 10*r + c for c in range(8)] for r in range(8)]

def clear_pixels():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

def show_sequence_on_strip(sequence):
    num_colors = len(sequence)
    pixels_per_color = LED_COUNT // num_colors
    index = 0
    for color in sequence:
        c = NEO_COLORS[color]
        for _ in range(pixels_per_color):
            if index < LED_COUNT:
                strip.setPixelColor(index, c)
                index += 1
    strip.show()

def get_unique_sequence(length):
    base = ['red', 'green', 'blue', 'yellow']
    color_count = length // 4
    remainder = length % 4

    pool = base * color_count
    if remainder:
        pool += random.sample(base, remainder)

    random.shuffle(pool)
    while any(pool[i] == pool[i+1] for i in range(len(pool)-1)):
        random.shuffle(pool)

    print("Sequence ({} colors):".format(length), " -> ", " -> ".join(pool))
    return pool

def get_2x2_block(x, y):
    return [launchpad_grid[y + dy][x + dx] for dy in range(2) for dx in range(2)]

def clear_board(outport):
    for row in launchpad_grid:
        for n in row:
            outport.send(mido.Message('note_on', note=n, velocity=0))

def light_block(outport, block, color):
    vel = COLOR_MAP[color]
    for n in block:
        outport.send(mido.Message('note_on', note=n, velocity=vel))

def flush_midi_input(inport, max_drain_time=0.2):
    try:
        inport._port.ignore_types(sysex=False, timing=False, sensing=False)
    except Exception:
        t0 = time.time()
        while time.time() - t0 < max_drain_time:
            msg = inport.poll()
            if not msg:
                break
            inport.receive()

def setup_blocks():
    all_positions = [(x, y) for x in range(0, 7, 2) for y in range(0, 7, 2)]
    random.shuffle(all_positions)
    return [get_2x2_block(x, y) for x, y in all_positions]

def flash_winner(winner):
    for _ in range(3):
        for row in launchpad_grid:
            for n in row:
                if winner == 1:
                    outport1.send(mido.Message('note_on', note=n, velocity=COLOR_MAP['green']))
                    outport2.send(mido.Message('note_on', note=n, velocity=COLOR_MAP['red']))
                else:
                    outport2.send(mido.Message('note_on', note=n, velocity=COLOR_MAP['green']))
                    outport1.send(mido.Message('note_on', note=n, velocity=COLOR_MAP['red']))
        time.sleep(0.2)
        for row in launchpad_grid:
            for n in row:
                outport1.send(mido.Message('note_on', note=n, velocity=0))
                outport2.send(mido.Message('note_on', note=n, velocity=0))
        time.sleep(0.1)

def run_game(level):
    seq_len = {1: 8, 2: 12, 3: 16}[level]
    sequence = get_unique_sequence(seq_len)
    blocks = setup_blocks()
    show_sequence_on_strip(sequence)

    player_data = [
        {'inport': inport1, 'outport': outport1, 'state': 'PLAY', 'red_end': 0, 'index': 0, 'note_map': {}},
        {'inport': inport2, 'outport': outport2, 'state': 'PLAY', 'red_end': 0, 'index': 0, 'note_map': {}}
    ]

    clear_board(outport1)
    clear_board(outport2)

    for blk, color in zip(blocks[:len(sequence)], sequence):
        light_block(outport1, blk, color)
        light_block(outport2, blk, color)
        for n in blk:
            player_data[0]['note_map'][n] = (blk, color)
            player_data[1]['note_map'][n] = (blk, color)

    while True:
        now = time.time()
        for i, player in enumerate(player_data):
            if player['state'] == 'RED' and now >= player['red_end']:
                clear_board(player['outport'])
                time.sleep(0.05)
                for blk, color in zip(blocks[:len(sequence)], sequence):
                    light_block(player['outport'], blk, color)
                flush_midi_input(player['inport'])
                player['state'] = 'PLAY'
                player['index'] = 0
                player['note_map'] = {n: (blk, color) for blk, color in zip(blocks[:len(sequence)], sequence) for n in blk}

            msg = player['inport'].poll()
            if player['state'] == 'PLAY' and msg and msg.type == 'note_on' and msg.velocity > 0:
                note = msg.note
                if note in player['note_map']:
                    blk, pressed = player['note_map'][note]
                    expected = sequence[player['index']]
                    if pressed == expected:
                        light_block(player['outport'], blk, 'off')
                        for n in blk:
                            player['note_map'].pop(n, None)
                        player['index'] += 1
                        if player['index'] == len(sequence):
                            print(f"\n\U0001F3C6 Player {i + 1} WINS!")
                            flash_winner(i + 1)
                            return
                    else:
                        print(f"\u274C Player {i + 1} WRONG → board RED")
                        for row in launchpad_grid:
                            for n in row:
                                player['outport'].send(mido.Message('note_on', note=n, velocity=COLOR_MAP['red']))
                        flush_midi_input(player['inport'])
                        player['state'] = 'RED'
                        player['red_end'] = now + 1.5

        time.sleep(0.005)

def main():
    print("\nNeoPixel MIDI Simon Game")
    print("Choose Level:")
    print("1. Level 1 (8 colors)")
    print("2. Level 2 (12 colors)")
    print("3. Level 3 (16 colors)")
    choice = input("Enter 1, 2 or 3: ")
    if choice in ['1', '2', '3']:
        run_game(int(choice))
    else:
        print("Invalid choice.")

if _name_ == '_main_':
    signal.signal(signal.SIGINT, lambda sig, frame: (clear_pixels(), sys.exit(0)))
    main()