#### The Code to integrate with CodePipeline because it uses its own S3 Bucket
import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    # TODO implement
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:533035462457:portfolioSNSTopic')

    # Set the Default Value,
    # so that if the Lambda is not executed by CodePiipleine
    location = {
        "bucketName" : 'portfoliobuild.dmf-nonprod.collegeboard.org',
        "objectKey" : 'portfoliobuild.zip'
    }

    try:

        # Get the Codepipeline Job
        job = event.get("CodePipeline.job")

        # Iterate thru the Artifacts
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]

        print "Building portfolio from " + str(location)

        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

        portfolio_bucket = s3.Bucket('portfolio.dmf-nonprod.collegeboard.org')
        build_bucket = s3.Bucket(location["bucketName"])

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj(location["objectKey"],portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm,
                    ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print "Job Done!!"
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio Deployed Successfully!!")

        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])

    except:
        topic.publish(Subject="Portfolio Deployed Failed", Message="Portfolio was not deployed successfully!!")
        raise

    return 'Hello from Lambda'



# ###################################################################
# ###### Without CodePipeline Integration #####
# import boto3
# from botocore.client import Config
# import StringIO
# import zipfile
# import mimetypes
#
# def lambda_handler(event, context):
#     #TODO implement
#     sns = boto3.resource('sns')
#     topic = sns.Topic('arn:aws:sns:us-east-1:533035462457:deployBigTrainBuild')
#
#     try:
#         s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
#
#         portfolio_bucket = s3.Bucket('portfolio.dmf-nonprod.collegeboard.org')
#         build_bucket = s3.Bucket('portfoliobuild.dmf-nonprod.collegeboard.org')
#
#         portfolio_zip = StringIO.StringIO()
#         build_bucket.download_fileobj('portfoliobuild.zip',portfolio_zip)
#
#         with zipfile.ZipFile(portfolio_zip) as myzip:
#             for nm in myzip.namelist():
#                 obj = myzip.open(nm)
#                 portfolio_bucket.upload_fileobj(obj,nm,
#                     ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
#                 portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
#
#         print "Job Done!!"
#         topic.publish(Subject="Portfolio Deployed", Message="Portfolio Deployed Successfully!!")
#
#     except:
#         topic.publish(Subject="Portfolio Deployed Failed", Message="Portfolio was not deployed successfully!!")
#         raise
#
#     return 'Hello from Lambda'




###################################################################

#### Without Lambda Code #######################################
# import boto3
# from botocore.client import Config
# import StringIO
# import zipfile
# import mimetypes
#
# s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
#
# portfolio_bucket = s3.Bucket('portfolio.dmf-nonprod.collegeboard.org')
# build_bucket = s3.Bucket('portfoliobuild.dmf-nonprod.collegeboard.org')
#
# portfolio_zip = StringIO.StringIO()
# build_bucket.download_fileobj('portfoliobuild.zip',portfolio_zip)
#
# with zipfile.ZipFile(portfolio_zip) as myzip:
#     for nm in myzip.namelist():
#         obj = myzip.open(nm)
#         portfolio_bucket.upload_fileobj(obj,nm,
#             ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
#         portfolio_bucket.Object(nm).Acl().put(ACL='public-read')


###################################################################
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
