from pyspark import SparkContext
import boto3
import os
import math

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
	s3_resource.Object(PRODUCT_REVIEWS_DATASET_BUCKET, obj['Key']).download_file(dest_filepath)
	return dest_filepath

if __name__ == "__main__":
	aws_access_key_id = None
	aws_secret_access_key = None

	if "AWS_ACCESS_KEY_ID" in os.environ:
		aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]

	if "AWS_SECRET_ACCESS_KEY" in os.environ:
		aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]

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

	# s3_resource = boto3.resource('s3')
	# s3_resource.Object(PRODUCT_REVIEWS_DATASET_BUCKET, 'tsv/amazon_reviews_us_Video_v1_00.tsv.gz').download_file('/tmp/amazon_reviews_us_Video_v1_00.tsv.gz')
	# tsv/sample_us.tsv

	# ignore the multilingual files
	ignore_files = ['tsv/',
					'tsv/amazon_reviews_multilingual_DE_v1_00.tsv.gz',
					'tsv/amazon_reviews_multilingual_FR_v1_00.tsv.gz',
					'tsv/amazon_reviews_multilingual_JP_v1_00.tsv.gz',
					'tsv/amazon_reviews_multilingual_UK_v1_00.tsv.gz']
	objs = [obj for obj in objs if obj['Key'] not in ignore_files]

	sc = SparkContext()
	# just trying to download the last 3 files to test
	# print(objs[-3:])
	distObjs = sc.parallelize(objs[-3:])
	downloaded_files = distObjs.map(download_files).collect()
	print(downloaded_files)
