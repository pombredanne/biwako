import collections
import threading


class NameAwareOrderedDict(collections.OrderedDict):
    """
    A custom namespace that not only orders its items, but can
    also make those items aware of their names immediately.
    It also helps maintain the list of fields in the stack.
    """

    def __setitem__(self, name, obj):
        if len(data.field_stack) == 1:
            # Only assign to the root namespace if it's not nested in a with block
            super(NameAwareOrderedDict, self).__setitem__(name, obj)

        if hasattr(obj, 'set_name'):
            obj.set_name(name)
            data.field_stack[-1].append(obj)


class DeclarativeMetaclass(type):
    @classmethod
    def __prepare__(cls, name, bases, **options):
        data.field_options = options
        data.field_stack = [[]]
        return NameAwareOrderedDict()

    def __new__(cls, name, bases, attrs, **options):
        # Nothing to do here, but we need to make sure options
        # don't get passed in to type.__new__() itself.
        return type.__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs, **options):
        cls._fields = []
        for name, attr in attrs.items():
            if hasattr(attr, 'attach_to_class'):
                attr.attach_to_class(cls)
        data.field_options = {}
        data.field_stack = [[]]


class DeclarativeFieldMetaclass(type):
    @classmethod
    def __prepare__(cls, name, bases, **options):
        return NameAwareOrderedDict()

    def __init__(cls, name, bases, attrs, **options):
        cls.arguments = {}
        # Go backwards so that the left-most classes take priority
        for base in reversed(bases):
            if hasattr(base, 'arguments'):
                cls.arguments.update(base.arguments)

        for name, attr in attrs.items():
            if name in cls.arguments and attr is None:
                del cls.arguments[name]
            if hasattr(attr, 'attach_to_class'):
                attr.attach_to_class(cls)

    def __call__(cls, *args, **kwargs):
        if data.field_options:
            options = {}
            for name, value in data.field_options.items():
                if name in cls.arguments:
                    options[name] = value
            options.update(kwargs)
        else:
            options = kwargs
        return super(DeclarativeFieldMetaclass, cls).__call__(*args, **options)


# Temporary storage
data = threading.local()
data.field_options = {}
data.field_stack = [[]]

