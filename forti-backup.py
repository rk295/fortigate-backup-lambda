#!/usr/bin/env python

import requests
import boto3
import botocore
import logging
import datetime
import os


logging.basicConfig(
    format='%(asctime)s %(levelname)s %(funcName)s:%(lineno)d %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info("Starting")


# Checks if the specified bucket exists, returns True if it does,
# False if not.
def check_bucket(s3, bucket):

    try:
        s3.meta.client.head_bucket(Bucket=bucket)
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            logging.error("Bucket name {} does not exist".format(bucket))
            return False

    logging.debug("Bucket name={} exists".format(bucket))
    return True


# Takes an s3 object and a bucket object and renames latest.conf
# to be yesterdays date
def rename_old(bucket, file_name):

    # Work out yesterday date and construct a filename.
    # we rename 'latest.conf' to this before replacing
    # with today's config
    y = datetime.datetime.now() - datetime.timedelta(days=1)
    backup_name = "FGVM-{}.conf".format(y.strftime("%Y-%m-%d-%H:%m:%S"))

    logging.info("Renaming latest.conf to {}".format(backup_name))

    copy_source = {
        'Bucket': bucket.name,
        'Key': file_name
    }

    obj = bucket.Object(backup_name)
    try:
        obj.copy(copy_source)
    except botocore.exceptions.ClientError as e:
        logging.error("Failed to copy file in the bucket error={}".format(e.message))
        return False

    logging.info("{} successfully renamed to {}".format(file_name, backup_name))
    return True


# performs a login, follows the provided redirect, then requests the
# config. Returns the config as a string
def get_config(user, password, url):

    forti_login_data="ajax=1&username={}&secretkey={}".format(user, password)

    login_url = "{}/logincheck".format(url)
    login_prompt_url = "{}/ng/prompt?viewOnly&redir=%2Fng%2F".format(url)
    download_config_url = "{}/api/v2/monitor/system/config/backup?destination=file&scope=global".format(url)

    s = requests.Session()
    logging.info("Initialised requests session handling")

    logging.info("Hitting login page")
    login = s.post(url=login_url, data=forti_login_data, verify=False, allow_redirects=False)

    logging.info("login status_code={} response={}".format(login.status_code, login.text))

    login_check = s.get(url=login_prompt_url, verify=False, allow_redirects=False)
    logging.info("login check status_code={}".format(login_check.status_code))

    download_config = s.get(url=download_config_url, verify=False, allow_redirects=False)
    logging.info("download_config status_code={}".format(download_config.status_code))

    return download_config.text


def upload_config(config, bucket, latest_conf_name):

    logging.info("Uploading new config to {}".format(latest_conf_name))
    try:
        bucket.put_object(Body=config, Key=latest_conf_name)
    except botocore.exceptions.ClientError as e:
        logging.error("Failed to upload file named {} error: {}".format(latest_conf_name, e.response))
        return False

    logging.info("Config successfully uploaded")
    return True


def main(event=None, context=None):

    bucket_name = os.getenv("BUCKET_NAME", "")
    forti_username = os.getenv("USERNAME", "admin")
    forti_password = os.getenv("PASSWORD", "")
    forti_hostname = os.getenv("HOST", "")
    forti_port = os.getenv("PORT", "")

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    forti_url = "https://{}:{}".format(forti_hostname, forti_port)
    latest_conf_name = "latest.conf"

    if not check_bucket(s3, bucket_name):
        logging.error("Cannot continue")
        return

    if not rename_old(bucket, latest_conf_name):
        logging.error("Cannot continue")
        return

    config = get_config(forti_username, forti_password, forti_url)

    upload_config(config, bucket, latest_conf_name)

    logging.info("Finished, exiting...")

if __name__ == "__main__":
    main()
