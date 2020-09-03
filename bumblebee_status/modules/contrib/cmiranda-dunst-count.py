# pylint: disable=C0111,R0903

"""
Displays the unread dunst notifications count

contributed by `cristianmiranda <https://github.com/cristianmiranda>`_ - many thanks!
"""

import os
import shutil

import requests

import core.decorators
import core.input
import core.module
import core.widget
import util.cli


class Module(core.module.Module):

    #
    # See ~/bin/update-notifications-count
    #
    APP_TMP_PATH = "/tmp/{}.dunst"

    @core.decorators.every(seconds=5)
    def __init__(self, config, theme):
        super().__init__(config, theme, core.widget.Widget(self.notifications))

        self.__total = 0
        self.__label = "-"

        self.__icon = self.parameter("icon", "")
        if len(self.__icon) > 0:
            self.__icon += " "

        self.__i3FocusWindow = self.parameter("i3-focus-window", "")

        self.__apps = []
        apps = self.parameter("apps", "")
        if apps:
            self.__apps = util.format.aslist(apps)

        core.input.register(self, button=core.input.LEFT_MOUSE, cmd=self.click)

    def notifications(self, _):
        return str(self.__label)

    def update(self):
        try:
            self.__total = 0
            label = "-"

            counts = []
            if len(self.__apps) > 0:
                for app in self.__apps:
                    count = self.__getAppCount(app)
                    self.__total += count
                    counts.append(str(count))

                label = "/".join(counts)

            self.__label = "{} {}".format(self.__icon, label)

        except Exception as err:
            self.__label = err

    def click(self, event):
        for app in self.__apps:
            self.__clearAppCount(app)
        self.update()
        util.cli.execute(
            "i3-msg '[class=\"(?i){}\"] focus'".format(self.__i3FocusWindow),
            wait=False,
            shell=True,
        )

    def state(self, widget):
        state = []

        if self.__total > 0:
            state.append("warning")

        return state

    def __getAppCount(self, app):
        buffer = self.__getTmpFilePath(app)
        if os.path.isfile(buffer) and os.access(buffer, os.R_OK):
            return len(open(buffer).readlines())
        else:
            return 0

    def __clearAppCount(self, app):
        buffer = self.__getTmpFilePath(app)
        if os.path.isfile(buffer) and os.access(buffer, os.R_OK):
            file = open(buffer, "r+")
            file.truncate(0)
            file.close()

    def __getTmpFilePath(self, app):
        return Module.APP_TMP_PATH.format(app)


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
