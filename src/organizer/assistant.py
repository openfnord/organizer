#!/usr/bin/env python

'''Assistant.

This code receives file paths and suggests how to organize them.'''

import os.path
from organizer import destinations
from organizer import natures

class Subdir(object):

    memory = None
    nature_hint = None
    destination_hint = None
    user_supplied_datum = None

    def __repr__(self):
        return "<Subdir nat %s dest %s user %s>" % (
                                                   self.nature_hint,
                                                   self.destination_hint,
                                                   self.user_supplied_datum)
    def __init__(self, memory):
        self.memory = memory

    def set_nature_hint(self, h):
        self.nature_hint = h

    def set_destination_hint(self, h):
        self.destination_hint = h

    def set_user_supplied_datum(self, h):
        self.user_supplied_datum = h

    def persist_in_memory(self):
        if self.destination_hint:
            if self.user_supplied_datum:
                if self.user_supplied_datum == self.destination_hint:
                    self.memory.remember_associated_hint(self.destination_hint,
                                                         None)
                else:
                    self.memory.remember_associated_hint(self.destination_hint,
                                                         self.user_supplied_datum)
        if self.nature_hint:
            if self.user_supplied_datum:
                if self.user_supplied_datum == self.nature_hint:
                    self.memory.remember_associated_hint(self.nature_hint,
                                                         None)
                else:
                    self.memory.remember_associated_hint(self.nature_hint,
                                                         self.user_supplied_datum)

    def __str__(self):
        if self.user_supplied_datum:
            return self.user_supplied_datum
        if self.destination_hint:
            h = self.memory.recall_associated_hint(self.destination_hint)
            if h:
                return h
            return self.destination_hint
        if self.nature_hint:
            h = self.memory.recall_associated_hint(self.nature_hint)
            if h:
                return h
            return self.nature_hint
        return ""

class Assistant(object):
    """The Assistant assists the user in organizing files and directories."""

    memory = None
    path = None
    nature = None
    destination = None
    subdirs = None

    def __init__(self, memory, path):
        self.memory = memory
        self._path = path
        self.nature = natures.detect_nature(self._path)
        self.subdirs = []

    def begin(self):
        initial_dest = self.memory.recall_destination_for_nature(self.nature.__class__)
        self.change_destination(initial_dest)

    def change_destination(self, new_destination):
        if new_destination is not None:
            new_destination = destinations.Destination(new_destination)
        self.destination = new_destination
        self.recompute_subdirs()

    def recompute_subdirs(self):
        subdirs = self.subdirs[:]
        p = None
        naturehints = self.nature.subdir_hints()
        r = max((len(subdirs), len(naturehints)))
        for n in range(r):
            if n + 1 > len(subdirs):
                subdir = Subdir(self.memory)
                subdirs.append(subdir)
            else:
                subdir = subdirs[n]
            if n < len(naturehints):
                subdir.set_nature_hint(naturehints[n])
            else:
                subdir.set_nature_hint(None)
            if self.destination:
                destguess = self.destination.guess_best_hint(str(subdir), p)
                subdir.set_destination_hint(destguess)
            p = str(subdir) if p is None else os.path.join(p, str(subdir))
        self.subdirs = subdirs

    def change_subdir(self, subdir_number, new_subdir):
        subdirs = self.subdirs[:]
        while len(subdirs) < subdir_number:
            subdirs.append(Subdir(self.memory))
        subdirs[subdir_number].set_user_supplied_datum(new_subdir)
        self.subdirs = subdirs
        self.recompute_subdirs()

    def persist_in_memory(self):
        self.memory.remember_destination_for_nature(self.nature.__class__,
                                                    self.destination.path)
        for s in self.subdirs:
            s.persist_in_memory()

    @property
    def final_path(self):
        if not self.destination:
            return None
        p = [self.destination.path] + [ str(s) for s in self.subdirs ] + [os.path.basename(self._path)]
        return os.path.join(*p)