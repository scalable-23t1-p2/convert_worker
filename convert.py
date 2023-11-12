import subprocess
import utils
import boto3
import os
from dotenv import load_dotenv
from celery import Celery

raw_video = "raw_video"
video_output = "video_output"
client = boto3.client(
's3',
aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
aws_secret_access_key=os.getenv("S3_SECRET_KEY")
)
BROKER_URL = os.getenv("CELERY_BROKER_URL")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
celery_app = Celery('convert', broker=BROKER_URL,
                    backend=RESULT_BACKEND)

@celery_app.task(name="convert")    
def convert(filename, s3_file_path):
    try:
        print("Converting video format to mp4")
        print("filename = "+filename)
        print("s3_file_path = "+s3_file_path)
        file = filename
        filename_noext, extension = utils.extract_ext(file)
        output_file = filename_noext + ".mp4"
        user_folder = s3_file_path.split('/',1)[0]
        BUCKET_NAME = 'toktikbucket'
        S3_PATH = s3_file_path
        LOCAL_PATH=f"{raw_video}/{filename}"
        S3_UPLOAD_PATH = f'{user_folder}/{output_file}'
        if extension != "mp4":
            print("localpath = "+LOCAL_PATH)
            utils.create_dir(raw_video)
            client.download_file(Bucket=BUCKET_NAME, Key=S3_PATH, Filename=LOCAL_PATH)
            print("done download raw from s3")
            client.delete_object(Bucket=BUCKET_NAME, Key=S3_PATH)
            print("done delete raw_video from s3")
            utils.create_dir(video_output)
            subprocess.run(
            [
            "ffmpeg",
            "-i",
            f"{LOCAL_PATH}",
            "-vf",
            "scale='min(1080,iw)':-1",
            "-crf",
            "18",
            "-preset",
            "slow",
            f"{video_output}/{output_file}",
            ]
            )
            print("done reformat to mp4")
            client.upload_file(Bucket=BUCKET_NAME, Key=S3_UPLOAD_PATH,Filename= f"{video_output}/{output_file}")
            print("done upload to s3")
            utils.clean_dir(filename) 
        task_thumbnail = celery_app.send_task("thumbnail", queue='q02',args=[filename, S3_UPLOAD_PATH])
        print("done send task thumbnail")
        task_chunk = celery_app.send_task("chunk", queue='q03',args=[filename, S3_UPLOAD_PATH])
        print("done send task chunkvid")
        return (task_chunk.task_id, task_thumbnail.task_id)
    except Exception as e:
        print(e.with_traceback)
        utils.clean_dir(filename)
        return ("error", "error")

if __name__ == "__main__":
    convert()
