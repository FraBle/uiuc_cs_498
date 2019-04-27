# CS 498 CCA: Project Team 40
> Improving Amazon Star Ratings through Text Analysis on Review Content

## Download Data Sets
1. Install Spark on your local machine, e.g. `brew install apache-spark` for MacOS
1. Install Python 3, e.g. `brew install python` for MacOS
1. Install the Python dependencies: `pip install boto3 click click_pathlib pyspark`
1. Run the Data Set Downloader: `python data_set_downloader.py`

### Usage and Options
```
Usage: data_set_downloader.py [OPTIONS]

  Utility to download Amazon Product Reviews data set.

Options:
  -a, --aws-access-key-id TEXT    AWS Access Key ID
  -s, --aws-secret-access-key TEXT
                                  AWS Secret Access Key
  -r, --aws-data-set-region TEXT  AWS Data Set Region
  -b, --aws-data-set-bucket TEXT  AWS Data Set S3 Bucket
  -f, --file-names TEXT           Data Set File Filter
  -d, --file-destination PATH     Data Set File Destination
  --debug                         Print additional information
  --help                          Show this message and exit.
```

### Default Values
| Option                | Value                |
|-----------------------|----------------------|
| `aws-data-set-region` | `us-east-1`          |
| `aws-data-set-bucket` | `amazon-reviews-pds` |
| `file-destination`    | `./datasets`         |

### Example Usage
Run with file name filter, custom file destination and debug info activated:
```
python data_set_downloader.py --file-names tsv/amazon_reviews_us_Watches_v1_00.tsv.gz --file-names tsv/amazon_reviews_us_Home_Entertainment_v1_00.tsv.gz -d .target --debug
```

## Statistics
A preliminary example of the process we intend to implement in a distributed computing process is shown in `Amazon Watches Reviews EDA.ipynb`.  
This Juptyer notebook demonstates how the Amazon Reviews can be divided into several tiers and how a training data set and model can be used to predict the tier that the product should belong using certain aggregate features.
