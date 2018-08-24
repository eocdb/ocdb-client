class Api:
    def __init__(self, server_url: str = None):
        self.server_url = server_url

    def config(self, name, value):
        print('config name, value:', name, value)

    def query(self, expr):
        print('query expr:', expr)

    def add(self, file: str):
        print('add file:', file)

    def remove(self, id):
        print('remove id:', id)
