import random
import re
import sys

from PyQt4 import QtGui, QtCore


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
        # self.__dict__.update(kwargs)
        self.__dict__ = self
        # self.__getattr__ = dict.__getitem__
        # self.__getattribute__ = dict.__getitem__

    __getattr__ = dict.__getitem__

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)
        self.__dict__ = self

    def __str__(self):
        state = ["%s=%r" % (attribute, value)
                 for (attribute, value)
                 in self.__dict__.items()]
        return '\n'.join(state)

    def addItems(self, items):
        """

        :type items: dict
        """
        for i, v in items.items():
            self[i] = v

    def delItem(self, item):
        self.pop(item)


class Field(Standard):
    def __init__(self, window, w=10, h=10, mines=10):
        """

        :type window: Window
        :type w: int
        :type h: int
        :type mines: int
        """
        # Common field sizes and corresponding mine count, most typical have |> at the end of the line:
        # 9 x 9, 10 |>
        # 9 x 9, 35
        # 16 x 16, 40 |>
        # 16 x 16, 99
        # 30 x 16, 99 |>
        # 30 x 20, 145
        # 30 x 16, 170
        # These and in general all field size and mine-count options are stored in fieldOptions.txt
        self.__window = window
        self.__w = w
        self.__h = h
        self.__mines = mines
        self.__field = []  # field coordinates: 0 -> first
        self.__logData = None
        # init Field:
        self.generateField()

    def setDimensions(self, dimensionTuple):
        """

        :type dimensionTuple: tuple
        """
        if len(dimensionTuple) != 3:
            return None
        else:
            self.__w, self.__h, self.__mines = dimensionTuple

    def getDimensions(self):
        """

        :rtype: tuple(int, int, int)
        """
        return self.__w, self.__h, self.__mines

    def generateField(self, maxIter=5000):
        """

        :type maxIter: int
        """
        self.__field = []
        for i in range(self.__h):
            buf = []
            for j in range(self.__w):
                buf.append(FieldElem(self, Coordinate(j, i), "N", 0))
            self.__field.append(buf)
        #
        minesLeft = self.__mines
        minesPlaced = 0
        iterCount = 0
        area = self.__w * self.__h
        if minesLeft >= area:
            self.__window.messageBox.warning(self.__window, "Please Mind That", "This field cannot be generated fully. \
The application will try placing as many mines as possible though.", "Alright!")
        currL = 0
        currT = 0
        while minesLeft > 0 and maxIter >= 0:
            rand = random.random()
            quo = minesLeft / area
            if rand <= quo:
                selectedFieldElem = self.getFieldElem(Coordinate(currL, currT))
                adjacentFieldElems = selectedFieldElem.getAdjacent("array")
                if not self.checkWouldSurround(Coordinate(currL, currT), adjacent=adjacentFieldElems):
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
            fullStr="{} mines placed after {} iterations;\nthat's\t{} \
mines per iteration or\n\t\t{} iterations per mine.".format(minesPlaced, iterCount - 1,
                                                            minesPlaced / (iterCount - 1),
                                                            (iterCount - 1) / minesPlaced),
            minesPlaced=minesPlaced, iterCount=iterCount, minesPlacedPerIter=minesPlaced / (iterCount - 1),
            iterPerMinesPlaced=(iterCount - 1) / minesPlaced)

    def log(self):
        for i in range(self.__w + 2):
            print("# ", end="")
        print("")
        for i, v in enumerate(self.__field):
            print("# ", end="")
            for j, w in enumerate(v):
                print(str(w.getAttr("__fieldType")) + " ", end="")
            print("#")
        for i in range(self.__w + 2):
            print("# ", end="")
        print("")
        print(self.__logData.fullStr)

    def checkWouldSurround(self, coordinates, **kwargs):
        """

        :type coordinates: Coordinate
        :rtype: Boolean
        """
        adjacentFieldElems = None
        if "adjacent" in kwargs:
            adjacentFieldElems = kwargs["adjacent"]
        else:
            adjacentFieldElems = self.getFieldElem(coordinates).getAdjacent("array")
        for elem in adjacentFieldElems:
            if elem is not None:
                adjacent = elem.getAdjacent("array")
                numAdjacent = 0
                numAdjacentMines = 0
                for i in adjacent:
                    if i is not None:
                        numAdjacent += 1
                        if i.getAttr("__fieldType") == "M":
                            numAdjacentMines += 1
                if numAdjacent == numAdjacentMines + 1:
                    return True
        return False

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
                    # print("Caution! #1")
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
            adjacentFieldElems = [self.getNeighbour(coordinates, Coordinate(0, -1), autoAdjustMethod=False),
                                  self.getNeighbour(coordinates, Coordinate(1, -1), autoAdjustMethod=False),
                                  self.getNeighbour(coordinates, Coordinate(1, 0), autoAdjustMethod=False),
                                  self.getNeighbour(coordinates, Coordinate(1, 1), autoAdjustMethod=False),
                                  self.getNeighbour(coordinates, Coordinate(0, 1), autoAdjustMethod=False),
                                  self.getNeighbour(coordinates, Coordinate(-1, 1), autoAdjustMethod=False),
                                  self.getNeighbour(coordinates, Coordinate(-1, 0), autoAdjustMethod=False),
                                  self.getNeighbour(coordinates, Coordinate(-1, -1), autoAdjustMethod=False)]
        else:
            print("Error #3")
        return adjacentFieldElems


class Coordinate(Standard):
    def __init__(self, l=0, t=0):
        """

        :type l: int
        :type t: int
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
        :type value: int
        """
        # self.__fieldObj = fieldObj
        # self.__coordinates = coordinates
        # self.__fieldType = fieldElemType
        # self.__value = value
        # self.__hidden = True
        self.__bunch = Bunch(__fieldObj=fieldObj, __coordinates=coordinates, __fieldType=fieldElemType, __value=value,
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

    def getBunch(self):
        """

        :rtype Bunch
        """
        return self.__bunch

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
        return self.getAttr("__fieldObj").getAdjacent(self.getAttr("__coordinates"), returnType=returnType)


class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        #
        self.bunchOfInternalHandles = Bunch()
        #
        field = Field(self)
        self.bunchOfInternalHandles.addItems({"field": field})
        #
        self.resize(800, 480)
        self.center()
        self.setWindowTitle("Minesweeper")
        self.setWindowIcon(QtGui.QIcon("Minesweeper_Icon.png"))
        #
        self.statusBar()
        mainMenu = self.menuBar()
        #
        fileMenu = mainMenu.addMenu("File")
        #
        extractAction = QtGui.QAction("Quit", self)
        extractAction.setShortcut("Ctrl+Q")
        extractAction.setStatusTip("Quit Minesweeper")
        extractAction.triggered.connect(sys.exit)
        #
        fileMenu.addAction(extractAction)
        #
        self.fieldComboBox = QtGui.QComboBox(self)
        optFile = open("fieldOptions.txt")
        for i in optFile:
            if i[0] is not "#":
                search = re.compile("\d+ x \d+, \d+")  # regEx to search for a valid pattern
                result = re.search(search, i)  # applying this regEx
                split = re.compile("\D+")  # regEx used for extracting the 3 Integers from the string
                peaces = [int(j) for j in re.split(split, i) if j is not ""]  # applying this regEx and converting the \
                # values from String back to Integer
                if result is not None:
                    self.fieldComboBox.addItem(i[result.span()[0]:result.span()[1]] + " mines", peaces)
        optFile.close()
        self.fieldComboBox.addItem("Custom", "custom")
        self.fieldComboBox.move(10, 35)
        self.fieldComboBox.resize(QtGui.QComboBox.sizeHint(self.fieldComboBox))
        self.fieldComboBox.activated[str].connect(self.evFieldComboBox)
        #
        self.saveFieldOpts = QtGui.QPushButton("Save this custom field", self)
        self.saveFieldOpts.resize(self.saveFieldOpts.sizeHint())
        self.saveFieldOpts.move(20 + self.fieldComboBox.size().width(), 35)
        self.saveFieldOpts.setVisible(False)
        self.saveFieldOpts.clicked.connect(self.evSaveFieldOptsBtn)
        #
        self.prompt = QtGui.QInputDialog(self)
        self.messageBox = QtGui.QMessageBox(self)
        #
        self.show()

    def evSaveFieldOptsBtn(self):
        # check for last character in the file
        fieldOpts = open("fieldOptions.txt", "rb+")
        fieldOpts.seek(-1, 2)  # move read/write cursor
        lastChar = fieldOpts.read()
        fieldOpts.close()
        fieldOpts = open("fieldOptions.txt", "a")
        if lastChar != b'\n':  # determine if a new line is needed
            fieldOpts.write("\n")
        fieldOpts.write("{} x {}, {}".format(*self.bunchOfInternalHandles["field"].getDimensions()))

    def evFieldComboBox(self, text):
        itemData = self.fieldComboBox.itemData(self.fieldComboBox.currentIndex())
        if itemData == "custom":
            # TODO make the button-visibility smarter: let it only show if the current custom field is not yet saved
            self.saveFieldOpts.setVisible(True)
            #
            inputMade = []
            #
            widthPrompt = self.prompt.getInt(self, "Input", "Width:", 10, 1)
            if widthPrompt[1]:
                inputMade.append(widthPrompt[0])
            else:
                pass
                # TODO add a handle(?)
            #
            heightPrompt = self.prompt.getInt(self, "Input", "Height:", 10, 1)
            if heightPrompt[1]:
                inputMade.append(heightPrompt[0])
            else:
                pass
                # TODO add a handle(?)
            #
            minePrompt = self.prompt.getInt(self, "Input", "Mines:", 10, 1)
            if minePrompt[1]:
                inputMade.append(minePrompt[0])
            else:
                pass
                # TODO add a handle(?)
            print(inputMade)
            self.bunchOfInternalHandles["field"].setDimensions(tuple(inputMade))
            self.bunchOfInternalHandles["field"].generateField()
            self.bunchOfInternalHandles["field"].log()
        else:
            self.saveFieldOpts.setVisible(False)
            #
            print(text)
            print(itemData)
            self.bunchOfInternalHandles["field"].setDimensions(tuple(itemData))
            self.bunchOfInternalHandles["field"].generateField()
            self.bunchOfInternalHandles["field"].log()

    def center(self):
        frame = self.frameGeometry()
        centerPoint = QtGui.QDesktopWidget().availableGeometry().center()
        frame.moveCenter(centerPoint)
        self.move(frame.topLeft())


class Sort:
    def __new__(cls, listOfLists, prioList, *args, **kwargs):
        """

        :type listOfLists: list of lists
        :type prioList: list of int
        """
        out = listOfLists
        for i in range(1, len(prioList) + 1):
            sortIndex = prioList.index(i)
            print(i, sortIndex)
            nth = cls.nthItem(cls, sortIndex)
            test = True
            while test:
                test = False
                for j, v in enumerate(out):
                    buf = None
                    if j != 0:
                        if nth(v) < nth(out[j - 1]):
                            buf = out[j - 1]
                            out[j - 1] = out[j]
                            out[j] = buf
                            test = True
        return out

    def nthItem(self, n):
        return lambda a: a[n]


def main():
    app = QtGui.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
