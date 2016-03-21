import random


class Standard(object):
    def __setitem__(self, key, value):
        setattr(self, key, value)
        return self[key]

    def __getitem__(self, item):
        return getattr(self, item, None)

    def setAttr(self, name, val):
        """

        :type name: String
        """
        return self.__setattr__(name, val)

    def getAttr(self, name):
        """

        :type name: String
        """
        return self.__getattribute__(name)


class Bunch(dict):
    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)
        self.__dict__.update(kwargs)

    def __str__(self):
        state = ["%s=%r" % (attribute, value)
                 for (attribute, value)
                 in self.__dict__.items()]
        return '\n'.join(state)

    __getattr__ = dict.__getitem__


class Field(Standard):
    def __init__(self, w=10, h=10, mines=10):
        """

        :type w: Integer
        :type h: Integer
        :type mines: Integer
        """
        # Common field sizes and corresponding mine count, most typical have |> at the end of the line:
        # 9 x 9, 10 |>
        # 9 x 9, 35
        # 16 x 16, 40 |>
        # 16 x 16, 99
        # 30 x 16, 99 |>
        # 30 x 20, 145
        # 30 x 16, 170
        self.__w = w
        self.__h = h
        self.__mines = mines
        self.__field = []  # field coordinates: 0 -> first
        self.__logData = None
        # init Field:
        for i in range(h):
            buf = []
            for j in range(w):
                buf.append(FieldElem(self, Coordinate(j, i), "N", 0))
            self.__field.append(buf)
        self.generateField()

    def generateField(self, maxIter=5000):
        """

        :type maxIter: Integer
        """
        minesLeft = self.__mines
        minesPlaced = 0
        iterCount = 0
        area = self.__w * self.__h
        if area > minesLeft:
            currL = 0
            currT = 0
            while minesLeft > 0 and maxIter >= 0:
                rand = random.random()
                quo = minesLeft / area
                if rand <= quo:
                    self.getFieldElem(Coordinate(currL, currT)).setAttr("__fieldType", "M")
                    minesLeft -= 1
                    minesPlaced += 1
                if currL < self.__w - 1:
                    currL += 1
                elif not (currL < self.__w - 1) and currT < self.__h - 1:
                    currL = 0
                    currT += 1
                else:
                    currL = 0
                    currT = 0
                maxIter -= 1
                iterCount += 1
            self.__logData = Bunch(
                fullStr="{} mines placed after {} iterations, \nthat's\t{} mines per iteration or \n\t\t{} iterations per mine.".format(
                    minesPlaced, iterCount - 1, minesPlaced / (iterCount - 1), (iterCount - 1) / minesPlaced),
                minesPlaced=minesPlaced, iterCount=iterCount, minesPlacedPerIter=minesPlaced / (iterCount - 1),
                iterPerMinesPlaced=(iterCount - 1) / minesPlaced)

    def log(self):
        for i in range(2 * self.__w + 3):
            print("#", end="")
        print("")
        for i, v in enumerate(self.__field):
            print("# ", end="")
            for j, w in enumerate(v):
                print(str(w.getAttr("__fieldType")) + " ", end="")
            print("#")
        for i in range(2 * self.__w + 3):
            print("#", end="")
        print("")
        print(self.__logData.fullStr)

    def getFieldElem(self, coordinates):
        """

        :type coordinates: Coordinate
        :rtype: FieldElem
        """
        if 0 <= coordinates.t <= self.__h - 1 and 0 <= coordinates.l <= self.__w - 1:
            return self.__field[coordinates.t][coordinates.l]
        else:
            return None

    def setFieldElem(self, coordinates, fieldElem):
        """

        :type coordinates: Coordinate
        :type fieldElem: FieldElem
        :rtype FieldElem or None
        """
        if 0 <= coordinates.t <= self.__h - 1 and 0 <= coordinates.l <= self.__w - 1:
            self.__field[coordinates.t][coordinates.l] = fieldElem
            return self.__field[coordinates.t][coordinates.l]
        else:
            return None

    def setFieldElemProperty(self, coordinates, property, val, create=False):
        """

        :type coordinates: Coordinate
        :type property: String
        :type create: Boolean
        """
        if 0 <= coordinates.t <= self.__h - 1 and 0 <= coordinates.l <= self.__w - 1:
            if not create:
                if hasattr(self.__field[coordinates.t][coordinates.l], property):
                    self.__field[coordinates.t][coordinates.l][property] = val
                else:
                    print("Error #4")
                    return None
            elif create:
                self.__field[coordinates.t][coordinates.l][property] = val
            else:
                print("Error #5")
                return None

    def getNeighbour_Down(self, ownCoordinates):
        """

        :type ownCoordinates: Coordinate
        :rtype FieldElem or None
        """
        if ownCoordinates.t + 1 <= self.__h - 1:
            return self.__field[ownCoordinates.t + 1][ownCoordinates.l]
        else:
            return None

    def getNeighbour_Up(self, ownCoordinates):
        """

        :type ownCoordinates: Coordinate
        :rtype FieldElem or None
        """
        if ownCoordinates.t - 1 >= 0:
            return self.__field[ownCoordinates.t - 1][ownCoordinates.l]
        else:
            return None

    def getNeighbour_Left(self, ownCoordinates):
        """

        :type ownCoordinates: Coordinate
        :rtype FieldElem or None
        """
        if ownCoordinates.l - 1 >= 0:
            return self.__field[ownCoordinates.t][ownCoordinates.l - 1]
        else:
            return None

    def getNeighbour_Right(self, ownCoordinates):
        """

        :type ownCoordinates: Coordinate
        :rtype FieldElem or None
        """
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
        """

        :type relCoordinates: Coordinate
        :type ownCoordinates: Coordinate
        :type method: String: "warp" or "walk"
        :type autoAdjustMethod: Boolean
        :rtype FieldElem
        """
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
        """

        :type coordinates: Coordinate
        :type returnType: String: "dict" or "array"
        :rtype dict of FieldElem or list of FieldElem
        """
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
        """

        :type l: Integer
        :type t: Integer
        """
        self.l = l
        self.t = t

    def log(self, **kwargs):
        print("<| l " + str(self.l) + ":t " + str(self.t) + " |>", **kwargs)


class FieldElem(Standard):
    def __init__(self, fieldObj, coordinates, fieldElemType, value):
        """

        :type fieldObj: Field
        :type coordinates: Coordinate
        :type fieldElemType: String: "M" or "N"
        :type value: Integer
        """
        # self.__fieldObj = fieldObj
        # self.__coordinates = coordinates
        # self.__fieldType = fieldElemType
        # self.__value = value
        # self.__hidden = True
        self.__bunch = Bunch(__fieldObj=fieldObj, __coorinates=coordinates, __fieldType=fieldElemType, __value=value,
                             __hidden=True)

    def setAttr(self, name, val):
        """

        :type name: String
        """
        self.__bunch[name] = val

    def getAttr(self, name):
        """

        :type name: String
        """
        return self.__bunch[name]

    def log(self, **kwargs):
        self.__bunch.__coordinates.log(**kwargs)

    def getNeighbour(self, relCoordinates=Coordinate()):
        """

        :type relCoordinates: Coordinate
        :rtype: list of FieldElem
        """
        return self.__bunch.__fieldObj.getNeighbour(self.__bunch.__coordinates, relCoordinates)

    def getAdjacent(self, returnType="dict"):
        """

        :type returnType: String: "dict" or "array"
        :rtype: dict of FieldElem or list of FieldElem
        """
        return self.__bunch.__fieldObj.getAdjacent(self.__bunch.__coordinates, returnType=returnType)


def main():
    field = Field(30, 16, 170)
    field.log()


if __name__ == '__main__':
    main()
