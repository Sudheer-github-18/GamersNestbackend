from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg.inspectors import SwaggerAutoSchema

class CustomSwaggerSchema(SwaggerAutoSchema):
    def get_operation(self, path, method):
        operation = super().get_operation(path, method)
        # Customize operation here
        return operation

    def get_response(self, path, method, status):
        response = super().get_response(path, method, status)
        # Customize response here
        return response

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version="v1",
        description="Your API description",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(),
)