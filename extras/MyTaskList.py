from libqtile import widget


class MyTaskList(widget.TaskList):
    def __init__(self, **config):
        widget.TaskList.__init__(self, **config)
        self.add_defaults(widget.TaskList.defaults)
        self.add_callbacks({"Button3": self.close_window})

    def _configure(self, qtile, bar):
        widget.TaskList._configure(self, qtile, bar)

    def close_window(self):
        if self.clicked:
            window = self.clicked
            window.cmd_kill()
