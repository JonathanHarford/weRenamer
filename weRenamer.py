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

ICON_SIZE = (16, 16)

class MainWindow(wx.Frame):
    
    def __init__(self, parent, title):
        
        super(MainWindow, self).__init__(parent, title=title)
        self.init_layout()    
        self.Centre()
        self.Show()

    def init_layout(self):

        mainpanel = ScrolledPanel(self, -1)

        mainpanel.SetupScrolling()
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        mainpanel.SetSizer(mainsizer)

        toolbar = self.CreateToolBar(style=wx.TB_3DBUTTONS)
        
        ico_showdirs = wx.ArtProvider.GetBitmap(wx.ART_NEW_DIR, wx.ART_TOOLBAR, ICON_SIZE)
        tool_showdirs = toolbar.AddCheckLabelTool(wx.ID_ANY, "Toggle inclusion of directories", ico_showdirs, shortHelp="Show directories?")
        # self.Bind(wx.EVT_TOOLBAR, self.showdirs, tool_showdirs)
        
        ico_showexts = wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE, wx.ART_TOOLBAR, ICON_SIZE)
        tool_showexts = toolbar.AddCheckLabelTool(wx.ID_ANY, "Toggle inclusion of file extensions", ico_showexts, shortHelp="Show file extensions?")
        
        ico_showhids = wx.ArtProvider.GetBitmap(wx.ART_QUESTION, wx.ART_TOOLBAR, ICON_SIZE)
        tool_showhids = toolbar.AddCheckLabelTool(wx.ID_ANY, "Toggle inclusion of hidden files", ico_showhids, shortHelp="Show hidden files?")
        
        toolbar.Realize()
        
        self.field1 = ExpandoTextCtrl(mainpanel, style=wx.TE_MULTILINE | wx.TE_DONTWRAP | wx.TE_READONLY)
        self.field1.SetFont(wx.Font(*FONT_FLAGS))
        self.field2 = ExpandoTextCtrl(mainpanel, style=wx.TE_MULTILINE | wx.TE_DONTWRAP)
        self.field2.SetFont(wx.Font(*FONT_FLAGS))

        mainsizer.Add(self.field1, 1, wx.GROW)
        mainsizer.Add(self.field2, 1, wx.GROW)
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKey)

        self.mainpanel = mainpanel
        self.toolbar = toolbar
        self.mainsizer = mainsizer

    def set_filenames(self, filenames, new_names):
            
        def strip_textctrl(t):
            t.SetValue(t.GetValue().strip())  # Ugh. More elegant way?
        
        for filename, new_name in zip(filenames, new_names):
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
        if self.field1.GetValue() == self.field2.GetValue(): 
            self.Destroy()
            return

        dlg = wx.MessageDialog(self,
                               "Rename?",
                               "Confirm Renaming",
                               wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
        
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES:
            self.Destroy()
            self.rename(self.field2.GetValue().split("\n"))
        elif result == wx.ID_NO:
            logging.info("NOT RENAMING")
            self.Destroy()

    def rename(self):
        for oldname, newname in zip(self.filenames, self.new_names):
            if oldname <> newname:
                print oldname + " => " + newname
                os.rename(oldname, newname)

if __name__ == '__main__':

    app = wx.App(False)
    frame = MainWindow(None, 'weRenamer')
    frame.set_filenames(os.listdir("."), os.listdir("."))
    app.MainLoop()

