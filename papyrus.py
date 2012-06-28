#!/usr/bin/env arch -i386 python


# This class is the main starting point for our application
# Initializes all of our GUI code

import wx, wx.richtext
import os.path
import scribe

class MainWindow(wx.Frame):
    def __init__(self):
        super(MainWindow, self).__init__(None, size=(800,-1))
        # used as a temporary variable to store filenames, for files we are opening
        self.filename = '[No Name]'
        self.dirname = '.'
        
        # to be appended to our file names
        self.extension = ".txt"
        
        # initialize GUI components
        self.CreateInteriorWindowComponents()
        self.CreateExteriorWindowComponents()
        #self.control.SetCursor(wx.StockCursor(wx.CURSOR_POINT_LEFT))
    def CreateInteriorWindowComponents(self):
        ''' Create "interior" window components. In this case it is just a
            simple multiline text control. '''
        self.panel = wx.Panel(self)

        self.notebook = wx.Notebook(self.panel)
        #self.control = wx.richtext.RichTextCtrl(self, style=wx.TE_MULTILINE)
        # create our RichTextCtrl as a child of the notebook
        control = wx.richtext.RichTextCtrl(self.notebook, style=wx.TE_MULTILINE)
        myscribe = scribe.Scribe(control)
        control.Bind(wx.EVT_CHAR, myscribe.OnChar)
        # add our first page to the notebook
        self.notebook.AddPage(control, "[No Name]")
        
        # adjust sizing parameters
        sizer = wx.BoxSizer()
        sizer.Add(self.notebook, 1, wx.EXPAND)
        self.panel.SetSizer(sizer)

    def CreateExteriorWindowComponents(self):
        ''' Create "exterior" window components, such as menu and status
            bar. '''
        self.CreateMenu()
        self.CreateToolbar()
        self.CreateStatusBar()
        self.SetTitle()
    
    def CreateToolbar(self):
        toolbar = self.CreateToolBar( wx.TB_HORIZONTAL | wx.NO_BORDER )
        toolbar.AddSimpleTool(801, wx.Bitmap('assets/img/page.png'), 'New', 'Create a new document')
        toolbar.AddSimpleTool(802, wx.Bitmap('assets/img/folder.png'), 'Open', 'Open an existing document')
        toolbar.AddSimpleTool(803, wx.Bitmap('assets/img/save.png'), 'Save', 'Save the current document')
        toolbar.AddSeparator()

        toolbar.AddSimpleTool(804, wx.Bitmap('assets/img/cut.png'), 'Cut', 'Cut')
        toolbar.AddSimpleTool(805, wx.Bitmap('assets/img/page_full.png'), 'Copy', 'Copy')
        toolbar.AddSimpleTool(806, wx.Bitmap('assets/img/package.png'), 'Paste', 'Paste')

        toolbar.Realize()
        
        self.Bind(wx.EVT_TOOL, self.OnNew , id=801)
        self.Bind(wx.EVT_TOOL, self.OnOpen, id=802)
        self.Bind(wx.EVT_TOOL, self.OnSave, id=803)
        self.Bind(wx.EVT_TOOL, self.OnCut,  id=804)
        self.Bind(wx.EVT_TOOL, self.OnCopy, id=805)
        self.Bind(wx.EVT_TOOL, self.OnPaste,id=806)

    def CreateMenu(self):
        fileMenu = wx.Menu()
        for id, label, helpText, handler in \
            [(wx.ID_NEW, '&New', 'New window', self.OnNew),
             (wx.ID_NEW, '&New Tab', 'New tab', self.OnNewTab),
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
        super(MainWindow, self).SetTitle('Papyrus')


    # Helper methods:

    def defaultFileDialogOptions(self):
        ''' Return a dictionary with file dialog options that can be
            used in both the save file dialog as well as in the open
            file dialog. '''
        return dict(message='Choose a file', defaultDir=self.dirname,
                    wildcard='*.txt')

    def askUserForFilename(self, **dialogOptions):
        dialog = wx.FileDialog(self, **dialogOptions)
        if dialog.ShowModal() == wx.ID_OK:
            userProvidedFilename = True

            #current = self.notebook.GetSelection()
            #self.notebook.SetPageText(current, dialog.GetFilename())
            self.filename = dialog.GetFilename()+self.extension
            self.dirname = dialog.GetDirectory()

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
    
    def OnNewTab(self, event):
        control = wx.richtext.RichTextCtrl(self.notebook, style=wx.TE_MULTILINE)
        myscribe = scribe.Scribe(control)
        control.Bind(wx.EVT_CHAR, myscribe.OnChar)
        # add our new page to the notebook
        self.notebook.AddPage(control, "[No Name]")

    def OnAbout(self, event):
        dialog = wx.MessageDialog(self, 'A text editor inspired by Google Scribe', 'About Papyrus Editor', wx.OK)
        dialog.ShowModal()
        dialog.Destroy()

    def OnExit(self, event):
        self.Close()  # Close the main window.

    def OnSave(self, event):
        control = self.notebook.GetCurrentPage()
        current = self.notebook.GetSelection()
        filename = self.notebook.GetPageText(current)
        if filename == "[No Name]":
            if self.askUserForFilename(defaultFile=filename, style=wx.SAVE, **self.defaultFileDialogOptions()):    
                # get the updated filename
                textfile = open(os.path.join(self.dirname, self.filename), 'w')
                textfile.write(control.GetValue())
                textfile.close()

                self.notebook.SetPageText(current, self.filename)
        else:
            textfile = open(os.path.join(self.dirname, filename), 'w')
            textfile.write(control.GetValue())
            textfile.close()

    def OnOpen(self, event):
        if self.askUserForFilename(style=wx.OPEN,
                                   **self.defaultFileDialogOptions()):

            control = wx.richtext.RichTextCtrl(self.notebook, style=wx.TE_MULTILINE)
            myscribe = scribe.Scribe(control)
            control.Bind(wx.EVT_CHAR, myscribe.OnChar)
            # add our first page to the notebook
            self.notebook.AddPage(control, self.filename)

            #filename = self.notebook.GetPageText(current)
                       
            textfile = open(os.path.join(self.dirname, self.filename), 'r')
            control.SetValue(textfile.read())
            textfile.close()

    def OnSaveAs(self, event):
        current = self.notebook.GetSelection()
        filename = self.notebook.GetPageText(current)

        if self.askUserForFilename(defaultFile=filename, style=wx.SAVE,
                                   **self.defaultFileDialogOptions()):
            self.OnSave(event)

    def OnCut(self, event):
        self.control.Cut()

    def OnCopy(self, event):
        self.control.Copy()

    def OnPaste(self, event):
        self.control.Paste()        

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
