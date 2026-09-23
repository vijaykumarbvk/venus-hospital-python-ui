from marshmallow import Schema, fields, validate

from common.constants import UserRole


class RegisterSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8), load_only=True)
    firstName = fields.String(required=True, data_key="firstName", attribute="first_name")
    lastName = fields.String(required=True, data_key="lastName", attribute="last_name")
    phoneNumber = fields.String(required=True, data_key="phoneNumber", attribute="phone_number")
    role = fields.String(required=True, validate=validate.OneOf(UserRole.ALL))


class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)


register_schema = RegisterSchema()
login_schema = LoginSchema()
