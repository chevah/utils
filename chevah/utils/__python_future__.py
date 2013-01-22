# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
import __builtin__
import sys

# Python 2.6+/3.0+. The code is based on
# http://bruynooghe.blogspot.com/2008/04/xsetter-syntax-in-python-25.html
# Only patch the property once if the setter does not exists.
if not hasattr(__builtin__.property, "setter"):

    __builtin__._property = property

    class property(property):

        def __init__(self, fget, *args, **kwargs):
            self.__doc__ = fget.__doc__
            super(property, self).__init__(fget, *args, **kwargs)

        def setter(self, fset):
            cls_ns = sys._getframe(1).f_locals
            for k, v in cls_ns.iteritems():
                if v == self:
                    propname = k
                    break
            cls_ns[propname] = property(
                self.fget, fset, self.fdel, self.__doc__)
            return cls_ns[propname]

        def deleter(self, fdel):
            cls_ns = sys._getframe(1).f_locals
            for k, v in cls_ns.iteritems():
                if v == self:
                    propname = k
                    break
            cls_ns[propname] = property(
                self.fget, self.fset, fdel, self.__doc__)
            return cls_ns[propname]

    __builtin__.property = property
