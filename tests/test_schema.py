from pydantic import ValidationError
from app.models.api_models import ChatResponse, Recommendation


def test_response_schema_accepts_valid_payload():
    response = ChatResponse(
        reply="Here are recommended assessments.",
        recommendations=[
            Recommendation(
                name="Java 8 (New)",
                url="https://www.shl.com/products/product-catalog/view/java-8-new/",
                test_type="K",
            )
        ],
        end_of_conversation=True,
    )
    assert response.recommendations[0].name == "Java 8 (New)"


def test_response_schema_rejects_extra_fields():
    try:
        ChatResponse(reply="x", recommendations=[], end_of_conversation=False, unexpected=True)
    except ValidationError:
        return
    raise AssertionError("Extra fields must be rejected")

