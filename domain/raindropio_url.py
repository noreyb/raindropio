class RaindropIOUrl:
    def __init__(self):
        self.base = "https://api.raindrop.io/rest/v1"
        self.single = "/raindrop"
        self.bulk = "/raindrops"

    def get_single(self):
        return self.base + self.single

    def get_bulk(self):
        return self.base + self.bulk
