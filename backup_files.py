# Import required python libraries
import os
import time
import datetime
import pipes
import boto3

# Path to store the backup files
BACKUP_PATH = '/home/joel/backup/backups'

# Set your config file witch contains the folders to backup
CONFIG_FILE = "/home/joel/backup/scripts/files.conf"

# S3 upload settings
# Uploading your fresh made backups to the S3 cloud, enable the below options
use_aws_s3_upload = True
aws_access_key_id = '<your_key>'
aws_secret_access_key = '<your_secret_key>'
aws_bucket = '<your_bucket_name>'
aws_regio = 'eu-west-1'

if use_aws_s3_upload:
    s3client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Getting current DateTime to create the separate backup folder like "20180817-123433".
DATETIME = time.strftime('%Y%m%d-%H%M%S')
TODAYBACKUPPATH = BACKUP_PATH + '/' + DATETIME
FOLDER_NAME = time.strftime('%Y/%m/%d/')

# Checking if backup folder already exists or not. If not exists will create it.
try:
    os.stat(TODAYBACKUPPATH)
except:
    os.mkdir(TODAYBACKUPPATH)

if not os.path.exists(CONFIG_FILE):
    print("Config file not found!")

else:
    in_file = open(CONFIG_FILE, "r")
    flength = len(in_file.readlines())
    in_file.close()
    p = 1
    folder_file = open(CONFIG_FILE, "r")

    while p <= flength:
        folder = folder_file.readline()   # reading database name from file
        folder = folder[:-1]  # deletes extra line
        gzipcmd = "tar -czf " + pipes.quote(TODAYBACKUPPATH) + "/" + folder.replace('/', '_') + ".tar.gz " + folder
        os.system(gzipcmd)
        p = p + 1

        # Now uploading backup files to your S3 Bucket
        if use_aws_s3_upload:
            print("Uploading to your S3 bucket...")
            s3client.upload_file(pipes.quote(TODAYBACKUPPATH) + "/" + folder.replace('/', '_') + ".tar.gz", aws_bucket, FOLDER_NAME + folder.replace('/', '_') + ".tar.gz")

    folder_file.close()
