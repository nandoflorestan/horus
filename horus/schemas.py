# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import re
import colander as c
import deform
import deform.widget as w
from hem.db import get_session
from hem.schemas import CSRFSchema
from .interfaces import IUserClass, IUIStrings
from .models import _


def email_exists(node, val):
    '''Colander validator that ensures a User exists with the email.'''
    req = node.bindings['request']
    User = req.registry.getUtility(IUserClass)
    exists = get_session(req).query(User).filter(User.email.ilike(val)).count()
    if not exists:
        Str = req.registry.getUtility(IUIStrings)
        raise c.Invalid(node, Str.reset_password_email_must_exist.format(val))


def unique_email(node, val):
    '''Colander validator that ensures the email does not exist.'''
    req = node.bindings['request']
    User = req.registry.getUtility(IUserClass)
    other = get_session(req).query(User).filter(User.email.ilike(val)).first()
    if other:
        S = req.registry.getUtility(IUIStrings)
        raise c.Invalid(node, S.registration_email_exists.format(other.email))


def unique_username(node, value):
    '''Colander validator that ensures the username does not exist.'''
    req = node.bindings['request']
    User = req.registry.getUtility(IUserClass)
    if get_session(req).query(User).filter(User.username == value).count():
        Str = req.registry.getUtility(IUIStrings)
        raise c.Invalid(node, Str.registration_username_exists)


def unix_username(node, value):  # TODO This is currently not used
    '''Colander validator that ensures the username is alphanumeric.'''
    if not ALPHANUM.match(value):
        raise c.Invalid(node, _("Contains unacceptable characters."))
ALPHANUM = re.compile(r'^[a-zA-Z0-9_.-]+$')


# Schema fragments
# ----------------
# These functions reduce duplication in the schemas defined below,
# while ensuring some constant values are consistent among those schemas.

def get_email_node(validator=None, description=_("Example: joe@example.com")):
    return c.SchemaNode(
        c.String(), title=_('Email'), description=description,
        validator=validator or c.All(c.Email(), unique_email),
        widget=w.TextInputWidget(size=40, maxlength=260, type='email'))


def get_checked_password_node(description=_(
        "Your password must be harder than a dictionary word or proper name!"),
        **kw):
    return c.SchemaNode(
        c.String(), title=_('Password'), validator=c.Length(min=4),
        widget=deform.widget.CheckedPasswordWidget(),
        description=description, **kw)


# Schemas
# -------

class UsernameLoginSchema(CSRFSchema):
    handle = c.SchemaNode(c.String(), title=_('User name'))
    password = c.SchemaNode(c.String(), validator=c.Length(min=4),
                            widget=deform.widget.PasswordWidget())
LoginSchema = UsernameLoginSchema  # TODO name "LoginSchema" is deprecated.


class EmailLoginSchema(CSRFSchema):  # TODO Not currently used
    '''For login, some apps just use email and have no username column.'''
    handle = get_email_node()
    password = c.SchemaNode(c.String(), validator=c.Length(min=4),
                            widget=deform.widget.PasswordWidget())


class UsernameRegisterSchema(CSRFSchema):
    username = c.SchemaNode(c.String(), title=_('User name'),
                            description=_("Name with which you will log in"),
                            validator=unique_username)
    email = get_email_node()
    password = get_checked_password_node()
RegisterSchema = UsernameRegisterSchema  # TODO The name "RegisterSchema" is deprecated.


class EmailRegisterSchema(CSRFSchema):  # TODO Not currently used
    email = get_email_node()
    password = get_checked_password_node()


class ForgotPasswordSchema(CSRFSchema):
    email = get_email_node(
        validator=c.All(c.Email(), email_exists),
        description=_("The email address under which you have your account. "
                      "Example: joe@example.com"))


class UsernameResetPasswordSchema(CSRFSchema):
    username = c.SchemaNode(
        c.String(),
        missing=c.null,
        widget=deform.widget.TextInputWidget(template='readonly/textinput'))
    password = get_checked_password_node()
ResetPasswordSchema = UsernameResetPasswordSchema  # TODO deprecated name


class EmailResetPasswordSchema(CSRFSchema):  # TODO Not currently used
    email = get_email_node()
    password = get_checked_password_node()
    # Is this really the same code as EmailRegisterSchema?


class UsernameProfileSchema(CSRFSchema):
    username = c.SchemaNode(
        c.String(),
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        missing=c.null)
    email = get_email_node(description=None, validator=c.Email())
    password = get_checked_password_node(missing=c.null)
ProfileSchema = UsernameProfileSchema  # TODO deprecated name


class EmailProfileSchema(CSRFSchema):  # TODO Not currently used
    email = get_email_node(description=None, validator=c.Email())
    password = get_checked_password_node(missing=c.null)


class UsernameAdminUserSchema(CSRFSchema):
    username = c.SchemaNode(c.String())
    email = get_email_node(description=None, validator=c.Email())
    password = get_checked_password_node(description=None, missing=c.null)
AdminUserSchema = UsernameAdminUserSchema  # TODO deprecated name


class EmailAdminUserSchema(CSRFSchema):  # TODO Not currently used
    email = get_email_node(description=None, validator=c.Email())
    password = get_checked_password_node(description=None, missing=c.null)
