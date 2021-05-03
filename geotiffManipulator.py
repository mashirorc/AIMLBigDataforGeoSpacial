from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import *
import webbrowser
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt
from skimage import exposure
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.collections import PatchCollection
import json
import import_tags
import mask
import math
import glob
import os
import cv2
from PIL import Image


class GeoTagger():
    def __init__(self, window):
        # initialize variables to be set in other methods
        self.geoFileName = None
        self.jsonFileName = None
        self.pngFileName = None
        self.img_rgb = None
        self.canvas = None
        self.fig = None
        self.ax = None
        self.pngCounter = 1
        self.connection_path = ''
        self.project_path = ''
        self.model_data_path = ''
        self.imported_tags = []
        # TODO num_images used for Config() in dynamic class use
        self.num_images = 0
        self.parsed_json = []
        self.generated_tag_info = []
        self.export_image = []

        # initialize the main window
        self.mainWindow = window
        self.mainWindow.title("GeoTagger")
        self.mainWindow.geometry("500x525")

        # Create Labels for Title and description
        self.titleLabel = Label(self.mainWindow, text='Welcome to GeoTagger', font=("Arial", 25))
        self.titleLabel.place(x=100, y=25)
        self.textLabel1 = Label(self.mainWindow,
                                text="Here you can view a GeoTIFF, export GeoTIFFs for use with VoTT, ")
        self.textLabel2 = Label(self.mainWindow, text="and render tags from VoTT. Click Import to get started.")
        self.textLabel1.place(x=100, y=75)
        self.textLabel2.place(x=125, y=100)

        # Vott buttons
        self.connection = Button(self.mainWindow, text='Connection', width=15, command=self.establish_connection)
        self.connection.place(x=25, y=125)
        self.connection_box = Entry(self.mainWindow, width=50, textvariable=self.connection_path)
        self.connection_box.place(x=175, y=128)

        self.project = Button(self.mainWindow, text='Project', width=15, command=self.establish_project)
        self.project.place(x=25, y=150)
        self.project_box = Entry(self.mainWindow, width=50, textvariable=self.project_path)
        self.project_box.place(x=175, y=153)

        self.model_data = Button(self.mainWindow, text='Model Data', width=15, command=self.establish_model_data)
        self.model_data.place(x=25, y=175)
        self.data_box = Entry(self.mainWindow, width=50, textvariable=self.model_data_path)
        self.data_box.place(x=175, y=178)

        # create an import button for importing a geotiff
        self.convertButton = Button(self.mainWindow, text='Import', width=15, command=self.open_geotiff)
        self.convertButton.place(x=25, y=210)

        # create button for importing tags
        self.import_tags_button = Button(self.mainWindow, text='Import Tags', width=15, command=self.process_tags)
        self.import_tags_button.place(x=175, y=210)

        # List box for choosing which labels to autotag
        self.label_list_box = Listbox(self.mainWindow, selectmode=MULTIPLE)
        self.label_list_box.place(x=325, y=210)

        # Button for training model
        self.model_train_button = Button(self.mainWindow, text='Train Model', width=15, command=self.train_model)
        self.model_train_button.place(x=25, y=245)

        # Button for predicting image
        self.predict_button = Button(self.mainWindow, text='Predict Image', width = 15, command=self.predict_image)
        self.predict_button.place(x=175, y=245)

        # Button for exporting to VoTT
        self.export_Vott = Button(self.mainWindow, text='Export Tags to VoTT', width=15, command=self.export_tags)
        self.export_Vott.place(x=25, y=280)

        # Creating Menu bar
        self.menubar = Menu(self.mainWindow)
        # Adding File Menu and commands
        self.fileMenuOption = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='File', menu=self.fileMenuOption)
        self.fileMenuOption.add_command(label='Open...', command=self.open_geotiff)
        # adding a help button
        # self.helpMenuOption = Menu(self.menubar, tearoff=0)
        # self.menubar.add_cascade(label='Help', menu=self.helpMenuOption, command=None)
        # self.mainWindow.config(menu=self.menubar)

        #create a label for info relating to the state of the app
        self.stateOfApp = StringVar()
        self.savedLabel = Label(self.mainWindow, textvariable=self.stateOfApp)
        self.savedLabel.pack(side=TOP, anchor = CENTER)
        # Creating Menu bar
        self.menubar = Menu(self.mainWindow)
        # Adding File Menu and commands
        self.fileMenuOption = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='File', menu=self.fileMenuOption)
        self.fileMenuOption.add_command(label='Open...', command=self.open_geotiff)
        self.mainWindow.config(menu=self.menubar)

    def establish_connection(self):
        self.connection_path = askdirectory()
        self.connection_box.insert(0, self.connection_path)

    def establish_project(self):
        self.project_path = askdirectory()
        self.project_box.insert(0, self.project_path)

    def establish_model_data(self):
        self.model_data_path = askdirectory()
        self.data_box.insert(0, self.model_data_path)

    def process_tags(self):
        if len(self.connection_path) == 0 or len(self.project_path) == 0 or len(self.model_data_path) == 0:
            print('load paths')
        else:
            self.label_list_box.delete(0, self.label_list_box.size() - 1)
            # print('accessing process')
            tag_processing = import_tags.Import_Tags(self.connection_path, self.project_path, self.model_data_path)
            tag_processing.parse_json(False)
            self.num_images = len(tag_processing.parsed_json)
            self.imported_tags.append(tag_processing.export_tags())
            self.parsed_json = tag_processing.parsed_json
            count = 1
            for item in self.imported_tags[-1]:
                self.label_list_box.insert(count, (item[0] + ' ' + str(item[1]) + ' images'))
                # print(self.label_list_box.get(0))
                count += 1

    def train_model(self):
        # print(self.label_list_box.curselection())
        if len(self.imported_tags) == 0:
            # TODO create popup box instead
            print('no data to train on')
        else:
            labels_selected = []
            image_count = 0
            selections = self.label_list_box.curselection()
            for item in selections:
                line_info = self.label_list_box.get(item)
                labels_selected.append(line_info.split()[0])
                image_count += int(line_info.split()[1])
            auto_train_model = mask.AutoTag()
            auto_train_model.load_dataset(self.parsed_json, self.connection_path, labels_selected,
                                          math.floor(image_count * 0.75), is_train=True)
            auto_train_model.prepare()

            auto_valid_model = mask.AutoTag()
            auto_valid_model.load_dataset(self.parsed_json, self.connection_path, labels_selected,
                                          math.floor(image_count * 0.75), is_train=False)
            auto_valid_model.prepare()
            autoConfig = mask.AutoTagConfig()
            # does not work after initialization
            # TODO create overloaded init class for config for dynamic class/steps use
            # autoConfig.NUM_CLASSES = len(labels_selected) + 1
            # autoConfig.STEPS_PER_EPOCH = self.num_images

            model = mask.mrcnn.model.MaskRCNN(mode='training',
                                         model_dir=self.model_data_path,
                                         config=autoConfig)

            model.load_weights(filepath='mask_rcnn_coco.h5',
                               by_name=True,
                               exclude=["mrcnn_class_logits", "mrcnn_bbox_fc", "mrcnn_bbox", "mrcnn_mask"])

            model.train(train_dataset=auto_train_model,
                        val_dataset=auto_valid_model,
                        learning_rate=0.01,
                        epochs=5,
                        layers='heads')

    def predict_image(self):
        image = askopenfilename()
        self.export_image.append(image)
        # print(image)
        # print(type(image))
        image = cv2.imread(image)
        predict_model = mask.mrcnn.model.MaskRCNN(mode='inference', config=mask.AutoTagConfig(),
                                      model_dir=self.model_data_path)

        # TODO needs to be a better more accurate way
        # https://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder
        most_recent_data = glob.glob(self.model_data_path + '/*')
        most_recent_folder = max(most_recent_data, key=os.path.getctime)
        most_recent_data = glob.glob(most_recent_folder + '/*')
        most_recent_h5 = max(most_recent_data, key=os.path.getctime)

        predict_model.load_weights(filepath=most_recent_h5, by_name=True)

        # TODO un-hardcode classes to dynamic version
        r = predict_model.detect([image])
        CLASS_NAMES = ['BG', 'Cloud']
        r = r[0]
        self.generated_tag_info.append(r)
        mask.mrcnn.visualize.display_instances(image=image,
                                          boxes=r['rois'],
                                          masks=r['masks'],
                                          class_ids=r['class_ids'],
                                          class_names=CLASS_NAMES,
                                          scores=r['scores'])

    def export_tags(self):
        r = self.generated_tag_info[-1]
        coords = r['rois']
        scores = r['scores']

        json_files = glob.glob(self.project_path + '/*.json')

        for file in json_files:
            f = open(file)
            json_f = json.load(f)
            f.close()
            if json_f['asset']['name'] == self.export_image[-1].split('/')[-1]:
                print('found corresponding json file')
                # y1, x1, y2, x2 = rois[x]
                for i in range(len(coords)):
                    # print(i)
                    # threshold for auto tagged boxes
                    # TODO have variable to accept the score threshold
                    if scores[i] > 0:
                        region_dict = {}
                        # TODO randomize id
                        region_dict["id"] = str(i)
                        region_dict['type'] = "RECTANGLE"
                        # TODO dynamically choose tags to automate
                        region_dict['tags'] = ["Cloud"]
                        region_dict['boundingBox'] = {}
                        region_dict['boundingBox']['height'] = float(coords[i][2] - coords[i][0])
                        region_dict['boundingBox']['width'] = float(coords[i][3] - coords[i][1])
                        region_dict['boundingBox']['left'] = float(coords[i][1])
                        region_dict['boundingBox']['top'] = float(coords[i][0])
                        region_dict['points'] = []
                        coord1 = {}
                        coord1['x'] = float(coords[i][1])
                        coord1['y'] = float(coords[i][0])
                        coord2 = {}
                        coord2['x'] = float(coords[i][3])
                        coord2['y'] = float(coords[i][2])
                        coord3 = {}
                        coord3['x'] = float(coords[i][1])
                        coord3['y'] = float(coords[i][0] + (coords[i][2] - coords[i][0]))
                        coord4 = {}
                        coord4['x'] = float(coords[i][1] + (coords[i][3] - coords[i][1]))
                        coord4['y'] = float(coords[i][0])

                        region_dict['points'].append(coord1)
                        region_dict['points'].append(coord2)
                        region_dict['points'].append(coord3)
                        region_dict['points'].append(coord4)

                        json_f['regions'].append(region_dict)
                # print(self.project_path + '/' + file)
                jsonTest = open(file, 'w')
                json.dump(json_f, jsonTest)
                jsonTest.close()
            else:
                print('didnt find')

    def open_geotiff(self):
        self.stateOfApp.set("")
        self.geoFileName = askopenfile(filetypes =[('GeoTIFF Files', '*.tif *.tiff')]).name
        #check that file opened
        if self.geoFileName is None:
            print("Error. File failed to open.")
            return
        self.convertButton.pack_forget()
        self.titleLabel.pack_forget()
        self.textLabel1.pack_forget()
        self.textLabel2.pack_forget()

        self.plot_geotiff()

        #Now we can make the option to export the item and tag with VoTT
        menuItemFound = 0
        for i in range(self.fileMenuOption.index('end')+1):
            if self.fileMenuOption.entrycget(i,'label') == 'Save as PNG...':
                menuItemFound = 1
        if menuItemFound != 1:
            self.fileMenuOption.add_command(label ='Save as PNG...', command = self.save_as_png)
        #once we have loaded an image, we can import tags
        menuItemFound = 0
        for i in range(self.fileMenuOption.index('end')+1):
            if self.fileMenuOption.entrycget(i,'label') == 'Render Tags...':
                menuItemFound = 1
        if menuItemFound != 1:
            self.fileMenuOption.add_command(label ='Render Tags...', command = self.open_json)

    def plot_geotiff(self):
        ds = gdal.Open(self.geoFileName)
        data = ds.ReadAsArray()
        # extract RGB bands
        tmp = data[3:0:-1,:,:] / data.max()
        # convert to 0-255 range
        img = np.array([])
        img = np.transpose((255. * tmp),(1,2,0)).astype(np.uint8)
        self.img_rgb = np.array([])
        self.img_rgb = img.copy()
        (x,y,z) = self.img_rgb.shape
        for i in range(0,z):
            #adjust for gamma and percentile
            self.img_rgb[:,:,i] =  self.contrast_enhance_band(img[:,:,i], percentile=(0.5, 99.5), gamma=0.7)
        #eliminate whitespace from the image
        self.fig = plt.figure(frameon=False)
        #make the image fill the entire figure
        self.ax = plt.Axes(self.fig, [0.,0.,1.,1.])
        self.ax.set_axis_off()
        self.fig.add_axes(self.ax)
        #scale it normally when loading the image
        image = self.ax.imshow(self.img_rgb) 

        if self.canvas and self.canvas.get_tk_widget().winfo_ismapped():
            self.canvas.get_tk_widget().forget()

        # creating the Tkinter canvas containing the Matplotlib figure
        self.canvas = FigureCanvasTkAgg(self.fig,master = self.mainWindow)  
        self.canvas.draw()
        # placing the canvas on the Tkinter window
        self.canvas.get_tk_widget().pack()

    #here we will convert to png and launch VoTT
    def save_as_png(self):
        self.stateOfApp.set("")
        filePath = self.geoFileName.rsplit("/", 1)[0] + '/'
        while(os.path.exists(filePath+"Figure_" + str(self.pngCounter) + ".png")):
            self.pngCounter += 1
        self.pngFileName = "Figure_" + str(self.pngCounter) + ".png"
        plt.imsave(filePath+self.pngFileName,self.img_rgb)
        self.stateOfApp.set("Geotiff saved as "+filePath+self.pngFileName+"\n You can now use VoTT to tag your image.")

    # here is where we process the tags
    def open_json(self):
        jsonFile = askopenfile(filetypes=[('JSON Files', '*.json')])
        self.jsonFileName = jsonFile.name
        if self.jsonFileName is None:
            print("Error. File failed to open.")
            return
        vott_info = json.load(jsonFile)
        self.getTags(vott_info)
        self.fileMenuOption.delete("Import Tags...")

    def getTags(self,vott_info):
        #make sure there is an asset in the vott dictionary
        if 'asset' not in vott_info:
            print("Error. JSON file does not contain an asset.")
            return
        else:
            #make sure there is a name in the vott dictionary
            if 'name' not in vott_info['asset']:
                print("Error. JSON file does not contain a name in asset.")
                return
            else:
                #make sure there is a region in the vott dictionary
                if 'regions' not in vott_info:
                    print("Error. JSON file does not contain an asset.")
                    return
                else:
                    tagList = []
                    #loop through the tags in the json
                    for tags in vott_info['regions']:
                        #make sure the tag has a name
                        if 'tags' not in tags:
                            print("Error. JSON file does not contain any tags.")
                            return
                        tagNames = tags['tags']
                        tagNamesAsString = ""
                        for names in tagNames:
                            tagNamesAsString += (str(names) + ", ")
                        tagNamesAsString = tagNamesAsString[:-2]
                        #make sure there are coordinate points in the json
                        if 'points' not in tags:
                            print("Error. JSON file does not contain any coordinate points for tags.")
                            return
                        coordinatePoints = []
                        #get the coordinate points of the polygon tags
                        for coordinates in tags['points']:
                            if "x" not in coordinates or "y" not in coordinates:
                                print("Error. JSON file does not contain any x or y value in coordinate points.")
                                return
                            coordinatePoints.append((coordinates["x"], coordinates["y"]))
                        #add a copy of the first coordinate to the end of the coordinates, as to close the polygon. 
                        if len(coordinatePoints) > 0:
                            coordinatePoints.append(coordinatePoints[0])
                        #add the tag to the list of tags.
                        tagList.append([tagNamesAsString,coordinatePoints])
                    self.renderTags(tagList)

    def renderTags(self, tagList):
        polygons = []
        for tag in tagList:
            polygons.append(patches.Polygon(tag[1], linewidth=1,edgecolor='r',facecolor='none'))
            #self.ax.add_patch(polygon)
            self.ax.annotate(tag[0], xy = tag[1][0], xytext=(tag[1][0][0]+2, tag[1][0][1]+2), color = 'r', fontsize=9, horizontalalignment='left', verticalalignment='bottom')
        #scale it normally when loading the image
        allTags = PatchCollection(polygons, match_original=True)
        self.ax.add_collection(allTags)

        #image = self.ax.imshow(self.img_rgb) 
        #self.canvas.draw()
        self.fig.canvas.draw()

    # Helper function for rendering the geotiffs (written by Peder)
    def contrast_enhance_band(self, x, percentile, gamma):
        """
        Gamma stretching and percentile stretching for more natural looking images.
        """
        plow, phigh = np.percentile(x, percentile)
        x = exposure.rescale_intensity(x, in_range=(plow, phigh))
        y = (x - x.min()) / (x.max() - x.min())
        y = y ** gamma
        img = (y * 255).astype(np.uint8)
        return (img)


if __name__ == "__main__":
    mainWindow = Tk()
    myWindow = GeoTagger(mainWindow)
    mainWindow.mainloop()