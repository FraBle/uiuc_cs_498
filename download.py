from pyspark import SparkContext
from pyspark.sql import SparkSession
import boto3
import gzip
import os
import math
import shutil

PRODUCT_REVIEWS_DATASET_BUCKET = "amazon-reviews-pds"
PRODUCT_REVIEWS_DATASET_REGION = "us-east-1"

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def download_files(obj):
	s3_resource = boto3.resource('s3')
	dest_filepath = os.path.join('/tmp', obj['Key'].lstrip('tsv/'))
	# s3_resource.Object(PRODUCT_REVIEWS_DATASET_BUCKET, obj['Key']).download_file(dest_filepath)
	return dest_filepath

def ungzip_file(target, dest=None):
	if not dest:
		dest = target.rstrip('.gz')
	with gzip.open(target, 'rb') as f_in:
		with open(dest, 'wb') as f_out:
			shutil.copyfileobj(f_in, f_out)
	return dest

if __name__ == "__main__":
	aws_access_key_id = None
	aws_secret_access_key = None
	download_filenames = None

	if "AWS_ACCESS_KEY_ID" in os.environ:
		aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]

	if "AWS_SECRET_ACCESS_KEY" in os.environ:
		aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]

	if "DOWNLOAD_FILENAMES" in os.environ:
		download_filenames = os.environ["DOWNLOAD_FILENAMES"].split(",")

	if aws_access_key_id and aws_secret_access_key:
		s3 = boto3.client('s3',
			aws_access_key_id=aws_access_key_id,
    		aws_secret_access_key=aws_secret_access_key,
			region_name=PRODUCT_REVIEWS_DATASET_REGION)
	else:
		s3 = boto3.client('s3', 
			region_name=PRODUCT_REVIEWS_DATASET_REGION)

	# list the contents of PRODUCT_REVIEWS_DATASET_BUCKET
	objs = s3.list_objects(Bucket=PRODUCT_REVIEWS_DATASET_BUCKET, Prefix='tsv')['Contents'] 
	for obj in objs:
		print(obj['Key'])
		response = s3.head_object(Bucket=PRODUCT_REVIEWS_DATASET_BUCKET, Key=obj['Key'])
		size = response['ContentLength']
		print(convert_size(size))

	# ignore the multilingual files
	ignore_files = ['tsv/',
					'tsv/amazon_reviews_multilingual_DE_v1_00.tsv.gz',
					'tsv/amazon_reviews_multilingual_FR_v1_00.tsv.gz',
					'tsv/amazon_reviews_multilingual_JP_v1_00.tsv.gz',
					'tsv/amazon_reviews_multilingual_UK_v1_00.tsv.gz']
	objs = [obj for obj in objs if obj['Key'] not in ignore_files]

	if download_filenames:
		new_objs = []
		for dl_file in download_filenames:
			temp_objs = [obj for obj in objs if dl_file in obj['Key']]
			for obj in temp_objs:
				new_objs.append(obj)
		objs = new_objs

	sc = SparkContext()
	distObjs = sc.parallelize(objs)
	downloaded_files = distObjs.map(download_files).collect()
	print(downloaded_files)
	distDownloads = sc.parallelize(downloaded_files)
	downloaded_tsvs = distDownloads.map(ungzip_file).collect()
	print(downloaded_tsvs)

	spark = SparkSession.builder.appName('AmazonImprovedStarRatings').getOrCreate()

	df = spark.read.format("csv").option("header", "true").option("delimiter", "\t").load("/tmp/*.tsv")
	print(df.show(5))
