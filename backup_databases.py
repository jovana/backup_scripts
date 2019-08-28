# Import required python libraries
import os
import time
import datetime
import pipes
import boto3

# Path to store the backup files
BACKUP_PATH = '/home/backup/backups'

# MySQL database details to which backup to be done.
# Make sure below user having enough privileges to take databases backup.
DB_HOST = 'localhost'
DB_USER = 'backup_user'
DB_USER_PASSWORD = 'SuperStrongPassword'

# To take multiple databases backup, create any file like databases.conf and put databases names
# one on each line and assigned to DB_NAME variable
DB_NAME = '/home/backup/scripts/databases.conf'

# To take only a backup from one database, use the below line
#DB_NAME = 'db_name_to_backup'

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

# Code for checking if you want to take single database backup or assinged multiple backups in DB_NAME.
print("checking for databases names file.")
if os.path.exists(DB_NAME):
    file1 = open(DB_NAME)
    multi = 1
    print("Databases file found...")
    print("Starting backup of all dbs listed in file " + DB_NAME)
else:
    print("Databases file not found...")
    print("Starting backup of database " + DB_NAME)
    multi = 0

# Starting actual database backup process.
if multi:
    in_file = open(DB_NAME, "r")
    flength = len(in_file.readlines())
    in_file.close()
    p = 1
    dbfile = open(DB_NAME, "r")

    while p <= flength:
        db = dbfile.readline()   # reading database name from file
        db = db[:-1]         # deletes extra line
        dumpcmd = "mysqldump -h " + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " > " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
        os.system(dumpcmd)
        gzipcmd = "gzip " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
        os.system(gzipcmd)
        p = p + 1

        # Now uploading backup files to your S3 Bucket
        if use_aws_s3_upload:
            print("Uploading to your S3 bucket...")
            s3client.upload_file(pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql.gz", aws_bucket, FOLDER_NAME + db + ".sql.gz")

    dbfile.close()
else:
    db = DB_NAME
    dumpcmd = "mysqldump -h " + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " > " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
    print("Dumping database contents...")
    os.system(dumpcmd)
    gzipcmd = "gzip " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
    os.system(gzipcmd)

    # Now uploading backup files to your S3 Bucket
    if use_aws_s3_upload:
        print("Uploading to your S3 bucket...")
        s3client.upload_file(pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql.gz", aws_bucket, FOLDER_NAME + db + ".sql.gz")

print("")
print("Backup script completed")

# Cleanup backup files (only if cloud upload has enabled)
if use_aws_s3_upload:
    os.system("rm -rf " + TODAYBACKUPPATH)
