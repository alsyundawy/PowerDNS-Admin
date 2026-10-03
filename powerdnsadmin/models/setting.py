import sys
from ast import literal_eval

import pytimeparse
from flask import current_app

from powerdnsadmin.lib.settings import AppSettings

from .base import db


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    value = db.Column(db.Text())

    ZONE_TYPE_FORWARD = "forward"
    ZONE_TYPE_REVERSE = "reverse"

    def __init__(self, setting_id=None, name=None, value=None, id=None):
        record_id = setting_id if setting_id is not None else id
        if isinstance(record_id, str) and value is None and name is not None:
            # Defensive fallback if called positionally as Setting(name, value)
            value = str(name)
            name = record_id
            record_id = None
        self.id = record_id
        self.name = name
        self.value = value

    def set_maintenance(self, mode):
        maintenance = Setting.query.filter(Setting.name == "maintenance").first()

        if maintenance is None:
            value = AppSettings.defaults["maintenance"]
            maintenance = Setting(name="maintenance", value=str(value))
            db.session.add(maintenance)

        mode = str(mode)

        try:
            if maintenance.value != mode:
                maintenance.value = mode
                db.session.commit()
            return True
        except Exception as e:
            current_app.logger.exception("Cannot set maintenance to {0}. DETAIL: {1}".format(mode, e))
            db.session.rollback()
            return False

    def toggle(self, setting):
        current_setting = Setting.query.filter(Setting.name == setting).first()

        if current_setting is None:
            value = AppSettings.defaults[setting]
            current_setting = Setting(name=setting, value=str(value))
            db.session.add(current_setting)

        try:
            if current_setting.value == "True":
                current_setting.value = "False"
            else:
                current_setting.value = "True"
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.exception("Cannot toggle setting {0}. DETAIL: {1}".format(setting, e))
            db.session.rollback()
            return False

    def set(self, setting, value):
        import json

        current_setting = Setting.query.filter(Setting.name == setting).first()

        if current_setting is None:
            current_setting = Setting(name=setting, value=None)
            db.session.add(current_setting)

        value = AppSettings.convert_type(setting, value)

        if isinstance(value, dict) or isinstance(value, list):
            value = json.dumps(value)

        try:
            current_setting.value = value
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.exception("Cannot edit setting {0}. DETAIL: {1}".format(setting, e))
            db.session.rollback()
            return False

    def _resolve_raw_setting(self, setting):
        if setting.upper() in current_app.config:
            return current_app.config[setting.upper()]
        return self.query.filter(Setting.name == setting).first()

    def get(self, setting):
        if setting not in AppSettings.defaults:
            current_app.logger.error("Unknown setting queried: {0}".format(setting))
            return None

        result = self._resolve_raw_setting(setting)
        if result is None:
            return AppSettings.defaults[setting]

        if hasattr(result, "value"):
            result = result.value

        result = AppSettings.convert_type(setting, result)
        if setting in ("forward_records_allow_edit", "reverse_records_allow_edit"):
            defaults_val = AppSettings.defaults.get(setting, {})
            default_map = defaults_val if isinstance(defaults_val, dict) else {}
            if not isinstance(result, dict):
                current_app.logger.warning(
                    "Setting {0} is not a mapping, falling back to " "the defaults".format(setting)
                )
                return dict(default_map)
            result = {
                **default_map,
                **result,
            }
        return result

    def get_group(self, group):
        if not isinstance(group, list):
            group = AppSettings.groups[group]

        result = {}

        for var_name in AppSettings.defaults:
            if var_name in group:
                result[var_name] = self.get(var_name)

        return result

    def get_records_allow_to_edit(self):
        return list(
            set(
                self.get_supported_record_types(self.ZONE_TYPE_FORWARD)
                + self.get_supported_record_types(self.ZONE_TYPE_REVERSE)
            )
        )

    def get_supported_record_types(self, zone_type):
        setting_value = []

        if zone_type == self.ZONE_TYPE_FORWARD:
            setting_value = self.get("forward_records_allow_edit")
        elif zone_type == self.ZONE_TYPE_REVERSE:
            setting_value = self.get("reverse_records_allow_edit")

        records = literal_eval(setting_value) if isinstance(setting_value, str) else setting_value
        types = [r for r in records if records[r]]

        # Sort alphabetically if python version is smaller than 3.6
        if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
            types.sort()

        return types

    def get_ttl_options(self):
        return [(pytimeparse.parse(ttl), ttl) for ttl in self.get("ttl_options").split(",")]
