##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
import time

from base.utils.cache import cache

CACHE_NOTIFICATIONS_TIMEOUT = 1800  # seconds -> 30 min
NOTIFICATIONS_KEY = "notifications_user_{}"
NOTIFICATIONS_TIMESTAMP = "notifications_last_read_user_{}"


def get_user_notifications(user):
    notifications_cached = get_notifications_in_cache(user)
    return notifications_cached if notifications_cached is not None else set_notifications_in_cache(user)


def get_notifications_in_cache(user):
    cache_key = make_notifications_cache_key(user)
    return cache.get(cache_key)


def set_notifications_in_cache(user):
    cache_key = make_notifications_cache_key(user)
    notifications = [notification.verb for notification in user.notifications.unread()]

    cache.set(cache_key, notifications, CACHE_NOTIFICATIONS_TIMEOUT)

    return notifications


def clear_user_notifications(user):
    cache_key = make_notifications_cache_key(user)
    cache.delete(cache_key)

    user.notifications.mark_all_as_deleted()


def are_notifications_already_loaded(user):
    cache_key = make_notifications_cache_key(user)
    return cache_key in cache


def get_notifications_last_date_read_for_user(user):
    cache_key = make_notifications_timestamp_cache_key(user)
    timestamp_last_read = cache.get(cache_key)
    return datetime.date.fromtimestamp(float(timestamp_last_read)) if timestamp_last_read else None


def set_notifications_last_read_as_today_for_user(user):
    cache_key = make_notifications_timestamp_cache_key(user)
    cache.set(cache_key, str(time.time()))


def make_notifications_cache_key(user):
    return NOTIFICATIONS_KEY.format(user.pk)


def make_notifications_timestamp_cache_key(user):
    return NOTIFICATIONS_TIMESTAMP.format(user.pk)
