auth_header_definition = {
    "Authorization": {
        "in": "header",
        "type": "string",
        "required": True,
        "description": "The access token needs to be preceded with 'Bearer' string.",
        "default": "Bearer ",
    }
}

auth_api_definitions = {
    "logout": {
        "path": "/logout",
        "operations": {
            "get": {
                "description": "Endpoint for changing password.",
                "parameters": [
                    {"in": "header", "name": "Authorization", "required": True, "type": "string"},
                ],
                "responses": {
                    "302": {"description": "The user has been logged out and redirected to /."},
                    "404": {"description": "The redirect page does not exist."},
                },
                "tags": ["auth"],
            }
        },
    },
    "register": {
        "path": "/register",
        "operations": {
            "post": {
                "description": "User registration endpoint",
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "properties": {
                                "email": {"format": "email", "type": "string"},
                                "password": {"format": "password", "type": "string"},
                            },
                            "required": ["email", "password"],
                            "type": "object",
                        },
                    }
                ],
                "responses": {
                    "200": {"description": "User has been registered and a confirmation email has been sent."},
                    "400": {"description": "Either email or password is not valid (Validation error)."},
                },
                "tags": ["auth"],
            }
        },
    },
    "confirm": {
        "path": "/confirm/{confirmation_token}",
        "operations": {
            "get": {
                "description": "Registration confirm endpoint",
                "parameters": [
                    {"in": "path", "name": "confirmation_token", "required": True, "type": "string"},
                ],
                "responses": {
                    "302": {"description": "The registration has been confirmed and the user will be redirected to /."},
                    "400": {"description": "The token might have expired or is invalid."},
                    "404": {"description": "The redirect page does not exist."},
                },
                "tags": ["auth"],
            }
        },
    },
    "reset_password": {
        "path": "/reset",
        "operations": {
            "post": {
                "description": "Reset password endpoint",
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "properties": {"email": {"format": "email", "type": "string"}},
                            "required": [
                                "email",
                            ],
                            "type": "object",
                        },
                    }
                ],
                "responses": {
                    "200": {
                        "description": "A link to the password change page has been sent to user's e-mail address."
                    },
                    "400": {"description": "The entered email does not correspond to any user."},
                },
                "tags": ["auth"],
            }
        },
    },
    "set_new_password": {
        "path": "/reset/{password_reset_token}",
        "operations": {
            "post": {
                "description": "Endpoint for setting a new password after requesting a password recover endpoint.",
                "parameters": [
                    {"in": "path", "name": "password_reset_token", "required": True, "type": "string"},
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "properties": {
                                "password": {"format": "password", "type": "string"},
                                "password_confirm": {"format": "password", "type": "string"},
                            },
                            "required": ["email", "password"],
                            "type": "object",
                        },
                    },
                ],
                "responses": {
                    "200": {"description": "The entered password has been set."},
                    "400": {"description": "Either the passwords don't match or did not pass the validation process."},
                },
                "tags": ["auth"],
            }
        },
    },
}
