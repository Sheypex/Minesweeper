from argparse import ArgumentError


class Standard(object):
    def __setitem__(self, key, value):
        self[key] = value
        return self[key]

    def __getitem__(self, item):
        if hasattr(self, item):
            return self[item]
        else:
            print("Error #1")
            return None

    def getAttr(self, name):
        return self[name]

    def setAttr(self, name, val):
        self[name] = val
        return self[name]


class Field(Standard):
    def __init__(self, w=10, h=10, mines=10):
        self.__w = w
        self.__h = h
        self.__mines = mines
        self.__field = []  # field coordinates: 0 -> first
        # init Field:
        for i in range(w):
            buf = []
            for j in range(h):
                buf.append(FieldElem(self, Coordinate(j, i), None, None))
            self.__field.append(buf)

    def getFieldElem(self, coordinates):
        """

        :rtype: FieldElem
        """
        if 0 <= coordinates.t <= self.__h - 1 and 0 <= coordinates.l <= self.__w - 1:
            return self.__field[coordinates.t][coordinates.l]
        else:
            return None

    def setFieldElem(self, coordinates, val):
        if 0 <= coordinates.t <= self.__h - 1 and 0 <= coordinates.l <= self.__w - 1:
            self.__field[coordinates.t][coordinates.l] = val
            return self.__field[coordinates.t][coordinates.l]
        else:
            return None

    def setFieldElemProperty(self, coordinates, property, val, create=False):
        if 0 <= coordinates.t <= self.__h - 1 and 0 <= coordinates.l <= self.__w - 1:
            if not create:
                if hasattr(self.__field[coordinates.t][coordinates.l], property):
                    self.__field[coordinates.t][coordinates.l][property] = val
                else:
                    print("Error #4")
                    return None
            if create:
                self.__field[coordinates.t][coordinates.l][property] = val

    def getNeighbour_Down(self, ownCoordinates):
        if ownCoordinates.t + 1 <= self.__h - 1:
            return self.__field[ownCoordinates.t + 1][ownCoordinates.l]
        else:
            return None

    def getNeighbour_Up(self, ownCoordinates):
        if ownCoordinates.t - 1 >= 0:
            return self.__field[ownCoordinates.t - 1][ownCoordinates.l]
        else:
            return None

    def getNeighbour_Left(self, ownCoordinates):
        if ownCoordinates.l - 1 >= 0:
            return self.__field[ownCoordinates.t][ownCoordinates.l - 1]
        else:
            return None

    def getNeighbour_Right(self, ownCoordinates):
        if ownCoordinates.l + 1 <= self.__w - 1:
            return self.__field[ownCoordinates.t][ownCoordinates.l + 1]
        else:
            return None

    def getNeighbour(self, ownCoordinates, relCoordinates, method="warp", autoAdjustMethod=True):
        # method:
        #   "warp": tries to move (->"warp") to the given relative coordinates directly
        #   "walk": tries to move to the given relative coordinates while checking for bounds on every step
        # autoAdjustMethod:
        #   True: will opt for method="walk" if "warp" previously failed to return/find a fieldElem in the field
        #   False: will not do so and rather return None -> might be used to check if a fieldElem exists at a point \
        #          relative to a given one, not really useful though(?)
        if method == "walk":
            selectedFieldElem = self.getFieldElem(ownCoordinates)
            if relCoordinates.l != 0:
                if relCoordinates.l > 0:
                    # print("Going to the right")
                    for i in range(0, relCoordinates.l, 1):
                        neighbour = self.getNeighbour_Right(selectedFieldElem.getCoordinates())
                        if neighbour is not None:
                            selectedFieldElem = neighbour
                            # print("Got neighbour to the right", end="\t")
                            #     neighbour.getCoordinates().log()
                            # else:
                            # print("There is/was no neighbour to the right")
                elif relCoordinates.l < 0:
                    # print("Going to the left")
                    for i in range(0, relCoordinates.l, -1):
                        neighbour = self.getNeighbour_Left(selectedFieldElem.getCoordinates())
                        if neighbour is not None:
                            selectedFieldElem = neighbour
                            # print("Got neighbour to the left", end="\t")
                            #     neighbour.getCoordinates().log()
                            # else:
                            # print("There is/was no neighbour to the left")
            if relCoordinates.t != 0:
                if relCoordinates.t > 0:
                    # print("Going to the bottom")
                    for i in range(0, relCoordinates.t, 1):
                        neighbour = self.getNeighbour_Down(selectedFieldElem.getCoordinates())
                        if neighbour is not None:
                            selectedFieldElem = neighbour
                            # print("Got neighbour to the bottom", end="\t")
                            #     neighbour.getCoordinates().log()
                            # else:
                            # print("There is/was no neighbour to the bottom")
                elif relCoordinates.t < 0:
                    # print("Going to the top")
                    for i in range(0, relCoordinates.t, -1):
                        neighbour = self.getNeighbour_Up(selectedFieldElem.getCoordinates())
                        if neighbour is not None:
                            selectedFieldElem = neighbour
                            # print("Got neighbour to the top", end="\t")
                            # neighbour.getCoordinates().log()
                            # else:
                            # print("There is/was no neighbour to the top")
            return selectedFieldElem
        elif method == "warp":
            newCoordinates = Coordinate(ownCoordinates.l + relCoordinates.l, ownCoordinates.t + relCoordinates.t)
            if 0 <= newCoordinates.t <= self.__h - 1 and \
                                    0 <= newCoordinates.l <= self.__w - 1:
                return self.__field[newCoordinates.t][newCoordinates.l]
            else:
                if autoAdjustMethod:
                    return self.getNeighbour(ownCoordinates, relCoordinates, method="walk")
                else:
                    print("Caution! #1")
                    return None
        else:
            print("Error #2")
            return None

    def getAdjacent(self, coordinates, returnType="dict"):
        adjacentFieldElems = None
        if returnType == "dict":
            adjacentFieldElems = {"u": self.getNeighbour(coordinates, Coordinate(0, -1), autoAdjustMethod=False),
                                  "ur": self.getNeighbour(coordinates, Coordinate(1, -1), autoAdjustMethod=False),
                                  "r": self.getNeighbour(coordinates, Coordinate(1, 0), autoAdjustMethod=False),
                                  "br": self.getNeighbour(coordinates, Coordinate(1, 1), autoAdjustMethod=False),
                                  "b": self.getNeighbour(coordinates, Coordinate(0, 1), autoAdjustMethod=False),
                                  "bl": self.getNeighbour(coordinates, Coordinate(-1, 1), autoAdjustMethod=False),
                                  "l": self.getNeighbour(coordinates, Coordinate(-1, 0), autoAdjustMethod=False),
                                  "ul": self.getNeighbour(coordinates, Coordinate(-1, -1), autoAdjustMethod=False)}
        elif returnType == "array":
            adjacentFieldElems = []
            adjacentFieldElems.append(self.getNeighbour(coordinates, Coordinate(0, -1), autoAdjustMethod=False))
            adjacentFieldElems.append(self.getNeighbour(coordinates, Coordinate(1, -1), autoAdjustMethod=False))
            adjacentFieldElems.append(self.getNeighbour(coordinates, Coordinate(1, 0), autoAdjustMethod=False))
            adjacentFieldElems.append(self.getNeighbour(coordinates, Coordinate(1, 1), autoAdjustMethod=False))
            adjacentFieldElems.append(self.getNeighbour(coordinates, Coordinate(0, 1), autoAdjustMethod=False))
            adjacentFieldElems.append(self.getNeighbour(coordinates, Coordinate(-1, 1), autoAdjustMethod=False))
            adjacentFieldElems.append(self.getNeighbour(coordinates, Coordinate(-1, 0), autoAdjustMethod=False))
            adjacentFieldElems.append(self.getNeighbour(coordinates, Coordinate(-1, -1), autoAdjustMethod=False))
        else:
            print("Error #3")
        return adjacentFieldElems


class Coordinate(Standard):
    def __init__(self, l=0, t=0):
        self.l = l
        self.t = t

    def log(self, **kwargs):
        print("<| l " + str(self.l) + ":t " + str(self.t) + " |>", **kwargs)


class FieldElem(Standard):
    def __init__(self, fieldObj: Field, coordinates: Coordinate, fieldElemType, value):
        self.__fieldObj = fieldObj
        self.__coordinates = coordinates
        self.__fieldType = fieldElemType
        self.__value = value
        self.__hidden = True

    def getCoordinates(self):
        return self.__coordinates

    def log(self, **kwargs):
        self.__coordinates.log(**kwargs)

    def getNeighbour(self, relCoordinates=Coordinate()):
        return self.__fieldObj.getNeighbour(self.__coordinates, relCoordinates)

    def getAdjacent(self, returnType):
        return self.__fieldObj.getAdjacent(self.__coordinates, returnType=returnType)


def main():
    field = Field(16, 16, 40)
    field.setFieldElemProperty(Coordinate(0, 0), "test", "Ja", create=True)
    print("done")


if __name__ == '__main__':
    main()
