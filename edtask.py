#!/usr/bin/python

"""
__version__ = "$Revision: 1.3 $"
__date__ = "$Date: 2004/04/14 02:38:47 $"
"""

import sys, os, json
from PythonCard import model

def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, filename)

class MyBackground(model.Background):

    def on_close(self,evt):
        self.MakeModal(False)
        self.Destroy()

    def on_initialize(self, event):
        # if you have any initialization
        # including sizer setup, do it here
        pass

    def on_ok_command(self, event):
        self.callback()
        self.close()

    def on_cancel_command(self, event):
        self.close()

    def on_updateconfig_command(self, event):
        me = self.parent.components
        filename = find_data_file(self.parent.configfile)
        picmodel = me.picmodel.items[me.picmodel.selection]
        self.parent.config[picmodel] = self.components.blockCode.text
        f = open(filename, "wt")
        f.write(json.dumps(self.parent.config, sort_keys=True, indent=4, separators=(',', ': ')))
        f.close()



