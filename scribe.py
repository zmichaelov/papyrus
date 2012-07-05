# This module encapsulates all of our autocompletion logic
# It wraps all of the functionality around a wx.RichTextCtrl 

import wx, string
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
import json, urllib, re

# helper class to store editor states
class Mode:
    INSERT = 0
    COMPLETION = 1

# URLs that point to our autocompletion sources
urls = {
    "Bing"   : "http://api.bing.com/osjson.aspx?",
    "Google" : "http://suggestqueries.google.com/complete/search?"
}
#events = {'client' : 'chrome', 'q' : request_term.lower() }
#events = { 'query' : request_term.lower() }
# class to encapsulate all of our autocomplete logic
class Scribe:
        
    def __init__(self, text):
        self.suggestions = []
        self.textArea = text
        self.mode = Mode.INSERT 
        
        self.COMMIT_ACTION = wx.WXK_TAB

        self.http_client = AsyncHTTPClient()
        self.request_url = urls["Google"]#"http://suggestqueries.google.com/complete/search?"

           
    def IsArrowKey(self, code):
        return code == wx.WXK_LEFT or code == wx.WXK_RIGHT or code == wx.WXK_UP or code == wx.WXK_DOWN
    
    # commits the currently suggested autocomplete
    def CommitAction(self):
        start, end = self.textArea.GetSelection()
        if self.mode == Mode.COMPLETION:
            self.textArea.BeginBatchUndo("Commit Suggestion")
            self.textArea.SetInsertionPoint(end)
            self.textArea.WriteText(" ")
            self.textArea.SetInsertionPoint(end + 1)
            self.textArea.EndBatchUndo()
            self.mode = Mode.INSERT
        else:
            self.textArea.Replace(start, end, "\t")
    
    # updates proposed completions
    def RunCompletion(self, completion, pos):
        self.textArea.BeginBatchUndo("Update Suggestion")

        self.textArea.SetInsertionPoint(pos)
        self.textArea.WriteText(completion)
        self.textArea.SetSelection(pos, pos + len(completion))
        self.textArea.MoveCaret(pos-1)
        self.mode = Mode.COMPLETION
        
        self.textArea.EndBatchUndo()
           
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
        
        # adding default behavior back to the editor, namely delete functionality
        if code == wx.WXK_BACK:
            self.textArea.Remove(pos-1, pos)
            return
        elif code == wx.WXK_DELETE:
            self.textArea.Remove(pos, pos+1)
            return
        else:        
            self.textArea.WriteText(chr(code))
        
        content = self.textArea.GetRange(0, pos+1)
        # Find where the word starts, by working backwards from our current position
        w = pos
        first_space = True
        for char in reversed(content):
            if (char not in string.letters and char == " " and not first_space) or char == '.':
                break
            if char == " ":
                first_space = False
            w -= 1   
        prefix = content[w+1:].lower()

        # look only for letters (no punctuation, numbers, etc.)
        
        seed = re.findall(r'[a-zA-Z\']+', content)
        
        if len(seed) < 3 or char == '.':
            self.updateSuggestions(prefix)
        else:
            new = " ".join(seed[-3:])
            self.updateSuggestions(new)

        for suggestion in self.suggestions:
            i = suggestion.find(prefix)
            if i != -1:
                completion = suggestion[pos - w + i:].rstrip() # only strip whitespace from the right side
                self.RunCompletion(completion, pos + 1)
                return
        
        # if nothing found
        self.mode = Mode.INSERT


    def handle_request(self, response):
        if response.error:
            print "Error:", response.error
        else:
            result = json.loads(response.body)
            #print "result:\t" + str(result[1])
            self.suggestions = result[1]
        IOLoop.instance().stop()


    def updateSuggestions(self, request_term):
        #print "request_term:\t" + request_term
        events = {'client' : 'firefox', 'q' : request_term.lower() }
        request = urllib.urlencode(events)
        self.http_client.fetch(self.request_url + request, self.handle_request)
        IOLoop.instance().start()
