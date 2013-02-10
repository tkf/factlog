# Copyright (c) 2013- Takafumi Arakaki

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import platform


def get_config_directory(appname):
    """
    Get OS-specific configuration directory.

    :type appname: str
    :arg  appname: capitalized name of the application

    """
    if platform.system().lower() == 'windows':
        path = os.path.join(os.getenv('APPDATA') or '~', appname, appname)
    elif platform.system().lower() == 'darwin':
        path = os.path.join('~', 'Library', 'Application Support', appname)
    else:
        path = os.path.join(os.getenv('XDG_CONFIG_HOME') or '~/.config',
                            appname.lower())
    return os.path.expanduser(path)


class ConfigStore(object):

    base_path = get_config_directory('FactLog')
    data_path = os.path.join(base_path, 'data')
    db_path = os.path.join(data_path, 'db.sqlite')

    def __init__(self):
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
