#!/usr/bin/env arch -i386 python

import wx, wx.richtext
import os.path, string

class Mode:
    INSERT = 0
    COMPLETION = 1

# class to encapsulate all of our autocomplete logic
class Scribe:
        
    def __init__(self, text):
        self.dummy = ["apple", "boston", "car", "hello"]
        self.textArea = text
        self.mode = Mode.INSERT 
        
        self.COMMIT_ACTION = wx.WXK_TAB
           
    def IsArrowKey(self, code):
        return code == wx.WXK_LEFT or code == wx.WXK_RIGHT or code == wx.WXK_UP or code == wx.WXK_DOWN
    
    def CommitAction(self):
        start, end = self.textArea.GetSelection()
        if self.mode == Mode.COMPLETION:
            self.textArea.SetInsertionPoint(end)
            self.textArea.WriteText(" ")
            self.textArea.SetInsertionPoint(end + 1)
            self.mode = Mode.INSERT
        else:
            self.textArea.Replace(start, end, "\t")
    # finishes the completion task
    def RunCompletion(self, completion, pos):
        self.textArea.SetInsertionPoint(pos)
#         print completion, pos
        self.textArea.WriteText(completion)
        self.textArea.SetSelection(pos, pos + len(completion))
        self.textArea.MoveCaret(pos-1)
        self.mode = Mode.COMPLETION
    # just for testing
    def OnChar2(self, event):
        code = event.GetKeyCode()
        pos = self.textArea.GetInsertionPoint()
        print pos
        if code == wx.WXK_BACK:
            self.textArea.Remove(pos-1, pos)
            pos -= 1            
        else:        
            self.textArea.WriteText(chr(code))        
    # listen for single character insertions
    def OnChar(self, event):
        """Fired when a character is inserted"""
        code = event.GetKeyCode()
        if code == self.COMMIT_ACTION:
            self.CommitAction()
            return

        # clear the previous selection
        self.textArea.DeleteSelection()
        
        pos = self.textArea.GetInsertionPoint()        
        # self.textArea.WriteText(chr(code))

        if code == wx.WXK_BACK:
            self.textArea.Remove(pos-1, pos)
            return            
        else:        
            self.textArea.WriteText(chr(code))
            
        content = self.textArea.GetRange(0, pos+1)
        # Find where the word starts
        w = pos
        for char in reversed(content):
            if char not in string.letters:
                break
            w -= 1
        print w    
        prefix = content[w+1:].lower().strip()
        completion = ""
        for dum in self.dummy:
            if dum.startswith(prefix):    
                completion = dum[pos - w:].strip()
                self.RunCompletion(completion, pos + 1)
                return
        
        # if nothing found
        self.mode = Mode.INSERT
 
class MainWindow(wx.Frame):
    def __init__(self, filename='noname.txt'):
        super(MainWindow, self).__init__(None, size=(800,-1))
        self.filename = filename
        self.dirname = '.'
        self.CreateInteriorWindowComponents()
        self.CreateExteriorWindowComponents()
        self.scribe = Scribe(self.control)
        self.control.Bind(wx.EVT_CHAR, self.scribe.OnChar)
        
    def CreateInteriorWindowComponents(self):
        ''' Create "interior" window components. In this case it is just a
            simple multiline text control. '''
        self.control = wx.richtext.RichTextCtrl(self, style=wx.TE_MULTILINE)

    def CreateExteriorWindowComponents(self):
        ''' Create "exterior" window components, such as menu and status
            bar. '''
        self.CreateMenu()
        self.CreateStatusBar()
        self.SetTitle()

    def CreateMenu(self):
        fileMenu = wx.Menu()
        for id, label, helpText, handler in \
            [(wx.ID_ABOUT, '&About', 'Information about this program',
                self.OnAbout),
             (wx.ID_OPEN, '&Open', 'Open a new file', self.OnOpen),
             (wx.ID_SAVE, '&Save', 'Save the current file', self.OnSave),
             (wx.ID_SAVEAS, 'Save &As', 'Save the file under a different name',
                self.OnSaveAs),
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
        super(MainWindow, self).SetTitle('Editor %s'%self.filename)


    # Helper methods:

    def defaultFileDialogOptions(self):
        ''' Return a dictionary with file dialog options that can be
            used in both the save file dialog as well as in the open
            file dialog. '''
        return dict(message='Choose a file', defaultDir=self.dirname,
                    wildcard='*.*')

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

    def OnAbout(self, event):
        dialog = wx.MessageDialog(self, 'A text editor inspired by Google Scribe', 'About Papyrus Editor', wx.OK)
        dialog.ShowModal()
        dialog.Destroy()

    def OnExit(self, event):
        self.Close()  # Close the main window.

    def OnSave(self, event):
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

        
app = wx.App(redirect=False)
frame = MainWindow()
app.SetTopWindow(frame)
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
