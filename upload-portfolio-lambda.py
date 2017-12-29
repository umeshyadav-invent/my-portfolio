import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    # TODO implement
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:533035462457:deployBigTrainBuild')

    try:
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

        portfolio_bucket = s3.Bucket('bigtrain.dmf-nonprod.collegeboard.org')
        build_bucket = s3.Bucket('bigtrainbuild.dmf-nonprod.collegeboard.org')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('bigtrainbuild.zip',portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm,
                    ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print "Job Done!!"
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio Deployed Successfully!!")

    except:
        topic.publish(Subject="Portfolio Deployed Failed", Message="Portfolio was not deployed successfully!!")
        raise

    return 'Hello from Lambda'


#### Without Lambda Code
# import boto3
# from botocore.client import Config
# import StringIO
# import zipfile
# import mimetypes
#
# s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
#
# portfolio_bucket = s3.Bucket('bigtrain.dmf-nonprod.collegeboard.org')
# build_bucket = s3.Bucket('bigtrainbuild.dmf-nonprod.collegeboard.org')
#
# portfolio_zip = StringIO.StringIO()
# build_bucket.download_fileobj('bigtrainbuild.zip',portfolio_zip)
#
# with zipfile.ZipFile(portfolio_zip) as myzip:
#     for nm in myzip.namelist():
#         obj = myzip.open(nm)
#         portfolio_bucket.upload_fileobj(obj,nm,
#             ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
#         portfolio_bucket.Object(nm).Acl().put(ACL='public-read')


### If you have to download the file on the server and unzip because of memory limitiation
# import boto3
# from botocore.client import Config
# import zipfile
#
# s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
#
# build_bucket = s3.Bucket('portfoliobuild.robinnorwood.info')
# portfolio_bucket = s3.Bucket('portfolio.robinnorwood.info')
#
# # On Windows, this will need to be a different location than /tmp
# build_bucket.download_file('portfolio.zip', '/tmp/portfolio.zip')
#
# with zipfile.ZipFile('/tmp/portfolio.zip') as myzip:
#     for nm in myzip.namelist():
#         obj = myzip.open(nm)
#         target_bucket.upload_fileobj(obj, nm)
#         target_bucket.Object(nm).Acl().put(ACL='public-read')
