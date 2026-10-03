from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from notification_service.api.schemas.common import (
    ApiError,
    ApiResponse,
)
from notification_service.plugins.exceptions import (
    InvalidPayloadError,
)
from notification_service.services.exceptions import NotificationNotFoundError


async def request_validation_error_handler(
    _request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    response = ApiResponse[None](
        error=ApiError(
            code="validation_error",
            message="Request validation failed",
            details=jsonable_encoder(exc.errors())
        )
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=response.model_dump(mode="json")
    )


async def invalid_payload_error_handler(
    _request: Request,
    exc: InvalidPayloadError
) -> JSONResponse:
    response = ApiResponse[None](
        error=ApiError(
            code="invalid_payload",
            message=str(exc),
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=response.model_dump(mode="json"),
    )


async def notification_not_found_error_handler(
    _request: Request,
    exc: NotificationNotFoundError,
) -> JSONResponse:
    response = ApiResponse[None](
        error=ApiError(
            code="notification_not_found",
            message=str(exc),
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=response.model_dump(mode="json"),
    )


def register_exception_handler(app: FastAPI) -> None:
    app.exception_handler(RequestValidationError)(
        request_validation_error_handler
    )

    app.exception_handler(InvalidPayloadError)(
        invalid_payload_error_handler
    )

    app.exception_handler(NotificationNotFoundError)(
        notification_not_found_error_handler
    )
