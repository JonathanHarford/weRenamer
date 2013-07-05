#!/usr/bin/env python
'''
Created on Jun 8, 2013

@author: Jonathan Harford  

'''

import logging
logging.basicConfig(format='%(message)s', level=logging.DEBUG)

import os, os.path
import wx
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.expando import ExpandoTextCtrl

FONT_FLAGS = (10,
              wx.FONTFAMILY_TELETYPE,
              wx.FONTSTYLE_NORMAL,
              wx.FONTWEIGHT_NORMAL)

ICON_SIZE = (16, 16)

class RenameCmd(object):
    """A RenameCmd is a pair of strings describing an intended file renaming."""
    
    def __init__(self, filename):
        (self.oldname, self.oldext) = os.path.splitext(filename)   
        (self.newname, self.newext) = os.path.splitext(filename)
        if os.path.isdir(filename):
            self.filetype = "dir"
        elif filename.startswith("."):
            self.filetype = "hidden"
        else:
            self.filetype = "file"
        
    
    def __str__(self):
        return self.fulloldname + " => " + self.fullnewname + " (" + self.filetype + ")"
    
    @property
    def fulloldname(self):
        return self.oldname + self.oldext

    @property
    def fullnewname(self):
        return self.newname + self.newext

    def refresh(self, newfullname):
        (self.newname, self.newext) = os.path.splitext(newfullname)

    def execute(self):
        """Executes the renaming."""
        if self.ischanged():
            logging.info( str(self))
            os.rename(self.fulloldname, self.fullnewname)
        else:         
            logging.info(self.fulloldname + " unchanged.")
            
    def ischanged(self):
        return self.fulloldname <> self.fullnewname

class MainWindow(wx.Frame):
    
    def __init__(self, parent, title):
        
        super(MainWindow, self).__init__(parent, title=title)
        self.init_layout()    
        self.Centre()
        self.Show()

    def showdirs(self, evt):
        if self.btn_showdirs.IsToggled():
            logging.info("showdirs checked.")
        else:        
            logging.info("showdirs unchecked.")
        
    def init_layout(self):

        mainpanel = ScrolledPanel(self, -1)

        mainpanel.SetupScrolling()
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        mainpanel.SetSizer(mainsizer)

        toolbar = self.CreateToolBar(style=wx.TB_3DBUTTONS)
        
        ico_showdirs = wx.ArtProvider.GetBitmap(wx.ART_NEW_DIR, wx.ART_TOOLBAR, ICON_SIZE)
        self.btn_showdirs = toolbar.AddCheckLabelTool(wx.ID_ANY, "Toggle inclusion of directories", ico_showdirs, shortHelp="Show directories?")
        self.Bind(wx.EVT_TOOL, self.showdirs, self.btn_showdirs)

        ico_showexts = wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE, wx.ART_TOOLBAR, ICON_SIZE)
        self.btn_showexts = toolbar.AddCheckLabelTool(wx.ID_ANY, "Toggle inclusion of file extensions", ico_showexts, shortHelp="Show file extensions?")
        
        ico_showhids = wx.ArtProvider.GetBitmap(wx.ART_QUESTION, wx.ART_TOOLBAR, ICON_SIZE)
        self.btn_showhids = toolbar.AddCheckLabelTool(wx.ID_ANY, "Toggle inclusion of hidden files", ico_showhids, shortHelp="Show hidden files?")
        
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

    def init_renames(self, filenames):
        self.rename_cmds = [RenameCmd(filename) for filename in filenames]

    def load_renames_into_textctrls(self):

        def strip_textctrl(t):
            t.SetValue(t.GetValue().strip())  # Hm. More elegant way?
        
        for r in self.rename_cmds:
            self.field1.AppendText(r.fulloldname + "\n")
            self.field2.AppendText(r.fullnewname + "\n")
        strip_textctrl(self.field1)
        strip_textctrl(self.field2)        
        
    def refresh_renames(self):
        newnames = self.field2.GetValue().split("\n")
        for rename, newname in zip(self.rename_cmds, newnames):
            rename.refresh(newname)

    def onKey(self, evt):
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self.OnClose(evt)
        else:
            evt.Skip()

    def OnClose(self, event):
        
        ## If there's no changes, we can just close.
        
        if self.field1.GetValue() == self.field2.GetValue(): 
            self.Destroy()
            logging.info("Renaming canceled.")
            return

        dlg = wx.MessageDialog(self,
                               "RenameCmd?",
                               "Confirm Renaming",
                               wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
        
        result = dlg.ShowModal()
        
        dlg.Destroy()

        if result == wx.ID_YES:
            self.Destroy()
            self.refresh_renames()
            for r in self.rename_cmds:
                r.execute()
                
        elif result == wx.ID_NO:
            logging.info("Renaming canceled.")
            self.Destroy()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainWindow(None, 'weRenamer')
    frame.init_renames(os.listdir("."))
    frame.load_renames_into_textctrls()
    app.MainLoop()

