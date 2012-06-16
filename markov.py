# module that generates random text using a word-based Markov model
import itertools,random

class Markov: 
    # k is the order of the markov model
    def __init__(self, k):
        self.k = k
        self.map = {}
    def __str__(self):
        return str(self.map)
    
    def add_sources(self, *files):
        [self.add_source(file) for file in files]        
        #[print (k + self.map[k]) for k in map.keys() if len(self.map[k]) > 5]
    # adds the specified file to the Markov map
    def add_source(self, filepath):
        data = open(filepath,'r')
        words = data.read().split()
        # add wrap-around for k-gram
        words.extend(words[0:self.k])
        
        for i in xrange(len(words)):
            # create order-k word Markov model as a tuple
            ngram = tuple(words[i:self.k+i])
            # get that key's list containing subsequent n-grams
            ngram_list = self.map.get(ngram, [])
            empty = False
            if len(ngram_list) == 0:
                empty = True
            ngram_list.append(tuple(words[i+1:(i+1)+self.k]))
            # update the key's value list
            if empty:
                self.map[ngram] = ngram_list
        # sort the keys
        self.map.keys().sort()
    # context is (are) the current character(s) being typed
    # this method retrieves the markov models best next word
    def getWord(self, context):
        # context is our previously entered word
        
        # find all keys that contain our context in some way
        seeds = [key for key in self.map.keys() if key.find(context) != -1]     
        
        # return the first value by default
        if len(seeds) > 0:
            return self.map[seed[0]]
        # if none are found, return one at random, (for now)
        seed = random.choice(self.map.keys())
        return self.map[seed
            
    # word count is the number of random words we want to generate
    def generate_text(self, word_count):
        string_builder = []
        # pick an initial key at random
        seed = random.choice(self.map.keys())
        #print seed
        for i in xrange(word_count):
            # get the values in for this key
            value = self.map[seed]
            #print value
            # pick a random entry from the list
            entry = random.choice(value)
            #print entry
            # append the last word in the tuple to our text list
            string_builder.append(entry[self.k-1])
            # set the current entry as our next seed
            seed = entry
            
        return ' '.join(string_builder)
        
        
            
        
