# todo: this probably isn't a very pythonic way to do this
class Observable:
    def __init__(self):
        self.observers = {}

    def observe(self, event, observer):
        existing = self.observers.get(event, None)
        if existing:
            existing.append(observer)
        else:
            self.observers[event] = [observer]

    def emit(self, event):
        if event in self.observers:
            for observer in self.observers[event]:
                observer()

