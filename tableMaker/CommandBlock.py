# CommandBlock.py
# Tarik Tosun
# University of Pennsylvania, September 2014
import pdb

class CommandBlock:
    def __init__(self):
        self.command_list = []
        self.triggers_list = []
        self.labels_list = []
        self.Ns = 0 # number of series blocks

    def __repr__(self):
        return self.make_table()

    def stitch(self, relativeBlock, firstTrigger='START', lastLabel='END'):
        ''' Stitches a RelativeBlock onto this CommandBlock with specified first
        trigger and last label. '''
        # Base case: relativeBlock is a raw command string
        if isinstance(relativeBlock, str):
            self.appendCommand(relativeBlock, firstTrigger, lastLabel)
        elif relativeBlock.type == 'series':
            self.stitchSeries(relativeBlock, firstTrigger, lastLabel)
        elif relativeBlock.type == 'parallel':
            self.stitchParallel(relativeBlock, firstTrigger, lastLabel)

    def stitchSeries(self, seriesBlock, firstTrigger, lastLabel):
        ''' Stitches a series block. The first element has trigger firstTrigger,
        the last element has label lastLabel, and everything in the middle is a
        linked list.'''
        blockName = str(self.Ns)+'-'
        self.Ns += 1
        N = len(seriesBlock.block_list)
        trigger = firstTrigger
        for (count, block) in enumerate(seriesBlock.block_list):
            if count == N-1: # we're processing the last block
                self.stitch(block, trigger, lastLabel)
                break
            label = blockName + str(count)
            self.stitch(block, trigger, label)
            trigger = label

    def stitchParallel(self, parallelBlock, firstTrigger, lastLabel):
        ''' Stitches a parallel block. Each element of a parallel block will have
        the same first trigger and last label. '''
        #blockName = 'p'+str(self.Np)+'-'
        #self.Np += 1
        for block in parallelBlock.block_list:
            self.stitch(block, firstTrigger, lastLabel)

    def appendCommand(self, command_string, trigger, label):
        ''' Appends the command string to this CommandBlock. '''
        self.command_list.append( command_string )
        self.triggers_list.append( trigger )
        self.labels_list.append( label )

    def make_table(self):
        ''' Returns the formatted table for this commandBlock. '''
        out = ''
        for i in xrange(0,len(self.command_list)):
            if self.triggers_list[i]==0: # hack so that first one won't have a trigger.
                out += self.command_list[i] + ' {' + str(self.labels_list[i]) + '} ;\n'
            else:
                out += self.command_list[i] + ' {{{}}} ({}) ;\n'.format(self.labels_list[i], self.triggers_list[i])
        return out

    def write(self, fname):
        ''' Writes out to file. '''
        tableString = self.make_table()
        f = open(fname, 'w')
        f.write(tableString)
        f.close()

