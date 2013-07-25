#!/usr/bin/env python
'''
Created on Jun 8, 2013

@author: Jonathan Harford  

'''

import logging
logging.basicConfig(format='%(message)s', level=logging.DEBUG) ## use: logging.info("Message")

import os.path
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

class RenameCmds(list):

    def load_from_textctrls(self, field_n):
        newnames = field_n.GetValue().split("\n")
        for rename, newname in zip(self, newnames):
            rename.refresh(newname)

    def load_to_textctrls(self, field_o, field_n):
        field_o.Clear()
        field_n.Clear()
        
        field_o.AppendText(self.get_olds())
        field_n.AppendText(self.get_news())
    
        for bold_start, bold_end in self.get_bolds():
            field_n.SetStyle(bold_start, bold_end, wx.TextAttr("black", "white", wx.Font(*FONT_NEW)))
        

    def get_olds(self):
        return "\n".join([cmd.fulloldname for cmd in self])

    def get_news(self):
        return "\n".join([cmd.fullnewname for cmd in self])            

    def get_bolds(self):
        cur = 0
        bolds = []
        for cmd in self:
            if cmd.ischanged():
                bolds.append((cur, cur + len(cmd.fullnewname)))
                logging.info("Change: {} {}".format(cmd, bolds[-1]))
            cur = cur + len(cmd.fullnewname) + 1
        return bolds

class MainWindow(wx.Frame):
    
    def __init__(self, parent, title):
        
        super(MainWindow, self).__init__(parent, title=title)
        self.init_layout()    
        self.Centre()
        self.Show()
        
    def showdirs(self, evt):
        self.rename_cmds.load_from_textctrls(self.field_n)
        if self.btn_showdirs.IsToggled():
            logging.info("showdirs checked.")
        else:        
            logging.info("showdirs unchecked.")
        self.rename_cmds.load_to_textctrls(self.field_o, self.field_n)
        
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
        
        field_o = ExpandoTextCtrl(mainpanel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        field_o.SetFont(wx.Font(*FONT_OLD))
        field_o.SetBackgroundColour(wx.LIGHT_GREY)
        
        field_n = ExpandoTextCtrl(mainpanel, style=wx.TE_MULTILINE)
        field_n.SetFont(wx.Font(*FONT_OLD))

        mainsizer.Add(field_o, 1, wx.GROW)
        mainsizer.Add(field_n, 1, wx.GROW)
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKey)

        self.mainpanel = mainpanel
        self.toolbar = toolbar
        self.mainsizer = mainsizer
        self.field_o = field_o
        self.field_n = field_n

    def init_renamecmds(self, filenames):
        self.rename_cmds = RenameCmds([RenameCmd(filename) for filename in filenames])
        self.rename_cmds.load_to_textctrls(self.field_o, self.field_n)
        
    def sync(self):
        self.rename_cmds.load_from_textctrls(self.field_n)
        self.rename_cmds.load_to_textctrls(self.field_o, self.field_n)

    def onKey(self, evt):
        self.rename_cmds.load_from_textctrls(self.field_n)
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self.OnClose(evt)
        else:
            evt.Skip()
                        

    def OnClose(self, event):
        
        if self.field_o.GetValue() == self.field_n.GetValue(): 
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
            self.rename_cmds.load_from_textctrls(self.field_n)
            for r in self.rename_cmds:
                r.execute()
                
        elif result == wx.ID_NO:
            logging.info("Renaming canceled.")
            self.Destroy()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainWindow(None, 'weRenamer')
    frame.init_renamecmds(os.listdir("."))
    app.MainLoop()


