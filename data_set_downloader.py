import gzip
import os
import math
import re
import shutil
import sys
from pathlib import Path
from pprint import pprint

try:
    import boto3
    import click
    import click_pathlib
    from pyspark import SparkContext
    from pyspark.sql import SparkSession
except ImportError:
    sys.exit("Please install dependencies: pip install boto3 click click_pathlib pyspark")


DEFAULT_PRODUCT_REVIEWS_DATASET_BUCKET = "amazon-reviews-pds"
DEFAULT_PRODUCT_REVIEWS_DATASET_REGION = "us-east-1"
DEFAULT_FILE_DESTINATION = Path('.') / '.datasets'
FILE_PATTERN = re.compile(r"tsv/amazon_reviews_us\w*\.tsv\.gz")

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def download_files(file, bucket, folder):
    s3_resource = boto3.resource('s3')
    path = folder / file['Key'].lstrip('tsv/')
    s3_resource.Object(bucket, file['Key']).download_file(str(path))
    return path

def ungzip_file(source):
    destination = source.with_suffix('')
    with gzip.open(source, 'rb') as f_in, open(destination, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    return destination

@click.command()
@click.option('--aws-access-key-id', '-a', help='AWS Access Key ID')
@click.option('--aws-secret-access-key', '-s', help='AWS Secret Access Key')
@click.option('--aws-data-set-region', '-r', help='AWS Data Set Region', default=DEFAULT_PRODUCT_REVIEWS_DATASET_REGION)
@click.option('--aws-data-set-bucket', '-b', help='AWS Data Set S3 Bucket', default=DEFAULT_PRODUCT_REVIEWS_DATASET_BUCKET)
@click.option('--file-names', '-f', multiple=True, help='Data Set File Filter')
@click.option('--file-destination', '-d', help='Data Set File Destination', default=DEFAULT_FILE_DESTINATION, type=click_pathlib.Path(exists=True))
@click.option('--debug', is_flag=True, help='Print additional information')
def download(aws_access_key_id, aws_secret_access_key, aws_data_set_region, aws_data_set_bucket, file_names, file_destination, debug):
    """Utility to download Amazon Product Reviews data set."""
    s3 = boto3.client('s3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_data_set_region)

    files = s3.list_objects(Bucket=aws_data_set_bucket, Prefix='tsv')['Contents']
    if debug:
        # list the contents of DEFAULT_PRODUCT_REVIEWS_DATASET_BUCKET
        print(f"Content of S3 bucket {aws_data_set_bucket}:")
        pprint([
            (file['Key'], convert_size(s3.head_object(Bucket=aws_data_set_bucket, Key=file['Key'])['ContentLength']))
            for file in files
        ])

    # ignore the multilingual files
    files = filter(lambda file: FILE_PATTERN.match(file['Key']), files)

    # apply provided filename filter
    files = [file for file in files if file['Key'] in file_names]

    if debug:
        print(f"\nFiltered file list for S3 bucket {aws_data_set_bucket}:")
        pprint([file['Key'] for file in files])

    context = SparkContext()
    distributed_dataset = context.parallelize(files)
    archives = distributed_dataset.map(lambda f: download_files(f, aws_data_set_bucket, file_destination)).collect()
    if debug:
        print(f"\nDownloaded archives:")
        pprint(archives)

    distributed_unpacked_dataset = context.parallelize(archives)
    downloaded_files = distributed_unpacked_dataset.map(ungzip_file).collect()
    if debug:
        print(f"\nDownloaded TSV files:")
        pprint(downloaded_files)

    if debug:
        spark = SparkSession.builder.appName('AmazonImprovedStarRatings').getOrCreate()
        path = file_destination / '*.tsv'
        df = spark.read.format("csv").option("header", "true").option("delimiter", "\t").load(str(path))
        print(df.show(5))

if __name__ == '__main__':
    download()
