# used for importing images into feature vectors
import cv2
# for local file processing
import os
import json


## This class holds all operations for importing the tfrecords from VoTT and parsing them for use
## Input: images_folder: string of the path to the images
## Input: export_folder: string of the path to the images
## Input: train_folder: string of path to the training images
## Info: project_folder contains JSON to parse
## Info: images_folder contains png corresponding to the pngs in the JSON
class Import_Tags:
    def __init__(self, images_folder, project_folder, train_folder):
        # path to images, input to VoTT project
        self.images = images_folder
        # path to exports of VoTT project
        self.project = project_folder
        self.train_folder = train_folder
        # labels for classification of images
        self.tags = []
        self.image_number = 0
        self.label_number = 0
        self.parsed_json = []

    def export_tags(self):
        return self.tags

    # retrieves the json information from the project_folder
    def parse_json(self, test=False):
        if test:
            print('obtaining info from ' + self.project)
            print('contains' + str(os.listdir(self.project)))

        tag_count = {}
        for doc in os.listdir(self.project):
            if doc.endswith('json'):
                if test:
                    print(doc)
                f = open(self.project + '\\' + doc)
                json_f = json.load(f)
                file_name = json_f['asset']['name']

                image_info = []

                for region in json_f['regions']:
                    # item: (height, width, left, top)
                    boundary = (region['boundingBox']['height'], region['boundingBox']['width'],
                                region['boundingBox']['left'], region['boundingBox']['top'])
                    points_list = []
                    for points in region['points']:
                        points_list.append((points['x'], points['y']))

                    label_list = []
                    for label in region['tags']:
                        label_list.append(label)
                        if tag_count.__contains__(label):
                            tag_count[label] = tag_count[label] + 1
                        else:
                            tag_count[label] = 1

                    dimensions = [json_f['asset']['size']['width'], json_f['asset']['size']['height']]

                    image_info.append((region['type'], dimensions, boundary, points_list, label_list))

                self.parsed_json.append((file_name, image_info))

                f.close()

        for item in tag_count:
            self.tags.append((item, tag_count[item]))

    def print_parsed(self):
        for item in self.parsed_json:
            print(item)
