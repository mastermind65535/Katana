class RateLimit:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.limit = 0
        return cls._instance

    def getRate(self):
        return self.limit
    
    def setRate(self, rate:float):
        self.limit = float(rate)