"""Split files into chunks with at least 2 seconds of silence for labeling"""

import argparse
import os
import pydub
from pydub.silence import detect_silence

def split_file(input_dir, output_dir, min_silence_len=2000):
    """Splits an audio file into chunks with at least 2 seconds of silence."""

    # Read in all the audio from the input directory and combine it into one file
    sound = pydub.AudioSegment.empty()
    for file in os.listdir(input_dir):
        sound += pydub.AudioSegment.from_file(os.path.join(input_dir, file))
    
    # Add the start and end points for the audio chunks so the file as at least 25 seconds long
    chunks = []
    chunk_points = [0]

    while chunk_points[-1] < len(sound):
        chunk = chunk_points[-1] + 60000
        # if the last two second of the chunk are not silent, add 2 seconds to the chunk
        # Check if the last two seconds of the chunk are silent
        if sound[chunk - 2000:chunk].dBFS > -40:
            chunk += 2000
        chunk_points.append(chunk - 1000)
    
    # Iterate through the chunk points to create the chunks
    for i in range(1, len(chunk_points)):
        start = chunk_points[i - 1]
        end = chunk_points[i]
        chunk = sound[start:end]
        
        # Skip chunks that contain only silence
        if chunk.dBFS > -40:
            chunk_name = os.path.join(output_dir, "{}_chunk_{}.wav".format(os.path.basename(input_dir), i))
            chunk.export(chunk_name, format="wav")
            chunks.append(chunk_name)
    
    return chunks

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="Path to the audio file to split")
    parser.add_argument("output_dir", help="Output directory for the chunks")
    args = parser.parse_args()

    chunks = split_file(args.file_path, args.output_dir)
    print("Successfully split file into {} chunks.".format(len(chunks)))
