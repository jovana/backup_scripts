# Import required python libraries
from configparser import ConfigParser
import os
import time
import datetime
import pipes

# Loading the configuration
cfg = ConfigParser()
cfg.read('config.ini')


# DOT NOT EDIT BELOW THIS LINE
# =============================

def running_database_backup(p_DatabaseName, p_BackupPath):
    """Function to run the database backup

    Arguments:
        p_DatabaseName {[String]} -- [description]
        p_BackupPath {[String]} -- [description]

    Returns:
        [Boolean] -- [Return always True to if this function has fineshed.]
    """
    FOLDER_NAME = time.strftime('%Y/%m/%d/')
    dumpcmd = "mysqldump -h " + cfg.get('DB', 'db_host') + " -u " + cfg.get('DB', 'db_user') + " -p" + cfg.get('DB',
                                                                                                               'db_user_password') + " " + p_DatabaseName + " > " + pipes.quote(p_BackupPath) + "/" + p_DatabaseName + ".sql"
    os.system(dumpcmd)
    gzipcmd = "gzip " + pipes.quote(p_BackupPath) + "/" + p_DatabaseName + ".sql"
    os.system(gzipcmd)

    # Now uploading backup files to your S3 Bucket
    if cfg.get('APP', 'aws_s3_upload'):
        import boto3
        print(f"Uploading database backup {p_DatabaseName} to your S3 bucket...")
        s3client.upload_file(pipes.quote(p_BackupPath) + "/" + p_DatabaseName + ".sql.gz", cfg.get('AWS', 'aws_bucket'), FOLDER_NAME + db + ".sql.gz")

    return True


# Set the database name / config path
DB_NAME = cfg.get('DB', 'db_name')

# check if AWS S3 has been activated.
if cfg.get('APP', 'aws_s3_upload'):
    s3client = boto3.client('s3', aws_access_key_id=cfg.get('AWS', 'aws_access_key_id'),
                            aws_secret_access_key=cfg.get('AWS', 'aws_secret_access_key'))

# Getting current DateTime to create the separate backup folder like "20190817-123433"
DATETIME = time.strftime('%Y%m%d-%H%M%S')
TODAYBACKUPPATH = cfg.get('APP', 'backup_path') + '/' + DATETIME

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
        db = db[:-1]  # deletes extra line

        print(f"Saving database contents from database {db}...")
        running_database_backup(db, TODAYBACKUPPATH)
        p = p + 1

    dbfile.close()
else:
    print(f"Saving database contents from database {DB_NAME}...")
    running_database_backup(DB_NAME, TODAYBACKUPPATH)

print("")
print("Database backup completed!")

# Cleanup backup files (only if S3 cloud upload has enabled)
if cfg.get('APP', 'aws_s3_upload'):
    print(f'All backup files has saved in your bucket: {cfg.get("AWS","aws_bucket")} on AWS S3.')
    print('Cleaning up temporaly backup files...')
    os.system("rm -rf " + TODAYBACKUPPATH)
    print('Done!')
