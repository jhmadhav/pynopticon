#    Pynopticon is a python object recognition framework using a bag of feature approach.
#    
#    Copyright (C) 2008  Thomas V. Wiecki
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import weakref
import copy

# set default to use lazy evaluation where possible
useLazyEvaluation=True
useTypeChecking=True
useCaching=True
verbosity=1
useOrange=True

def stripSlot(slot):
    import pickle
    slot.container.useLazyEvaluation=False
    slot.container.getDataAsIter()
    slot.container.generator = None
    slot.container.sequence = slot.container.data
    slot.container.references = None
    slot.seqIterator = None
    slot.bulkIterator = None
    slot.processFunc = None
    slot.processFuncs = None
    slot.inputSlot = None
    slot.outputType.conversions = None

def saveSlots(fname, outputSlot=None, outputSlots=None):
    import pickle

    # First, let every output slot process and save all the data
    # Also, remove all instancemethods
    try:
        fdescr = open(fname, mode='w')

        if outputSlot is not None:
            slot = copy.copy(outputSlot)
            stripSlot(slot)
            if verbosity > 0:
                print "Saving slot to %s" % fname
            pickle.dump(slot, fdescr)
            
        elif outputSlots is not None:
            raise NotImplementedError, "At the moment you can only pickle one slot at a time"
            for outputSlot in outputSlots:
                slot = copy.deepcopy(outputSlot)
                stripSlot(slot)
            pickle.dump(outputSlots, fdescr)
            
    finally:
        del fdescr

    
def loadSlots(fname):
    import pickle

    try:
        fdescr = open(fname, mode='r')
        if verbosity > 0:
            print "Loading slot from %s" % fname
        outputSlot = pickle.load(fdescr)
        outputSlot.container.references = weakref.WeakValueDictionary()
        
    finally:
        del fdescr

    return outputSlot
    
def applySettings(settingsList, widget, obj=None, kwargs=None, outputSlot=None, outputSlots=None):
    """Function to apply settings of a widget to a pynopticon module. The
    widget variables to apply to the module must have the same name
    and be listed in settingsList.

    You may specify outputSlot or outputSlots to test if
    useLazyEvaluation changed so that data can be computed and stored.
    """

    changed = False

    if obj is not None:
        for setting in settingsList:
            try:
                if getattr(obj, setting):
                    if getattr(widget, setting) != getattr(obj, setting):
                        setattr(obj, setting, getattr(widget, setting))
                        changed = True
            except AttributeError:
                pass

    if kwargs is not None:
        for setting in settingsList:
            if setting in kwargs:
                if kwargs[setting] != getattr(widget, setting):
                    kwargs[setting] = getattr(widget, setting)
                    changed = True

    # Check if outputSlots are provided
    if outputSlot is not None or outputSlots is not None:
        # Check if lazy evaluation was turned off
        if widget.useLazyEvaluation is False:
            if outputSlot is not None:
                outputSlots = [outputSlot]
            if outputSlots is not None:
                for slot in outputSlots:
                    # Turn off Lazy Evaluation
                    slot.useLazyEvaluation = False
                    slot.container.useLazyEvaluation = False
                    if verbosity>0:
                        print "Computing and storing data..."
                    # Compute data (if necessary)
                    slot.container.getDataAsIter()
            

    if changed:
        print "Changed"
        return True
        
    return False

def weakmethod(obj, methname):
    r = weakref.ref(obj)
    del obj
    def _weakmethod(*args, **kwargs):
        return getattr(r(), methname)(*args, **kwargs)
    return _weakmethod


# Dummy classes to use in Orange

class Descriptors(object):
    pass

class Codebook(object):
    pass

class Images(object):
    pass

class Labels(object):
    pass

class Histograms(object):
    pass

class Clusters(object):
    pass