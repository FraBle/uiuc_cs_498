# uiuc_cs_498
CS 498 Project: Improving Amazon Star Ratings through Text Analysis on Review Content

## Running the Application
PySpark is required to run spark_main.py.  The python context must also contain the required packages to be avaliable to PySpark to run the spark job via spark-submit.  Some environment variables can be provided to override the default settings.  By default the script will use the machine's default AWS credentials and download all files from the Amazon Customer Reviews Dataset.

 AWS_ACCESS_KEY_ID=**** AWS_SECRET_ACCESS_KEY=**** DOWNLOAD_FILENAMES=amazon_reviews_us_Watches_v1_00.tsv.gz spark-submit spark_main.py

## Statistics
A preliminary example of the process we intend to implement in a distributed computing process is shown in Amazon Watches Reviews EDA.ipynb.  This Juptyer notebook demonstates how the Amazon reviews can be divided into several tiers and how a training dataset and model can be used to predict the tier that the product should belong using some aggregate features.