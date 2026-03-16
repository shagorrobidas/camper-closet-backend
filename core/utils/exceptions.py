from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import logging
import traceback
from typing import Any, Optional
from datetime import timezone as dt_timezone
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc: Exception, context: Optional[Any] = None):
    """Custom exception handler that normalizes error responses.

    Uses the same response shape as `CustomResponse.error` so clients
    receive consistent payloads for all API errors.
    """
    # Ensure context is a dictionary for DRF's exception_handler
    if context is None:
        context = {}
    elif not isinstance(context, dict):
        # If context is a request object (as seen in some calls), wrap it
        context = {'request': context}

    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        error_data = response.data

        message: str = "An error occurred"
        code: Any = response.status_code
        errors: Optional[Any] = None

        if isinstance(error_data, dict):
            # Try to extract message from common keys
            detail = error_data.get("detail")
            custom_error = error_data.get("error")
            custom_message = error_data.get("message")
            custom_code = error_data.get("code")

            if custom_message:
                if isinstance(custom_message, list) and custom_message:
                    message = str(custom_message[0])
                else:
                    message = str(custom_message)
            elif custom_error:
                if isinstance(custom_error, list) and custom_error:
                    message = str(custom_error[0])
                else:
                    message = str(custom_error)
            elif detail:
                message = str(detail)

            if custom_code:
                if isinstance(custom_code, list) and custom_code:
                    code = custom_code[0]
                else:
                    code = custom_code

            # Extract actual validation errors if present
            raw_errors = {
                k: v for k, v in error_data.items()
                if k not in ["detail", "error", "code", "message"]
            }
            if raw_errors:
                error_msgs = []
                for k, v in raw_errors.items():
                    if isinstance(v, list):
                        error_msgs.extend([str(item) for item in v])
                    else:
                        error_msgs.append(str(v))
                errors = {"message": " ".join(error_msgs)}
            else:
                errors = None
        elif isinstance(error_data, list):
            errors = error_data
            if len(error_data) > 0 and isinstance(error_data[0], str):
                message = error_data[0]
        else:
            if error_data:
                errors = error_data
                message = str(error_data)

        custom_response = {
            "success": False,
            "status_code": response.status_code,
            "code": code,
            "message": message,
            "timestamp": timezone.now().astimezone(dt_timezone.utc).isoformat(),
            "data": None,
            "errors": errors,
        }

        response.data = custom_response
    else:
        # Handle exceptions that DRF's default handler doesn't catch
        # (e.g., Django's ObjectDoesNotExist or other 500s)
        
        if isinstance(exc, ObjectDoesNotExist):
            custom_response = {
                "success": False,
                "status_code": status.HTTP_404_NOT_FOUND,
                "code": 404,
                "message": str(exc),
                "timestamp": timezone.now().astimezone(dt_timezone.utc).isoformat(),
                "data": None,
                "errors": {"detail": str(exc)},
            }
            return Response(custom_response, status=status.HTTP_404_NOT_FOUND)

        logger.error(f"Unhandled Exception: {str(exc)}")
        logger.error(traceback.format_exc())

        custom_response = {
            "success": False,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "An internal server error occurred.",
            "timestamp": timezone.now().astimezone(dt_timezone.utc).isoformat(),
            "data": None,
            "errors": str(exc) if settings.DEBUG else None,
        }

        if settings.DEBUG:
            custom_response["errors"] = {
                "detail": str(exc),
                "traceback": traceback.format_exc().split("\n")
            }

        response = Response(
            custom_response,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
