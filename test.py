class Polygon:
    def __init__(self, sides):
        self.sides = sides

    def area(self):
        return 10

class Triangle(Polygon):
    def __init__(self):
        Polygon.__init__(self, 3)

    def area2(self):
        self.area()

t = Triangle()
print t.area()
