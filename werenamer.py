#!/usr/bin/env python
'''
Created on Jun 8, 2013

@author: Spielford

TODO:
* Set initial height/width to be 1/3 screen
* I use ExpandoTextCtrl instead of TextCtrl to keep scrollbars from appearing.
  Is there a way to do this with TextCtrls? 

'''

import logging
logging.basicConfig(format='%(message)s', level=logging.DEBUG)

import os
import sys
import string
import wx
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.expando import ExpandoTextCtrl

class MainWindow(wx.Frame):
    
    def __init__(self, parent, title):
        
        super(MainWindow,self).__init__(parent, title=title)
        
        self.init_layout()    
        self.Centre()
        self.Show()

    def init_layout(self):
        mainpanel = ScrolledPanel(self, -1,
                                  # style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER, 
                                  name="panel1")
        mainpanel.SetupScrolling()
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        mainpanel.SetSizer(mainsizer)
        mainpanel.SetAutoLayout(1)
        mainsizer.Fit(mainpanel)

        self.frozens = ExpandoTextCtrl(mainpanel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)
        self.control = ExpandoTextCtrl(mainpanel, style=wx.TE_MULTILINE | wx.TE_DONTWRAP)

        mainsizer.Add(self.frozens, 1, wx.GROW)
        mainsizer.Add(self.control, 1, wx.GROW)
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKey)

        self.mainpanel = mainpanel
        self.mainsizer = mainsizer

    def add_filenames(self, filenames):
        self.frozens.AppendText("\n".join(filenames))
        self.control.AppendText("\n".join(filenames))
            
    def onKey(self, evt):
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self.OnClose(evt)
        else:
            evt.Skip()

    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
                               "Rename?",
                               "Confirm Renaming", 
                               wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES:
            logging.info("RENAMING")
            self.Destroy()
        if result == wx.ID_NO:
            logging.info("NOT RENAMING")
            self.Destroy()


if __name__ == '__main__':

    app = wx.App(False)
    frame = MainWindow(None, 'weRenamer')
    frame.add_filenames(os.listdir("."))
    app.MainLoop()
    print("done")

