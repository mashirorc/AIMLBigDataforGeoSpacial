# this project follows the implementation of the Mask RCNN model seen here
# https://blog.paperspace.com/mask-r-cnn-in-tensorflow-2-0/

# mrcnn citation
# @misc{matterport_maskrcnn_2017,
#   title={Mask R-CNN for object detection and instance segmentation on Keras and TensorFlow},
#   author={Waleed Abdulla},
#   year={2017},
#   publisher={Github},
#   journal={GitHub repository},
#   howpublished={\url{https://github.com/matterport/Mask_RCNN}},
# }

from numpy import zeros, asarray
import mrcnn.utils
import mrcnn.config
import mrcnn.model
import mrcnn.visualize
import math
import warnings

warnings.filterwarnings('ignore')


# TODO add dynamic functionality, num_steps, steps_per_epoch input
class AutoTagConfig(mrcnn.config.Config):
    NAME = "auto_tag"
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    NUM_CLASSES = 2
    STEPS_PER_EPOCH = 4


class AutoTag(mrcnn.utils.Dataset):
    # image_info: Import_Tags().parsed_json
    # [(file_name, polygon_type, dimensions(width, height), boundary_coordinates, list_points, list_labels)]
    def load_dataset(self, image_info, img_path, class_labels, train_cutoff, is_train=True):
        # Background class is first class
        count = 1
        for item in class_labels:
            self.add_class("dataset", count, item)
            count += 1

        image_count = 0
        # each image has a list of bounding boxes ==
        # each Vott image has a list of tags
        for image in image_info:
            print(image)
            # file name, without file type
            image_id = image_count
            image_path = img_path + '\\' + image[0]
            width = image[1][0][1][0]
            height = image[1][0][1][1]
            boxes = image[1]
            box_info = []

            for image_boxes in boxes:
                image_count += 1
                if is_train and image_count >= train_cutoff:
                    continue

                if not is_train and image_count < train_cutoff:
                    continue

                # added to self.image_info of Dataset object as part of add_image(**kwargs), image_info.update(kwargs)
                xmin = math.floor(image_boxes[2][2])
                ymin = math.floor(image_boxes[2][3])
                xmax = math.floor(image_boxes[2][2]) + math.floor(image_boxes[2][1])
                ymax = math.floor(image_boxes[2][3]) + math.floor(image_boxes[2][0])
                # only grabs the first tag label, TODO
                image_class = image_boxes[4][0]
                box_info.append([xmin, ymin, xmax, ymax, image_class])

            if len(box_info) > 0:
                self.add_image('dataset', image_id=image_id, path=image_path, annotation=[box_info, width, height])

    def load_mask(self, image_id):
        info = self.image_info[image_id]
        box_info = info['annotation']
        boxes = box_info[0]
        w = box_info[1]
        h = box_info[2]
        masks = zeros([h, w, len(boxes)], dtype='uint8')

        class_ids = list()
        for i in range(len(boxes)):
            box = boxes[i]
            y_start, y_end = box[1], box[3]
            x_start, x_end = box[0], box[2]
            masks[y_start:y_end, x_start:x_end, i] = 1
            class_ids.append(self.class_names.index(box[4]))
        return masks, asarray(class_ids, dtype='int32')