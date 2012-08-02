# This module encapsulates all of our autocompletion logic
# It wraps all of the functionality around a wx.RichTextCtrl 

import wx, string
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
import json, urllib, re, logging

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
        
        # initialize our logging file
        logging.basicConfig(filename='papyrus.log',level=logging.DEBUG)
           
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
            if pos - 1 >= 0:
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
        cr_count = 0 # keeps track of whether there has been a carriage return
        for char in reversed(content):
            logging.debug("char:" + char)
            if (not first_space and char == " ") or char == '.':
                if cr_count == 0:
                    w += 1
                break
            if char == ' ':
                first_space = False
            if char == '\r' or char == '\n':
                first_space = False
                cr_count += 1
            w -= 1 
        logging.debug("pos - w:" + str(pos - w))      
        prefix = content[w+1:].lower().lstrip()

        # look only for letters (no punctuation, numbers, etc.)
        
        seed = re.findall(r'[a-zA-Z\']+', content)
        
        order = 3 # how many terms back we look
        new = ''
        logging.debug('prefix:' + prefix)
        if len(seed) < order or char == '.' or cr_count > 0:
            self.updateSuggestions(prefix)
        else:
            new = " ".join(seed[-order:]).lstrip()
            self.updateSuggestions(new)

        for suggestion in self.suggestions:

            i = suggestion.find(prefix)
            if i != -1:
                completion = suggestion[pos - w + i - cr_count:].rstrip() # only strip whitespace from the right side
                logging.debug("completion:" + completion)
                self.RunCompletion(completion, pos + 1)
                return
        # if nothing found
        self.mode = Mode.INSERT


    def handle_request(self, response):
        if response.error:
            logging.error("Error:", response.error)
        else:
            result = json.loads(response.body)
            logging.debug("result:" + str(result[1]))
            self.suggestions = result[1]
        IOLoop.instance().stop()


    def updateSuggestions(self, request_term):
        logging.debug("request_term:" + request_term)

        events = {'client' : 'firefox', 'q' : request_term.lower().strip() }
        request = urllib.urlencode(events)
        self.http_client.fetch(self.request_url + request, self.handle_request)
        IOLoop.instance().start()
