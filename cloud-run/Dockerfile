# Base image supports Nvidia CUDA but does not require it and can also run demucs on the CPU
FROM 

# Clone Facebook Demucs
RUN git clone -b main --single-branch https://github.com/facebookresearch/demucs /lib/demucs
WORKDIR /lib/demucs

# Install dependencies
RUN python3 -m pip install -e . --no-cache-dir
# Run once to ensure demucs works and trigger the default model download
RUN ls
RUN python3 -m demucs -d cpu test.mp3 
# Cleanup output - we just used this to download the model
RUN rm -r separated

# Install Flask
RUN python3 -m pip install flask

# Add the Flask app
COPY flask_app.py /lib/demucs

VOLUME /data/input
VOLUME /data/output
VOLUME /data/models

# Run the Flask app
CMD ["python3", "/lib/demucs/flask_app.py"]
