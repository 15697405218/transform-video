import logging
import wx

class TextCtrlHandler(logging.Handler):
    def __init__(self, ctrl):
        super(TextCtrlHandler, self).__init__()
        self.ctrl = ctrl

    def emit(self, record):
        msg = self.format(record)
        wx.CallAfter(self.ctrl.AppendText, msg + '\n')
