import datetime
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import status
from typing import Any, Optional, Dict


class CustomResponse:
    """Utility class providing standardized API responses.

    All API responses should follow this structure for consistency.
    
    Response shape:
      - success (bool): Indicates if the request was successful.
      - status_code (int): The HTTP status code.
      - message (str): A human-readable message describing the result.
      - timestamp (str): ISO8601 UTC timestamp of the response.
      - data (any): Optional payload containing requested data.
      - errors (any): Details about errors (e.g., validation).
    """

    @staticmethod
    def _now_iso() -> str:
        """Helper to get current time in ISO8601 UTC format."""
        return timezone.now().astimezone(datetime.timezone.utc).isoformat()

    @staticmethod
    def success(
        message: str,
        data: Optional[Any] = None,
        status_code: int = status.HTTP_200_OK,
    ) -> Response:
        """Return a standardized success response.
       
        Args:
            message: Success message.
            data: Data payload to return.
            status_code: HTTP status code (default 200).
        """
        response_data: Dict[str, Any] = {
            "success": True,
            "status_code": int(status_code),
            "message": message,
            "timestamp": CustomResponse._now_iso(),
            "data": data,
            "errors": None,
        }

        return Response(response_data, status=int(status_code))

    @staticmethod
    def error(
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: Optional[Any] = None,
        data: Optional[Any] = None,
        errors: Optional[Any] = None,
    ) -> Response:
        """Return a standardized error response.
        
        Args:
            message: Error message or title.
            status_code: HTTP status code (default 400).
            code: Optional custom error code.
            data: Optional data payload (even in error).
            errors: Detailed error information (e.g., serializer fields).
        """
        response_data: Dict[str, Any] = {
            "success": False,
            "status_code": int(status_code),
            "code": code if code is not None else int(status_code),
            "message": message,
            "timestamp": CustomResponse._now_iso(),
            "data": data,
            "errors": errors,
        }

        return Response(response_data, status=int(status_code))
