#!/usr/bin/env arch -i386 python


# This class is the main starting point for our application
# Initializes all of our GUI code

import wx, wx.richtext
import os.path
import scribe

class MainWindow(wx.Frame):
    def __init__(self, filename=''):
        super(MainWindow, self).__init__(None, size=(800,-1))
        self.filename = filename
        self.dirname = '.'
        self.CreateInteriorWindowComponents()
        self.CreateExteriorWindowComponents()
        self.scribe = scribe.Scribe(self.control)
        self.control.Bind(wx.EVT_CHAR, self.scribe.OnChar)
#         self.control.SetCursor(wx.StockCursor(wx.CURSOR_POINT_LEFT))
    def CreateInteriorWindowComponents(self):
        ''' Create "interior" window components. In this case it is just a
            simple multiline text control. '''
        self.control = wx.richtext.RichTextCtrl(self, style=wx.TE_MULTILINE)

    def CreateExteriorWindowComponents(self):
        ''' Create "exterior" window components, such as menu and status
            bar. '''
        self.CreateMenu()
        self.CreateToolbar()
        self.CreateStatusBar()
        self.SetTitle()
    
    def CreateToolbar(self):
        toolbar = self.CreateToolBar( wx.TB_HORIZONTAL | wx.NO_BORDER )
        toolbar.AddSimpleTool(801, wx.Bitmap('minimalistica/png/32x32/page.png'), 'New', '')
        toolbar.AddSimpleTool(802, wx.Bitmap('minimalistica/png/32x32/folder.png'), 'Open', 'Open an existing document')
        toolbar.AddSimpleTool(803, wx.Bitmap('minimalistica/png/32x32/save.png'), 'Save', 'Save the current document')
        toolbar.Realize()
        
        self.Bind(wx.EVT_TOOL, self.OnNew , id=801)
        self.Bind(wx.EVT_TOOL, self.OnOpen, id=802)
        self.Bind(wx.EVT_TOOL, self.OnSave, id=803)
    def CreateMenu(self):
        fileMenu = wx.Menu()
        for id, label, helpText, handler in \
            [(wx.ID_NEW, '&New', 'New document', self.OnNew),
             (wx.ID_ABOUT, '&About', 'Information about this program', self.OnAbout),
             (wx.ID_OPEN, '&Open', 'Open a new file', self.OnOpen),
             (wx.ID_SAVE, '&Save', 'Save the current file', self.OnSave),
             (wx.ID_SAVEAS, 'Save &As', 'Save the file under a different name', self.OnSaveAs),
             (None, None, None, None),
             (wx.ID_EXIT, 'E&xit', 'Terminate the program', self.OnExit)]:
            if id == None:
                fileMenu.AppendSeparator()
            else:
                item = fileMenu.Append(id, label, helpText)
                self.Bind(wx.EVT_MENU, handler, item)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, '&File') # Add the fileMenu to the MenuBar
        self.SetMenuBar(menuBar)  # Add the menuBar to the Frame

    def SetTitle(self):
        # MainWindow.SetTitle overrides wx.Frame.SetTitle, so we have to
        # call it using super:
        super(MainWindow, self).SetTitle('Papyrus %s'%self.filename)


    # Helper methods:

    def defaultFileDialogOptions(self):
        ''' Return a dictionary with file dialog options that can be
            used in both the save file dialog as well as in the open
            file dialog. '''
        return dict(message='Choose a file', defaultDir=self.dirname,
                    wildcard='*.pyr')

    def askUserForFilename(self, **dialogOptions):
        dialog = wx.FileDialog(self, **dialogOptions)
        if dialog.ShowModal() == wx.ID_OK:
            userProvidedFilename = True
            self.filename = dialog.GetFilename()
            self.dirname = dialog.GetDirectory()
            self.SetTitle() # Update the window title with the new filename
        else:
            userProvidedFilename = False
        dialog.Destroy()
        return userProvidedFilename

    # Event handlers:
    def OnNew(self, event):
        # TODO: add support for tabbed browsing
        frame = MainWindow()
        frame.Centre()
        frame.Show()
                
    def OnAbout(self, event):
        dialog = wx.MessageDialog(self, 'A text editor inspired by Google Scribe', 'About Papyrus Editor', wx.OK)
        dialog.ShowModal()
        dialog.Destroy()

    def OnExit(self, event):
        self.Close()  # Close the main window.

    def OnSave(self, event):
        if self.filename == "":
            if self.askUserForFilename(defaultFile=self.filename, style=wx.SAVE, **self.defaultFileDialogOptions()):    
                textfile = open(os.path.join(self.dirname, self.filename), 'w')
                textfile.write(self.control.GetValue())
                textfile.close()
        else:
            textfile = open(os.path.join(self.dirname, self.filename), 'w')
            textfile.write(self.control.GetValue())
            textfile.close()
    def OnOpen(self, event):
        if self.askUserForFilename(style=wx.OPEN,
                                   **self.defaultFileDialogOptions()):
            textfile = open(os.path.join(self.dirname, self.filename), 'r')
            self.control.SetValue(textfile.read())
            textfile.close()

    def OnSaveAs(self, event):
        if self.askUserForFilename(defaultFile=self.filename, style=wx.SAVE,
                                   **self.defaultFileDialogOptions()):
            self.OnSave(event)

    def OnCut(self, event):
        self.text.Cut()

    def OnCopy(self, event):
        self.text.Copy()

    def OnPaste(self, event):
        self.text.Paste()        

app = wx.App(redirect=False)
frame = MainWindow()
app.SetTopWindow(frame)
frame.Centre()
frame.Show(True)
app.MainLoop()

# class MyApp(wx.App):
#     def OnInit(self):
#         frame = MainWindow()
#         self.SetTopWindow(frame)
# 
#         print "Print statements go to this stdout window by default."
# 
#         frame.Show(True)
#         return True
#         
# app = MyApp(redirect=True)
# app.MainLoop()
