#!/usr/bin/env python
'''
Created on Jun 8, 2013

@author: Jonathan Harford

'''

import logging
logging.basicConfig(format='%(message)s', level=logging.DEBUG)

import os
import wx
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.expando import ExpandoTextCtrl

FONT_FLAGS = (10,
              wx.FONTFAMILY_TELETYPE,
              wx.FONTSTYLE_NORMAL,
              wx.FONTWEIGHT_NORMAL)

class MainWindow(wx.Frame):

    def __init__(self, parent, title, filenames, new_names):
        super(MainWindow,self).__init__(parent, title=title)
        self.init_layout()
        self.set_filenames(filenames, new_names)
        self.Centre()
        self.Show()

    def init_layout(self):

        mainpanel = ScrolledPanel(self, -1,
                                  # style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER,
                                  name="mainpanel")
        mainpanel.SetupScrolling()
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        mainpanel.SetSizer(mainsizer)

        field1 = ExpandoTextCtrl(mainpanel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        field1.SetFont(wx.Font(*FONT_FLAGS))
        field1.SetBackgroundColour('Light Grey')

        field2 = ExpandoTextCtrl(mainpanel, style=wx.TE_MULTILINE)
        field2.SetFont(wx.Font(*FONT_FLAGS))

        mainsizer.Add(field1, 1, wx.GROW)
        mainsizer.Add(field2, 1, wx.GROW)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKey)

        self.mainpanel = mainpanel
        self.mainsizer = mainsizer
        self.field1 = field1
        self.field2 = field2

    def set_filenames(self, filenames, new_names):

        def strip_textctrl(t):
            t.SetValue(t.GetValue().strip())  # Ugh. More elegant way?

        self.field1.SetDefaultStyle(wx.TextAttr("red"))
        for filename, new_name in zip(filenames,new_names):
            self.field1.AppendText(filename + "\n")
            self.field2.AppendText(new_name + "\n")
        strip_textctrl(self.field1)
        strip_textctrl(self.field2)

        self.filenames = filenames
        self.new_names = new_names

    def onKey(self, evt):
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self.OnClose(evt)
        else:
            evt.Skip()

    def OnClose(self, event):

        # If there's no changes, we can just close.
        if not self.field2.IsModified():
            self.Destroy()
            return

        dlg = wx.MessageDialog(self,
                               "Rename?",
                               "Confirm Renaming",
                               wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)

        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES:
            self.rename()
            self.Destroy()
        elif result == wx.ID_NO:
            logging.info("NOT RENAMING")
            self.Destroy()

    def update_new_names(self):
        self.new_names = self.field2.GetValue().split("\n")

    def rename(self):
        self.update_new_names()
        for oldname, newname in zip(self.filenames, self.new_names):
            if oldname <> newname:
                print oldname + " => " + newname
                os.rename(oldname, newname)

if __name__ == '__main__':
    app = wx.App(False)
    frame = MainWindow(None, 'weRenamer', os.listdir("."), os.listdir("."))
    app.MainLoop()

