import numpy
import pandas as pd


class gre_list:
    def __init__(self, pref):

        self.wip_name = pref + '_wip.csv'
        self.rip_name = pref + '_rip.csv'
        self.words = pd.read_csv('./data/' + self.wip_name)
        self.words.reset_index(drop=True, inplace=True)
        self.words['learned'] = 0
        self.learned_words = pd.read_csv('./data/' + self.rip_name)
        self.n_serve = 0
        self.calc_prob()

    def calc_prob(self):
        self.words['serve_prob'] = self.words.wrong / (self.words.correct + self.words.wrong)
        self.words['serve_prob'] /= self.words.serve_prob.sum()
        self.words['cum_prob'] = self.words.serve_prob.cumsum()

    def serve(self):

        # Choose word to serve
        rand_num = numpy.random.rand()
        word_ind = numpy.where(self.words.cum_prob > rand_num)[0].min()

        print "Word: ", self.words.word[word_ind]
        response = raw_input("[S] Show meaning, [C] Mark Correct, [W] Mark Incorrect, [R] Mark Remembered, [E] Exit: ")
        while response not in ['S', 'C', 'W', 'R', 'E']:
            print 'Response should be in [S, C, W, R, E]. You entered ' + response + '. Please try again.'
            response = raw_input(
                "[S] Show meaning, [C] Mark Correct, [W] Mark Incorrect, [R] Mark Remembered, [E] Exit: ")

        if response == 'S':
            print "Meaning: ", self.words.meaning[word_ind]
            response = raw_input("[C] Mark Correct, [W] Mark Incorrect, [R] Mark Remembered, [E] Exit: ")
            while response not in ['C', 'W', 'R', 'E']:
                print 'Response should be in [C, W, R, E]. You entered ' + response + '. Please try again.'
                response = raw_input("[C] Mark Correct, [W] Mark Incorrect, [R] Mark Remembered, [E] Exit: ")

        if response == 'C':
            self.words.loc[word_ind, 'correct'] += 1.0

        if response == 'W':
            self.words.loc[word_ind, 'wrong'] += 1.0

        if response == 'R':
            self.learned_words = pd.concat((self.learned_words, self.words[word_ind:word_ind + 1][['word', 'meaning']]))
            self.words = self.words[self.words.word != self.words.word[word_ind]]
            self.words.reset_index(drop=True, inplace=True)

        self.calc_prob()

        if response == 'E' or self.n_serve % 10 == 0:
            self.words[['word', 'meaning', 'correct', 'wrong']].to_csv('./data/' + self.wip_name)
            self.learned_words[['word', 'meaning']].to_csv('./data/' + self.rip_name)

        self.n_serve += 1

        if response == 'E':
            return False

        else:
            return True


def restore(word_list='barrons'):
    wlist = pd.read_csv('data/%s.csv' % (word_list))
    wlist['correct'] = 1
    wlist['wrong'] = 1
    wlist.to_csv('data/%s_wip.csv' % (word_list))
    rip_list = pd.DataFrame(columns=['word', 'meaning'])
    rip_list.to_csv('data/%s_rip.csv' % (word_list))


def split(word_list='barrons', parts=20):
    wlist = pd.read_csv('data/%s.csv' % (word_list))
    for i, p in enumerate(numpy.array_split(wlist, parts)):
        p.to_csv('data/%s_%d.csv' % (word_list, i))
        restore('%s_%d' % (word_list, i))


def run(word_list='barrons'):
    gl = gre_list(word_list)
    ask_more = True
    while ask_more:
        ask_more = gl.serve()
