# midi code
import mido
import random
import time

# === MIDI SETUP ===
inport = mido.open_input("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 28:0")#listen for button presses
outport = mido.open_output("Launchpad Pro MK3:Launchpad Pro MK3 LPProMK3 MIDI 28:0")# Sends commands to light up pad

# === COLORS ===
COLOR_MAP = {
    'red': 5,
    'green': 21,
    'blue': 78,
    'yellow': 13,
    'off': 0,
    'flash': 5  # flash color for wrong
}

# === GRID SETUP ===
launchpad_grid = [[81 - 10 * r + c for c in range(8)] for r in range(8)]
#reduce by 10 going down , Goes up by 1 going to the right .Layout Starts 11 and ends 88.

# === HELPERS ===
def get_2x2_block(x, y):#returns 4 midi note numbers to form a 2x2 button starting at (x,y)
    return [launchpad_grid[y + dy][x + dx] for dy in range(2) for dx in range(2)]

def clear():#Turns all the pads off by sending velocity=0 to all notes.
    for row in launchpad_grid:
        for note in row:
            outport.send(mido.Message('note_on', note=note, velocity=0))

def light_block(block, color):#lights up notes in the block with colour
    for note in block:
        outport.send(mido.Message('note_on', note=note, velocity=COLOR_MAP[color]))

def flash_red():#when press wrong colour in sequence, flash red
    for row in launchpad_grid:
        for note in row:
            outport.send(mido.Message('note_on', note=note, velocity=COLOR_MAP['flash']))
    time.sleep(0.5)
    clear()

# === GAME BLOCK SETUP ===
def setup_game_blocks():# randomly generate the 2x2 blocks positions on the 8x8 grid
    all_positions = [(x, y) for x in range(0, 7, 2) for y in range(0, 7, 2)]
    random.shuffle(all_positions)
    color_blocks = {'red': [], 'green': [], 'blue': [], 'yellow': []}  #creates a list of 16 colours 4 of Red,Green,Blue and Yellow
    colors = ['red'] * 4 + ['green'] * 4 + ['blue'] * 4 + ['yellow'] * 4
    random.shuffle(colors)
    for color, (x, y) in zip(colors, all_positions):
        block = get_2x2_block(x, y)    #assign each 2x2 block a colour and returns w coloir keys and list of blocks as values
        color_blocks[color].append(block)
    return color_blocks

# === MAIN GAME LOOP ===

def run_game():
    while True:
        clear()
        blocks = setup_game_blocks()
        light_blocks(blocks)

        # Create a sequence with exactly 4 of each color, shuffled randomly
        colors = ['red'] * 4 + ['green'] * 4 + ['blue'] * 4 + ['yellow'] * 4
        random.shuffle(colors)
        color_sequence = colors

        print("\nPress in this order:", " -> ".join(color_sequence))
        sequence_index = 0#tracks where the player is in the sequence
        note_to_block = {}#track the note to its block and colour

        # map each note to its block and color
        for color, block_list in blocks.items():
            for block in block_list:
                for note in block:
                    note_to_block[note] = (block, color)

        while sequence_index < len(color_sequence):#wait for pad press
            msg = inport.receive()
            if msg.type == 'note_on' and msg.velocity > 0:#when pressed
                note = msg.note
                if note in note_to_block:#check if it matches the expected colour in the sequence
                    block, color = note_to_block[note]
                    expected_color = color_sequence[sequence_index]
                    if color == expected_color:# if matches the sequence, turn off that block
                        light_block(block, 'off')
                        # remove this block from pool to avoid double use
                        for n in block:
                            note_to_block.pop(n, None)
                        sequence_index += 1
                    else: # if incoprrect flashes red
                        print("Wrong color! Restarting sequence...")
                        flash_red()
                        break  # restart the game loop
        else:# when the sequenceis complete
            print("✅ Sequence complete! Restarting...")
            time.sleep(1)

def light_blocks(blocks):
    for color, block_list in blocks.items():
        for block in block_list:
            light_block(block, color)

# === START ===
if __name__ == "__main__":
    run_game()

