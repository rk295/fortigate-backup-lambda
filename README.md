fortigate-backup lambda
=======================

This code connects to a fortigate instance and downloads the backup. The backup is then stored in s3 as `latest.conf`. Before uploading to s3 the previous `latest.conf` is renamed to a dated file, eg: `FGVM-2017-12-07-12:12:23.conf`.

Permissions to write to the bucket must be provided for via IAM Roles. By design, the script has no concept of access keys.

Running
-------

The lambda was intended to by triggered by a CloudWatch Alarm, for example nightly.

Configuration
-------------

The function is configured only through the environment variables listed below:

* `BUCKET_NAME` - The name of the bucket to write too.
* `USERNAME` - The username to connect to the VPN as.
* `PASSWORD` - The password to connect to the VPN with.
* `HOST` - The VPN hostname.
* `PORT` - The port of the admin interface of the VPN server.

Maturity
--------

The code is tested, and in product use. However you must consider the code to be relatively imature. It has little or no error checking, especially around checking for the required environment variables.

Also, what should it do if the backup fails for some reason? The question was never answered, so care should be taken to ensure it is producing backup files.