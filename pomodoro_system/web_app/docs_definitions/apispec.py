from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

marshmallow_plugin = MarshmallowPlugin()

api_spec = APISpec(
    title="Pomodoro App",
    version="0.1.0",
    openapi_version="2.0",
    info={"description": "The API documentation contains user-specific methods and authentication-related endpoints"},
    plugins=[marshmallow_plugin],
    securityDefinitions={
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    },
    security=[{"Bearer": []}],
)
