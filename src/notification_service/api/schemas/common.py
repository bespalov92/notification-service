from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ApiSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_alias=True,
        validate_by_name=True,
        serialize_by_alias=True,
        extra="forbid",
    )


class ApiError(ApiSchema):
    code: str = Field(
        description="Machine-readable error code",
    )

    message: str = Field(
        description="Human-readable error message",
    )

    details: list[dict[str, object]] | None = Field(
        default=None,
        description="Additional structured error details",
    )


class ApiResponse[DataT](ApiSchema):
    data: DataT | None = Field(
        default=None,
        description="Response payload for a successful request",
    )

    meta: dict[str, object] = Field(
        default_factory=dict,
        description="Additional response metadata",
    )

    error: ApiError | None = Field(
        default=None,
        description="Error information for a failed request",
    )
