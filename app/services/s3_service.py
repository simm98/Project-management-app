import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv
import os

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")

s3_client = boto3.client("s3", region_name=AWS_REGION)

def upload_file(file_obj, key: str):
    """
    Sube un archivo a S3.
    :param file_obj: objeto tipo file (ej. UploadFile de FastAPI)
    :param key: ruta/nombre dentro del bucket
    """
    try:
        s3_client.upload_fileobj(file_obj, S3_BUCKET, key)
        return f"s3://{S3_BUCKET}/{key}"
    except NoCredentialsError:
        raise RuntimeError("Credenciales AWS no encontradas")
    except ClientError as e:
        raise RuntimeError(f"Error al subir archivo: {e}")

def download_file(key: str, local_path: str):
    """
    Descarga un archivo desde S3.
    """
    try:
        s3_client.download_file(S3_BUCKET, key, local_path)
        return local_path
    except ClientError as e:
        raise RuntimeError(f"Error al descargar archivo: {e}")
