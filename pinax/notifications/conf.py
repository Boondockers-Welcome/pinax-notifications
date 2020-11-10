from __future__ import unicode_literals

import importlib

from django.apps import apps as django_apps
from django.conf import settings  # noqa
from django.core.exceptions import ImproperlyConfigured

from appconf import AppConf


def load_model(path):
    try:
        return django_apps.get_model(path)
    except ValueError:
        raise ImproperlyConfigured(
            "{0} must be of the form 'app_label.model_name'".format(path)
        )
    except LookupError:
        raise ImproperlyConfigured("{0} has not been installed".format(path))


def load_path_attr(path):
    i = path.rfind(".")
    module, attr = path[:i], path[i + 1:]
    try:
        mod = importlib.import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured("Error importing {0}: '{1}'".format(module, e))
    try:
        attr = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured("Module '{0}' does not define a '{1}'".format(module, attr))
    return attr


def is_installed(package):
    try:
        __import__(package)
        return True
    except ImportError:
        return False


class PinaxNotificationsAppConf(AppConf):

    LOCK_WAIT_TIMEOUT = -1
    GET_LANGUAGE_MODEL = None
    LANGUAGE_MODEL = None
    QUEUE_ALL = False
    HOOKSET = "pinax.notifications.hooks.DefaultHookSet"
    BACKENDS = [
        ("email", "pinax.notifications.backends.email.EmailBackend"),
    ]
    AGGREGATE_NOTICES = {
        # Format label_name: AggregateNoticeModel
        # where AggregateNotice Model implements the following class methods
        #   @classmethod
        #   def save_notice_to_aggregate(label, user, extra_context, sender)
        #       method should store unsent notices in a model to be dealt
        #       with in aggregate_send_method.
        #       Returns boolean indicating if notice is being saved for aggregation.
        #       If not, engine will send it immediately.
        #
        #   @classmethod
        #   def get_aggregate_notices_method():
        #       returns list of notices to send in format
        #       [(user, label, extra_content, sender)]
        #       Note that label returned here could be different than original label
    }

    def configure_backends(self, value):
        backends = []
        for medium_id, bits in enumerate(value):
            if len(bits) == 2:
                label, backend_path = bits
                spam_sensitivity = None
            elif len(bits) == 3:
                label, backend_path, spam_sensitivity = bits
            else:
                raise ImproperlyConfigured(
                    "NOTIFICATION_BACKENDS does not contain enough data."
                )
            backend_instance = load_path_attr(backend_path)(medium_id, spam_sensitivity)
            backends.append(((medium_id, label), backend_instance))
        return dict(backends)

    def configure_get_language_model(self, value):
        if value is None:
            return lambda: load_model(settings.PINAX_NOTIFICATIONS_LANGUAGE_MODEL)

    def configure_aggregate_notices(self, value):
        aggregate_notices = {}
        for label, model in value.items():
            aggregate_notices[label] = load_path_attr(model)
        return aggregate_notices

    def configure_hookset(self, value):
        return load_path_attr(value)()

    class Meta:
        prefix = "pinax_notifications"
