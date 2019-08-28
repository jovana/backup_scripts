# Automate your backups

This script is desinged for working on Linux Ubuntu to backup your important databases. Using a cronjob to run this when needed.

## Requirments
- Python 3.7
- If you want to upload your backup files to the AWS S3 cloud, install boto3
```
pip3 install boto3
```

### Setup a dedicated user for MySQL / MariaDB
To make sure you have a user witch can access the database's you need to backup create a new user.
Start the mysql cli

```mysql```

Create the user:
```CREATE USER 'backup_user'@'localhost' IDENTIFIED BY 'YourSuperStrongPassword';```

Set the correct permissions (if this script run on the same server, use localhost, otherwise use the host / ip from the remote system):
```
GRANT ALL PRIVILEGES ON *.* TO 'backup_user'@'localhost';
flush PRIVILEGES;
```

Check if this user has the correct permissions:
```show grants for 'backup_user'@'localhost';```

### Setup the backup script parameters
Enter the correct details on top of this script:
Your server host:
```DB_HOST = 'localhost'```

Your database username:
```DB_USER = 'backup_user'```

Your database password:
```DB_USER_PASSWORD = 'SuperStrongPassword'```

where to store the backup files:
```BACKUP_PATH = '/home/backup/backups'```

If you like to use the AWS S3 upload, make sure set the below line to True. If you don't want to use this enter False (using the capitals):
```use_aws_s3_upload = True```

Als enter your AWS KEY and Securt key and region:
```
aws_access_key_id = '<your_key>'
aws_secret_access_key = '<your_secret_key>'
aws_bucket = '<your_bucket_name>'
```

### Setup the CrobJob
Start your crontab editor:
```crontab -e```

Enter this line to run this script every day at 3am:
```0 3 * * * /etc/python3 /home/backup/scripts/backup_databases.py```

To found out where the file python3 can be found on your system simple run the below command:
```whereis python3```

