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

FONT_OLD = (10,
              wx.TELETYPE,
              wx.NORMAL,
              wx.NORMAL)

FONT_NEW= (10,
              wx.TELETYPE,
              wx.NORMAL,
              wx.BOLD)

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
        return '''{}: "{}" => "{}"'''.format(self.filetype, self.fulloldname, self.fullnewname)
    
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
        self.load_textctrls_into_renamecmds()
        if self.btn_showdirs.IsToggled():
            logging.info("showdirs checked.")
        else:        
            logging.info("showdirs unchecked.")
        self.load_renamecmds_into_textctrls()
        
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
        
        field1 = ExpandoTextCtrl(mainpanel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        field1.SetFont(wx.Font(*FONT_OLD))
        field1.SetBackgroundColour(wx.LIGHT_GREY)
        
        field2 = ExpandoTextCtrl(mainpanel, style=wx.TE_MULTILINE)
        field2.SetFont(wx.Font(*FONT_OLD))

        mainsizer.Add(field1, 1, wx.GROW)
        mainsizer.Add(field2, 1, wx.GROW)
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKey)

        self.mainpanel = mainpanel
        self.toolbar = toolbar
        self.mainsizer = mainsizer
        self.field1 = field1
        self.field2 = field2

    def init_renamecmds(self, filenames):
        self.rename_cmds = [RenameCmd(filename) for filename in filenames]
        
    def load_renamecmds_into_textctrls(self):

        def strip_textctrl(t):
            t.SetValue(t.GetValue().strip())  # Hm. More elegant way?
            
        self.field1.Clear()
        self.field2.Clear()
        bold_starts = []
        bold_ends = []
        
        for r in self.rename_cmds:
            
            self.field1.AppendText(r.fulloldname + "\n")
            
            if r.ischanged(): bold_starts.append(self.field2.InsertionPoint)
            self.field2.AppendText(r.fullnewname + "\n")
            if r.ischanged(): bold_ends.append(self.field2.InsertionPoint)
            
        strip_textctrl(self.field1)
        strip_textctrl(self.field2)
        for bold_start, bold_end in zip(bold_starts,bold_ends):
            self.field2.SetStyle(bold_start, bold_end, wx.TextAttr("black", "white", wx.Font(*FONT_NEW)))
 
        
    def load_textctrls_into_renamecmds(self):
        newnames = self.field2.GetValue().split("\n")
        for rename, newname in zip(self.rename_cmds, newnames):
            rename.refresh(newname)

    def onKey(self, evt):
        self.load_textctrls_into_renamecmds()
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self.OnClose(evt)
        else:
            evt.Skip()
                        

    def OnClose(self, event):
        
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
            self.load_textctrls_into_renamecmds()
            for r in self.rename_cmds:
                r.execute()
                
        elif result == wx.ID_NO:
            logging.info("Renaming canceled.")
            self.Destroy()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainWindow(None, 'weRenamer')
    frame.init_renamecmds(os.listdir("."))
    frame.load_renamecmds_into_textctrls()
    app.MainLoop()


