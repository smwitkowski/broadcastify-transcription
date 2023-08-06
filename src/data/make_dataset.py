from google.cloud import storage
import json
import os
import click

def convert_to_rttm_and_uem(data, filename, file_length):
    rttm_output = ""
    uem_output = f"{filename} NA 0 {file_length} \n" # Assuming the audio length is 61s for each file
    for result in data["result"]:
        start_time = result["value"]["start"]
        duration = result["value"]["end"] - start_time
        speaker = result["value"]["labels"][0].split(" ")[-1]
        channel = result["value"]["channel"]
        rttm_line = f"SPEAKER {filename} 1 {start_time:.2f} {duration:.2f} <NA> <NA> {speaker} <NA> <NA>\n"
        rttm_output += rttm_line
    return rttm_output, uem_output


def download_audio_file(bucket, audio_path):
    audio_directory = 'data/audio'
    blob = bucket.blob(audio_path.replace('gs://', '').split('/', 1)[1])
    local_path = os.path.join(audio_directory, os.path.basename(audio_path))
    blob.download_to_filename(local_path)
    return os.path.basename(audio_path)

@click.command()
@click.argument('project_id', type=click.STRING, default='personal-project-space-353201')
@click.argument('bucket_name', type=click.STRING, default='purple-label-studio-data')
@click.argument('prefix', type=click.STRING, default='broadcastify/output/')
@click.argument('output_directory', type=click.STRING, default='data')
def main(project_id, bucket_name, prefix, output_directory):

    uems_directory = os.path.join(output_directory, 'uems')
    rttms_directory = os.path.join(output_directory, 'rttms')
    lists_directory = os.path.join(output_directory, 'lists')
    audio_directory = os.path.join(output_directory, 'audio')

    for dir_path in [uems_directory, rttms_directory, lists_directory, audio_directory]:
        if not os.path.exists(dir_path):
            os.mkdirs(dir_path, exist_ok=True)

    # Initialize the GCS client
    client = storage.Client(project=project_id)
    bucket = client.get_bucket(bucket_name)

    # Initialize the output strings
    uem_outputs = {"train": "", "test": "", "development": ""}
    rttm_outputs = {"train": "", "test": "", "development": ""}
    filenames_lists = {"train": [], "test": [], "development": []}

    # Collect blob contents
    uem_contents = []
    blob_contents = []
    file_names = []
    blobs = bucket.list_blobs(prefix=prefix)
    for blob in blobs:
        if blob.name != prefix:  # Skip the directory itself
            print(f"Processing {blob.name}...")
            blob_content = blob.download_as_text()
            data = json.loads(blob_content)
            filename = os.path.basename(data['task']['data']['audio'])
            file_length = data['result'][0]['original_length']
            rttm_output, uem_output = convert_to_rttm_and_uem(data, filename, file_length)
            with open(os.path.join(rttms_directory, f"{filename}.rttm"), 'w') as file:
                file.write(rttm_output)

            with open(os.path.join(uems_directory, f"{filename}.uem"), 'w') as file:
                file.write(uem_output)
            # Download the original audio file
            downloaded_filename = download_audio_file(bucket, data['task']['data']['audio'])
            file_names.append(downloaded_filename)
            blob_contents.append(blob_content)

    # Shuffle and split the contents
    train_size = int(0.8 * len(blob_contents))
    test_size = int(0.1 * len(blob_contents))

    filenames_lists["train"] = file_names[:train_size]
    filenames_lists["test"] = file_names[train_size:train_size + test_size]
    filenames_lists["development"] = file_names[train_size + test_size:]

    # Write the RTTM content and filenames to files
    for split in ['train', 'test', 'development']:
        with open(os.path.join(lists_directory, f'{split}.lst'), 'w') as file:
            file.write("\n".join(filenames_lists[split]))

if __name__ == '__main__':
    main()
