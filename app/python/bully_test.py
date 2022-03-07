import unittest

target = __import__("bully_logic.py")
logic = target.logic


class TestLogic(unittest.TestCase):
    
    
    def test_preamble(self):
        
        logic.preamble ()
        def getData(self):
            print "PRODUCTION getData called"
            return "Production code that gets data from server or data file"
        data = [1, 2, 3]
        result = sum(data)
        self.assertEqual(result, 6)


    def getData(self):
        print "PRODUCTION getData called"
        return "Production code that gets data from server or data file"

    def getDataLength(self):
        return len(self.getData())

class TestClassIWantToTest(unittest.TestCase):

    def testGetDataLength(self):
        def mockGetData(self):
            print "MOCK getData called"
            return "1234"

        origGetData = ClassIWantToTest.getData
        try:
            ClassIWantToTest.getData = mockGetData
            myObj = ClassIWantToTest()
            self.assertEqual(4, myObj.getDataLength())
        finally:
            ClassIWantToTest.getData = origGetData


if __name__ == '__main__':
    unittest.main()