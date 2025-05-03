import os
import boto3

class S3KaggleModelSync:
    def __init__(self, aws_access_key, aws_secret_key, region, bucket_name, s3_prefix, base_dir="/kaggle/working"):
        print("[INIT] Setting AWS credentials and initializing S3 client...")
        
        self.bucket = bucket_name
        self.prefix = s3_prefix
        self.local_dir = os.path.join(base_dir, s3_prefix)  # Final local save dir

        os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_key
        os.environ["AWS_DEFAULT_REGION"] = region

        os.makedirs(self.local_dir, exist_ok=True)
        self.s3 = boto3.client("s3")

        print(f"[INIT DONE] Bucket: {self.bucket}")
        print(f"           Prefix: {self.prefix}")
        print(f"           Local Dir: {self.local_dir}")

    def download(self):
        print("\n[DOWNLOAD] Starting download from S3...")
        paginator = self.s3.get_paginator('list_objects_v2')
        found = False
        for page in paginator.paginate(Bucket=self.bucket, Prefix=self.prefix):
            for obj in page.get('Contents', []):
                found = True
                s3_key = obj['Key']
                local_path = os.path.join(self.local_dir, os.path.relpath(s3_key, self.prefix))
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                print(f"[DOWNLOADING] {s3_key} → {local_path}")
                self.s3.download_file(self.bucket, s3_key, local_path)

        if not found:
            print("[INFO] No files found at that prefix in the bucket.")
        else:
            print("[DOWNLOAD DONE] All files downloaded.")

    def upload(self):
        print("\n[UPLOAD] Starting upload to S3...")
        for root, _, files in os.walk(self.local_dir):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, self.local_dir)
                s3_key = f"{self.prefix}/{relative_path}"
                print(f"[UPLOADING] {full_path} → s3://{self.bucket}/{s3_key}")
                self.s3.upload_file(full_path, self.bucket, s3_key)
        print("[UPLOAD DONE] All files uploaded.")
