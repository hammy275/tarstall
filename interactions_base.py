from abc import ABC, abstractmethod

class Interactions(ABC):
    @abstractmethod
    def ask(self, question):
        pass

    @abstractmethod
    def get_input(self, question, options, default, gui_labels=None, from_easy=False):
        pass

    @abstractmethod
    def pprint(self, st, title="tarstall-gui"):
        pass

    @abstractmethod
    def ppause(self, st, title="tarstall-gui"):
        pass

    @abstractmethod
    def progress(self, val, should_show=True):
        pass
