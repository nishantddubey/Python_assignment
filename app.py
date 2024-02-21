from flask import Flask, render_template, request, redirect, url_for
import boto3
import os

app = Flask(__name__)

# Configure AWS credentials
AWS_ACCESS_KEY_ID = 'AKIAQT5APJTNRFRAYNT3'
AWS_SECRET_ACCESS_KEY = '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'
AWS_REGION = 'ap-south-1'

# Create an S3 client
s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  region_name=AWS_REGION)

# Define bucket name
BUCKET_NAME = 's3access-file'


@app.route('/')
def index():
    # List contents of the S3 bucket
    response = s3.list_objects(Bucket=BUCKET_NAME)
    files = []
    folders = {}
    if 'Contents' in response:
        for obj in response['Contents']:
            if obj['Key'].endswith('/'):
                folder_name = obj['Key']
                folders[folder_name] = []
            else:
                file_name = obj['Key']
                folder_name = '/'.join(file_name.split('/')[:-1])
                folders[folder_name].append(file_name)
                files.append(file_name)  # Collect all file names
    return render_template('index.html', folders=folders, files=files)


@app.route('/create-folder', methods=['POST'])
def create_folder():
    folder_name = request.form['folder-name']
    if folder_name:
        # Create folder in S3 bucket
        s3.put_object(Bucket=BUCKET_NAME, Key=(folder_name + '/'))
    return redirect(url_for('index'))


@app.route('/delete-folder', methods=['POST'])
def delete_folder():
    folder_name = request.form['folder-name']
    if folder_name:
        # Delete folder and its contents from S3 bucket
        s3.delete_object(Bucket=BUCKET_NAME, Key=(folder_name))
    return redirect(url_for('index'))


@app.route('/delete-file', methods=['POST'])
def delete_file():
    file_name = request.form['file-name']
    if file_name:
        # Delete file from S3 bucket
        s3.delete_object(Bucket=BUCKET_NAME, Key=file_name)
    return redirect(url_for('index'))


@app.route('/upload-file', methods=['POST'])
def upload_file():
    file = request.files['file']
    folder = request.form['folder']
    if file:
        # Upload file to S3 bucket in the selected folder
        s3.upload_fileobj(file, BUCKET_NAME, folder + '/' + file.filename)
    return redirect(url_for('index'))


@app.route('/copy-file', methods=['POST'])
def copy_file():
    source_file = request.form['source-file']
    destination_folder = request.form['destination-folder']
    if source_file and destination_folder:
        # Copy file within S3 bucket
        s3.copy_object(Bucket=BUCKET_NAME, CopySource=f"{BUCKET_NAME}/{source_file}", Key=(destination_folder + '/' + os.path.basename(source_file)))
    return redirect(url_for('index'))


@app.route('/move-file', methods=['POST'])
def move_file():
    source_file = request.form['source-file']
    destination_folder = request.form['destination-folder']
    if source_file and destination_folder:
        # Move file within S3 bucket (copy then delete)
        s3.copy_object(Bucket=BUCKET_NAME, CopySource=f"{BUCKET_NAME}/{source_file}", Key=(destination_folder + '/' + os.path.basename(source_file)))
        s3.delete_object(Bucket=BUCKET_NAME, Key=source_file)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
