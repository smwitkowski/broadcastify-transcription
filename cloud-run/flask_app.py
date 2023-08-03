from flask import Flask, request
import os
import subprocess

app = Flask(__name__)

@app.route('/run_demucs', methods=['POST'])
def run_demucs():
    # check if the post request has the file part
    if 'file' not in request.files:
        return 'No file part in the request', 400
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return 'No selected file', 400
    if file:
        # Save the file to /data/input directory
        file.save(os.path.join('/data/input', file.filename))

        # Then, call the command with the filename
        cmd = ["python3", "-m", "demucs", "-n", "htdemucs", "--out", "/data/output", "--mp3", "--two-stems", f"/data/input/{file.filename}"]
        subprocess.run(cmd)

        # Clean up the input file
        os.remove(os.path.join('/data/input', file.filename))

    return "Demucs run completed"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
