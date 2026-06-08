import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv
import os

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

s3_client = boto3.client("s3", region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def upload_file(file_obj, key: str):
    """
    Sube un archivo a S3.
    :param file_obj: objeto tipo file (ej. UploadFile de FastAPI)
    :param key: ruta/nombre dentro del bucket
    """
    try:
        response = s3_client.list_buckets()
        print("Buckets disponibles:", [b["Name"] for b in response["Buckets"]])
        s3_client.upload_fileobj(file_obj, S3_BUCKET, key)
        return f"s3://{S3_BUCKET}/{key}"
    except NoCredentialsError:
        raise RuntimeError("Credenciales AWS no encontradas")
    except ClientError as e:
        raise RuntimeError(f"Error al subir archivo: {e}")

def download_file(key: str, local_dir: str = None):
    """
    Descarga un archivo desde S3 y lo guarda en una carpeta local.
    :param key: ruta/nombre dentro del bucket (ej. 'uploads/.../archivo.pdf')
    :param local_dir: carpeta local donde guardar (por defecto app/uploads)
    :return: ruta absoluta del archivo descargado
    """
    if local_dir is None:
        local_dir = os.path.join(os.getcwd(), "uploads")
    filename = os.path.basename(key)
    local_path = os.path.join(local_dir, filename)
    try:
        s3_client.download_file(S3_BUCKET, key, local_path)
        return local_path
    except ClientError as e:
        raise RuntimeError(f"Error al descargar archivo: {e}")
