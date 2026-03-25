import os
import json
import base64
import uuid
from pathlib import Path
from dotenv import load_dotenv

from django.core.files.storage import default_storage

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from openai import OpenAI

from users.permission import ProfileAccessMixin
from core.utils import CustomResponse, custom_exception_handler

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


class ScanItemView(ProfileAccessMixin, APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        try:
            img = request.FILES.get('image')
            if not img:
                return CustomResponse.error(
                    message="No image provided.",
                    status_code=400
                )

            ext = Path(img.name).suffix.lower()
            file_bytes = img.read()
            img.seek(0)  # Reset file pointer after reading bytes

            if ext not in ['.jpg', '.jpeg', '.png']:
                return CustomResponse.error(
                    message="Unsupported file format.",
                    status_code=400
                )

            # Save the image to media directory
            filename = f"scanning_item/{uuid.uuid4()}{ext}"
            saved_path = default_storage.save(filename, img)
            try:
                image_url = request.build_absolute_uri(
                    default_storage.url(saved_path)
                )
            except Exception:
                image_url = default_storage.url(saved_path)

            # Convert bytes to base64 string
            b64_image = base64.b64encode(file_bytes).decode("utf-8")

            # Remove the dot from extension for data URL
            mime_type = "image/jpeg" if ext in ['.jpg', '.jpeg'] else "image/png"

            response = client.chat.completions.create( 
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI that extracts product details from images. "
                            "Always return valid JSON with keys: title, color, size, brand, description, quantity. "
                            "The 'quantity' must be a number (e.g., 1). "
                            "The 'color' must be a JSON array of 6-character hex color codes (e.g., ['#FF0000', '#000000']) representing the dominant colors."
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this image and return product details including numeric quantity."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{b64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300,
                response_format={ "type": "json_object" }
            )

            content = response.choices[0].message.content
            
            # Parse the text response into JSON if it succeeds
            try:
                parsed_data = json.loads(content)
                parsed_data["images_url"] = image_url
            except json.JSONDecodeError:
                # Fallback if the model didn't return perfect JSON
                parsed_data = {
                    "images_url": image_url,
                    "raw_output": content
                }

            return CustomResponse.success(
                data=parsed_data,
                message="Image scanned successfully",
                status_code=200
            )

        except Exception as e:
            return custom_exception_handler(e, request)
