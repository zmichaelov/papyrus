#!/usr/bin/env arch -i386 python


# This class is the main starting point for our application
# Initializes all of our GUI code

import wx, wx.richtext, wx.aui
import os.path, codecs
import scribe

defaultname = '[No Name]'

class MainWindow(wx.Frame):
    def __init__(self):
        super(MainWindow, self).__init__(None, size=(800, -1))
        # used as a temporary variable to store filenames, for files we are opening
        self.filename = defaultname
        self.dirname = '.'
        
        # to be appended to our file names
        self.extension = ".txt"
        
        # initialize GUI components
        self.CreateInteriorWindowComponents()
        self.CreateExteriorWindowComponents()
        #self.control.SetCursor(wx.StockCursor(wx.CURSOR_POINT_LEFT))
    
    def NewScribe(self):
        '''Creates a new RichTextCtrl with Scribe functionality'''
        control = wx.richtext.RichTextCtrl(self.notebook, style=wx.TE_MULTILINE)
        newscribe = scribe.Scribe(control)
        #control.Bind(wx.EVT_CHAR, newscribe.OnChar)
        return control

    def CreateInteriorWindowComponents(self):
        ''' Create "interior" window components. In this case it is just a
            simple multiline text control. '''
        self.panel = wx.Panel(self)

        self.notebook = wx.aui.AuiNotebook(self.panel)
        # create our RichTextCtrl as a child of the notebook
        # add our first page to the notebook
        self.notebook.AddPage(self.NewScribe(), defaultname)
        
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

        # add undo and redo and print

        toolbar.AddSimpleTool(804, wx.Bitmap('assets/img/cut.png'), 'Cut', 'Cut')
        toolbar.AddSimpleTool(805, wx.Bitmap('assets/img/page_full.png'), 'Copy', 'Copy')
        toolbar.AddSimpleTool(806, wx.Bitmap('assets/img/glyphicons_029_paste.png'), 'Paste', 'Paste')
        toolbar.AddSeparator()
        
        toolbar.AddSimpleTool(807, wx.Bitmap('assets/img/undo.png'), 'Undo', 'Undo')
        toolbar.AddSimpleTool(808, wx.Bitmap('assets/img/redo.png'), 'Redo', 'Redo')
        #toolbar.AddCheckTool(807, wx.Bitmap('assets/img/glyphicons_102_bold.png'))        
        #toolbar.AddCheckTool(808, wx.Bitmap('assets/img/glyphicons_101_italic.png'))
        #toolbar.AddCheckTool(809, wx.Bitmap('assets/img/glyphicons_103_text_underline.png'))
        
        # TODO: add left, center and right justified icons
        toolbar.Realize()
        
        self.Bind(wx.EVT_TOOL, self.OnNew , id=801)
        self.Bind(wx.EVT_TOOL, self.OnOpen, id=802)
        self.Bind(wx.EVT_TOOL, self.OnSave, id=803)
        self.Bind(wx.EVT_TOOL, self.OnCut,  id=804)
        self.Bind(wx.EVT_TOOL, self.OnCopy, id=805)
        self.Bind(wx.EVT_TOOL, self.OnPaste,id=806)
        #self.Bind(wx.EVT_TOOL, self.OnBold, id=807)

    def CreateMenu(self):
        fileMenu = wx.Menu()
        for id, label, helpText, handler in \
            [(wx.ID_NEW, '&New Window\tCtrl+N', 'New window', self.OnNew),
             (101, '&New Tab\tCtrl+T', 'New tab', self.OnNewTab),
             (wx.ID_ABOUT, '&About', 'Information about this program', self.OnAbout),
             (wx.ID_OPEN, '&Open\tCtrl+O', 'Open a new file', self.OnOpen),
             (wx.ID_SAVE, '&Save\tCtrl+S', 'Save the current file', self.OnSave),
             (wx.ID_SAVEAS, 'Save &As\tShift+Ctrl+S', 'Save the file under a different name', self.OnSaveAs),
             (None, None, None, None),
             (wx.ID_EXIT, 'E&xit', 'Terminate the program', self.OnExit)]:
            if id == None:
                fileMenu.AppendSeparator()
            else:
                item = fileMenu.Append(id, label, helpText)
                self.Bind(wx.EVT_MENU, handler, item)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, '&File') # Add the fileMenu to the MenuBar

        # Edit Menu
        editMenu = wx.Menu()
        for id, label, helpText, handler in \
            [(wx.ID_UNDO, '&Undo\tCtrl+Z', 'Undo the previous action', self.OnUndo),
             (wx.ID_REDO, '&Redo\tShift+Ctrl+Z', 'Redo the previous action', self.OnRedo),
             (None, None, None, None),
             (102, '&Close Tab\tCtrl+W', 'Close the current tab', self.OnCloseTab)]:
            if id == None:
                editMenu.AppendSeparator()
            else:
                item = editMenu.Append(id, label, helpText)
                self.Bind(wx.EVT_MENU, handler, item)

        menuBar.Append(editMenu, '&Edit')

        self.SetMenuBar(menuBar)  # Add the menuBar to the Frame

    def SetTitle(self):
        # MainWindow.SetTitle overrides wx.Frame.SetTitle, so we have to
        # call it using super:
        super(MainWindow, self).SetTitle('Papyrus')

    
    # Helper methods:
    
    def GetCurrentCtrl(self):
        '''Returns the RichTextCtrl of the currently active tab'''
        current = self.notebook.GetSelection()
        return self.notebook.GetPage(current)

    def defaultFileDialogOptions(self):
        ''' Return a dictionary with file dialog options that can be
            used in both the save file dialog as well as in the open
            file dialog. '''
        return dict(message='Choose a file', defaultDir=self.dirname,
                    wildcard='*'+self.extension)

    def askUserForFilename(self, **dialogOptions):
        dialog = wx.FileDialog(self, **dialogOptions)
        if dialog.ShowModal() == wx.ID_OK:
            userProvidedFilename = True

            self.filename = dialog.GetFilename()
            self.dirname = dialog.GetDirectory()

        else:
            userProvidedFilename = False
        dialog.Destroy()
        return userProvidedFilename

    # Event handlers:
    def OnNew(self, event):
        # TODO: add support for tabbed browsing
        frame = MainWindow()
        frame.Show()
    
    def OnNewTab(self, event):
        # add our new page to the notebook
        self.notebook.AddPage(self.NewScribe(), defaultname)

    def OnAbout(self, event):
        dialog = wx.MessageDialog(self, 'A text editor inspired by Google Scribe', 'About Papyrus Editor', wx.OK)
        dialog.ShowModal()
        dialog.Destroy()

    def OnExit(self, event):
        self.Close()  # Close the main window.

    def OnSave(self, event):
        current = self.notebook.GetSelection()
        filename = self.notebook.GetPageText(current)
        control = self.notebook.GetPage(current)
        if filename == defaultname:
            if self.askUserForFilename(defaultFile=filename, style=wx.SAVE, **self.defaultFileDialogOptions()):    
                # get the updated filename
                textfile = codecs.open(os.path.join(self.dirname, self.filename+self.extension), 'w', 'utf-8', 'strict')
                textfile.write(control.GetValue())
                textfile.close()
                #control.SaveFile(os.path.join(self.dirname, self.filename+self.extension))
                self.notebook.SetPageText(current, self.filename+self.extension)
        else:
            textfile = codecs.open(os.path.join(self.dirname, filename), 'w','utf-8', 'strict')
            textfile.write(control.GetValue())
            textfile.close()
            #control.SaveFile(os.path.join(self.dirname, filename))


    def OnOpen(self, event):
        if self.askUserForFilename(style=wx.OPEN,
                                   **self.defaultFileDialogOptions()):
            # check and see if we have a currently opened tab that has not been modified
            current = self.notebook.GetSelection()
            control = self.NewScribe()
            
            if self.GetCurrentCtrl().GetValue() == "" and self.notebook.GetPageText(current) == defaultname:
                control = self.GetCurrentCtrl() # use the existing page
            else:
                self.notebook.AddPage(control, self.filename) # add a new page

            textfile = open(os.path.join(self.dirname, self.filename), 'r')
            control.SetValue(textfile.read())
            textfile.close()

            
            current = self.notebook.GetSelection() # get the updated current tab
            self.notebook.SetPageText(current, self.filename) # give it the appropriate filename

            #control.LoadFile(os.path.join(self.dirname,self.filename))

    def OnSaveAs(self, event):
        current = self.notebook.GetSelection()
        filename = self.notebook.GetPageText(current)

        if self.askUserForFilename(defaultFile=filename, style=wx.SAVE,
                                   **self.defaultFileDialogOptions()):
            self.OnSave(event)

    def OnCut(self, event):
        control = self.GetCurrentCtrl()
        control.Cut()

    def OnCopy(self, event):
        control = self.GetCurrentCtrl()
        control.Copy()

    def OnPaste(self, event):
        control = self.GetCurrentCtrl()
        control.Paste()        

    def OnBold(self, event):
        control = self.GetCurrentCtrl()
        control.BeginBold()

    def OnUndo(self, event):
        pass
    def OnRedo(self, event):
        pass

    def OnCloseTab(self, event):
        count = self.notebook.GetPageCount()
        if count == 1:
            self.OnExit(event)
        elif count > 1:
            current = self.notebook.GetSelection()
            self.notebook.DeletePage(current) 

app = wx.App(redirect=False)
frame = MainWindow()
app.SetTopWindow(frame)
frame.Centre()
frame.Show()
app.MainLoop()
