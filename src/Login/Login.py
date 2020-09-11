class Login:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __call__(self, *args, **kwargs):
        return self.check()

    def check(self):
        if self.username == 'daveboy' and self.password == 'enigma':
            return "Ok"
        else:
            return "Not Ok"


