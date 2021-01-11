#!/usr/bin/env python

import os
import os.path
import glob
import re
import plac
from pathlib import Path
from PIL import Image
from midiutil import MIDIFile

FRAMES_PER_SECOND = 12
FRAMES_PER_BEAT   = 9
DEFAULT_OUTPUT_FILENAME = "output.mid"


class ImageStats:
    
    def __init__(self, image):
        self.image = image.convert("RGB")
        self.size = self.image.width * self.image.height
        
        greyscale = image.convert("L")
        channels = self.image.split()
        greyscale_histogram = greyscale.histogram()
        self.brightness = self._calculate_brightness(greyscale_histogram)
        self.contrast = self._calculate_contrast(greyscale_histogram)
        self.saturation = self._calculate_saturation()
        self.colour_proportion = self._calculate_colour_proportions(channels)

    def _calculate_brightness(self, histogram):
        brightness = sum([p * i / 255 for i, p in enumerate(histogram)]) / self.size
        return brightness

    def _calculate_contrast(self, histogram):
        contrast = sum([p * abs(i - 127.5) / 127.5 for i, p in enumerate(histogram)]) / self.size
        return contrast

    def _calculate_saturation(self):
        # TODO: Not sure how to do this.
        return 0

    def _calculate_colour_proportions(self, channels):
        intensities = [self._calculate_brightness(c.histogram()) for c in channels]
        return [i / sum(intensities) for i in intensities]


def note_to_pitch(note):
    # C4 is Middle C.
    note_offsets = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    match = re.search(r"([a-gA-G])([#b]?)(\d+)", note)
    note_name, accidental, octave = match[1], match[2], int(match[3])
    offset = 12 + 12 * octave
    offset += note_offsets.index(note_name)
    if accidental == "#":
        offset += 1
    if accidental == "b":
        offset -= 1
    return offset


def load_image(filename):
    print(f"Processing {filename}")
    return Image.open(filename)


def add_note(midi_file, beat, note, duration=1, volume=100):
    midi_file.addNote(0, 0, note_to_pitch(note), beat, duration, volume)


def generate_notes(midi_file, frame_number, beat, image_data):
    # TODO: Remove debugging prints
    print("Frame", frame_number)
    print("Beat", beat)
    print("Brightness", image_data.brightness)
    print("Contrast", image_data.contrast)
    print("Saturation", image_data.saturation)
    print("Colour Ratio", image_data.colour_proportion)
    # TODO: Remove testing melody
    tune = ["C4", "G4", "F4", "B3"]
    note = tune[frame_number % len(tune)]
    add_note(midi_file, frame_number, note)
    # TODO: Use the time and image data to generate some sweet tunes


def generate(dir_path, frames_per_second, frames_per_beat, output_filename):
    dir_pattern = os.path.join(dir_path, "*")
    print(f"Searching through {dir_pattern}.")
    midi_file = MIDIFile(1)
    bpm = (frames_per_second / frames_per_beat) * 60
    print(f"BPM of {bpm}.")
    midi_file.addTempo(0, 0, bpm)
    for frame, image in enumerate( (load_image(path) for path in glob.glob(dir_pattern)) ):
        beat = frame / frames_per_beat
        image_data = ImageStats(image)
        generate_notes(midi_file, frame, beat, image_data)
    with open(output_filename, 'wb') as output_file:
        midi_file.writeFile(output_file)


def main(dir_path:          ("", "option", "dir", Path) = os.getcwd(), 
         frames_per_second: ("", "option", "fps", int)  = FRAMES_PER_SECOND, 
         frames_per_beat:   ("", "option", "fpb", int)  = FRAMES_PER_BEAT, 
         output_filename:   ("", "option", "o", Path)   = DEFAULT_OUTPUT_FILENAME):
    # TODO: <Remove>
    dir_path = "examples/test1"
    # </Remove>
    generate(dir_path, frames_per_second, frames_per_beat, output_filename)
    

if __name__ == "__main__":    
    plac.call(main)
