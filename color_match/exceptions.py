class UndefinedSpace(Exception):

    def init(self, space_name, message=""):
        self.space_name = space_name
        self.message = message
        super().init(self.message)
        
    def str(self):
        msg ="Space {} is not among the available color space types."
        return self.message + msg