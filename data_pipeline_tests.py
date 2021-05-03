import unittest
from geotiffManipulator import *


class TestPipeLine(unittest.TestCase):
    # test assumes that corresponding json files have 7 tags
    def test_import_tags(self):
        mainWindow = Tk()
        myWindow = GeoTagger(mainWindow)
        # mainWindow.mainloop()
        myWindow.connection_path = 'C:\\Users\\Sophie\\Desktop\\School\\SeniorProject\\ProjectPresentation\\images'
        myWindow.project_path = 'C:\\Users\\Sophie\\Desktop\\School\\SeniorProject\\ProjectPresentation\\project'
        myWindow.model_data_path ='C:\\Users\\Sophie\\Desktop\\School\\SeniorProject\\ProjectPresentation\\data'
        myWindow.process_tags()

        print(myWindow.label_list_box.get(1))
        self.assertEqual(myWindow.label_list_box.get(0), 'Cloud 7 images')

    def test_import_num_images(self):
        mainWindow = Tk()
        myWindow = GeoTagger(mainWindow)
        # mainWindow.mainloop()
        myWindow.connection_path = 'C:\\Users\\Sophie\\Desktop\\School\\SeniorProject\\ProjectPresentation\\images'
        myWindow.project_path = 'C:\\Users\\Sophie\\Desktop\\School\\SeniorProject\\ProjectPresentation\\project'
        myWindow.model_data_path ='C:\\Users\\Sophie\\Desktop\\School\\SeniorProject\\ProjectPresentation\\data'
        myWindow.process_tags()

        self.assertEqual(myWindow.num_images, 5)


if __name__ == '__main__':
    unittest.main()