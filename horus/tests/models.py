# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from sqlalchemy.ext.declarative import declarative_base
from horus.models import (ActivationMixin, BaseModel, GroupMixin, UserMixin,
                          UsernameMixin, UserGroupMixin)

Base = declarative_base(cls=BaseModel)


class User(UserMixin, UsernameMixin, Base):
    pass


class Group(GroupMixin, Base):
    pass


class UserGroup(UserGroupMixin, Base):
    pass


class Activation(ActivationMixin, Base):
    pass
