import os
import subprocess
import shutil
import pika
import json
import requests
import torch
from PIL import Image, UnidentifiedImageError
import time

# Paths configuration
local_temp_folder = "C:\\Users\\khali\\Desktop\\Vocies\\Project\\tempfoto"
output_folder = "C:\\Users\\khali\\Desktop\\Vocies\\Project\\output_foto"
ffmpeg_path = "ffmpeg.exe"
photo_ai_path = "C:\\Program Files\\Topaz Labs LLC\\Topaz Photo AI\\tpai.exe"
yolov5_model_path = "C:\\Users\\khali\\Desktop\\Vocies\\Project\\yolov5\\yolov5s.pt"
yolov5_repo_path = "C:\\Users\\khali\\Desktop\\Vocies\\Project\\yolov5"

# Timeout for subprocess calls
subprocess_timeout = 600
ffmpeg_timeout = 30

def clear_temp_folder(folder):
    if not os.path.exists(folder):
        print(f"Folder {folder} does not exist.")
        return

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def upscale_image_with_photo_ai(input_file, output_folder):
    if not os.path.exists(photo_ai_path):
        print(f"Photo AI executable not found at {photo_ai_path}")
        return None

    command = [
        photo_ai_path,
        input_file,
        "--output", output_folder,
        #"--overwrite",
        '--upscale scale=6 minor_denoise=100 minor_deblur=100 model="High Fidelity V2',
        '--sharpen strength=100 --denoise strength=100 minor_deblur=100 original_detail=100 ',
    ]
    try:
        print(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=subprocess_timeout)
        print(result.stdout or "No stdout")
        print(result.stderr or "No stderr")  
        output_file = os.path.join(output_folder, os.path.basename(input_file))
        print(f"Successfully upscaled {input_file} to {output_file}")
        time.sleep(5)  # Wait time
        return output_file
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {' '.join(command)}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Failed to upscale image {input_file}. Error: {e.stderr or 'No stderr'}")
        return None

def get_optimal_crop_coordinates(input_file):
    if not os.path.exists(yolov5_model_path):
        print(f"YOLOv5 model not found at {yolov5_model_path}")
        return None

    try:
        model = torch.hub.load(yolov5_repo_path, 'custom', path=yolov5_model_path, source='local')
        model.conf = 0.1  # Confidence threshold (you can adjust this value)
    except Exception as e:
        print(f"Error loading YOLOv5 model: {e}")
        return None

    try:
        with Image.open(input_file) as img:
            img.verify()
    except (IOError, SyntaxError, UnidentifiedImageError) as e:
        print(f"Invalid image file {input_file}: {e}")
        return None

    try:
        results = model(input_file)
        if len(results.xyxy[0]) > 0:
            print(f"Objects detected: {len(results.xyxy[0])}")
            best_result = results.xyxy[0][0].tolist()
            x1, y1, x2, y2 = map(int, best_result[:4])
            width, height = x2 - x1, y2 - y1
            center_x = x1 + width // 2
            center_y = y1 + int(height * 0.33)
            return (center_x, center_y)
        else:
            print(f"No objects detected in {input_file}")
            return None
    except Exception as e:
        print(f"Error processing image with YOLOv5: {e}")
        return None

def crop_image(input_file, output_file, center_x, center_y, aspect_ratio):
    try:
        image = Image.open(input_file)
    except Exception as e:
        print(f"Failed to open image {input_file}. Error: {e}")
        return None

    img_width, img_height = image.size
    if aspect_ratio == "16:9":
        new_width = img_width
        new_height = int(img_width * 9 / 16)
    elif aspect_ratio == "1:1":
        new_width = new_height = min(img_width, img_height)
    elif aspect_ratio == "9:16":
        new_height = img_height
        new_width = int(img_height * 9 / 16)
    elif aspect_ratio == "4:3":
        new_width = img_width
        new_height = int(img_width * 3 / 4)
    elif aspect_ratio == "4:5":
        new_width = img_width
        new_height = int(img_width * 5 / 4)
    else:
        raise ValueError(f"Unsupported aspect ratio: {aspect_ratio}")

    x1 = max(0, center_x - new_width // 2)
    y1 = max(0, center_y - new_height // 2)
    if x1 + new_width > img_width:
        x1 = img_width - new_width
    if y1 + new_height > img_height:
        y1 = img_height - new_height
    crop_filter = f"crop={new_width}:{new_height}:{x1}:{y1}"
    command = [
        ffmpeg_path,
        "-i", input_file,
        "-vf", crop_filter,
        output_file
    ]
    try:
        print(f"Running command: {' '.join(command)}")
        print(f"Crop parameters - x1: {x1}, y1: {y1}, new_width: {new_width}, new_height: {new_height}")
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=ffmpeg_timeout)
        print(result.stdout or "No stdout")
        print(result.stderr or "No stderr")
        print(f"Successfully cropped {input_file} to {output_file}")
        return output_file
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {' '.join(command)}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Failed to crop image {input_file}. Error: {e.stderr or 'No stderr'}")
        return None

def on_message(channel, method_frame, header_frame, body):
    message = json.loads(body)
    asset = message['asset']
    formats = message['formats']
    local_path = os.path.join(local_temp_folder, asset['filename']).replace("\\", "/")
    os.makedirs(output_folder, exist_ok=True)
    try:
        base_name, _ = os.path.splitext(asset['filename'])
        upscaled_file = upscale_image_with_photo_ai(local_path, output_folder)
        if upscaled_file:
            crop_coords = get_optimal_crop_coordinates(upscaled_file)
            if crop_coords:
                center_x, center_y = crop_coords
                for fmt in formats:
                    aspect_ratio = fmt.replace('x', ':')
                    output_file = os.path.join(output_folder, f"{base_name}_{fmt}.jpg")
                    cropped_file = crop_image(upscaled_file, output_file, center_x, center_y, aspect_ratio)
                    if cropped_file:
                        success_message = {
                            "type": "success",
                            "message": "Asset format has been successfully created and upscaled",
                            "data": {
                                "assetId": asset['id'],
                                "format": fmt,
                                "url": f"file://{cropped_file}"
                            }
                        }
                        channel.basic_publish(exchange='image-processor', routing_key='conversion-image-update', body=json.dumps(success_message))
                        print(f"Success message sent for {output_file}")
                        print(f"Success message: {json.dumps(success_message)}")
                        os.remove(upscaled_file)
                        print(f"Deleted local temp file: {upscaled_file}")
                        os.remove(local_path)
                        print(f"Deleted original file: {local_path}")
                        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    except Exception as e:
        print(f"Error processing file {local_path}: {e}")
        error_message = {
            "type": "error",
            "message": str(e),
            "data": {
                "assetId": asset['id'],
                "format": fmt if 'fmt' in locals() else "unknown"
            }
        }
        channel.basic_publish(exchange='image-processor', routing_key='conversion-image-update', body=json.dumps(error_message))
        print(f"Error message sent: {error_message}")
        channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)

def main():
    if not os.path.exists(local_temp_folder):
        os.makedirs(local_temp_folder)
        print(f"Created local temp folder: {local_temp_folder}")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='localhost',
            port=5672,
            credentials=pika.PlainCredentials('guest', 'guest')
        )
    )
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='convert-image-format',
                        on_message_callback=on_message, auto_ack=False)
    print("Waiting for messages. To exit press CTRL+C")
    try:
        for filename in os.listdir(local_temp_folder):
            if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
                local_path = os.path.join(local_temp_folder, filename).replace("\\", "/")
                asset_id = os.path.splitext(filename)[0]
                formats = ["4x3", "16x9", "1x1", "9x16", "4x5"]
                message = {
                    "asset": {"id": asset_id, "filename": filename},
                    "formats": formats,
                    "url": f"file://{local_path}"
                }
                on_message(channel, None, None, json.dumps(message))
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()
    print("Finished processing files.")

if __name__ == "__main__":
    print("FOTO-Konvertierung: Starting processing script...")
    while True:
        try:
            main()
        except Exception as e:
            print(f"Main function crashed: {e}. Restarting in 5 seconds...")
            time.sleep(5)
        except ConnectionError as e:
            print(f"Failed to establish initial connection: {e}. Retrying in 5 seconds...")
            time.sleep(5)
