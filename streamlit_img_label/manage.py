import os
import re
import numpy as np
from PIL import Image
from annotation import output_xml, read_xml

class ImageManager:

    def __init__(self, filename):
        self._filename = filename
        self._img = Image.open(filename)
        self._rects = []
        self._load_rects()
        self._resized_ratio_w = 1
        self._resized_ratio_h = 1

    def _load_rects(self):
        rects_xml = read_xml(self._filename)
        if rects_xml:
            self._rects = rects_xml
    

    def get_img(self):
        return self._img

    def get_rects(self):
        return self._rects
    
    def resizing_img(self, max_height=700, max_width=700):
        resized_img = self._img.copy()
        if resized_img.height > max_height:
            ratio = max_height / resized_img.height
            resized_img = resized_img.resize(
                (int(resized_img.width * ratio), int(resized_img.height * ratio))
            )
        if resized_img.width > max_width:
            ratio = max_width / resized_img.width
            resized_img = resized_img.resize(
                (int(resized_img.width * ratio), int(resized_img.height * ratio))
            )

        self._resized_ratio_w = self._img.width / resized_img.width
        self._resized_ratio_h = self._img.height / resized_img.height
        return resized_img

    def _resize_rect(self, rect):
        resized_rect = {}
        resized_rect["left"] = rect["left"] / self._resized_ratio_w
        resized_rect["width"] = rect["width"] / self._resized_ratio_w
        resized_rect["top"] = rect["top"] / self._resized_ratio_h
        resized_rect["height"] = rect["height"] / self._resized_ratio_h
        if 'label' in rect:
            resized_rect["label"] = rect['label']
        return resized_rect

    def get_resized_rects(self):
        return [self._resize_rect(rect) for rect in self._rects]

    def _chop_box_img(self, rect):
        rect["left"] = int(rect["left"] * self._resized_ratio_w)
        rect["width"] = int(rect["width"] * self._resized_ratio_w)
        rect["top"] = int(rect["top"] * self._resized_ratio_h)
        rect["height"] = int(rect["height"] * self._resized_ratio_h)
        left, top, width, height = rect['left'], rect['top'], rect['width'], rect['height']

        raw_image = np.asarray(self._img).astype("uint8")
        prev_img = np.zeros(raw_image.shape, dtype="uint8")
        prev_img[top : top + height, left : left + width] = raw_image[
            top : top + height, left : left + width
        ]
        prev_img = prev_img[top : top + height, left : left + width]
        label = ''
        if 'label' in rect:
            label = rect['label']
        return (Image.fromarray(prev_img), label)

    def init_annotation(self, rects):
        self._current_rects = rects
        return [self._chop_box_img(rect) for rect in self._current_rects]

    def set_annotation(self, index, label):
        self._current_rects[index]["label"] = label

    def save_annotation(self):
        output_xml(self._filename, self._img, self._current_rects)

class ImageDirManager:
    def __init__(self, dir_name):
        self._dir_name = dir_name
        self._files = []
        self._annotations_files = []
    
    def get_all_files(self, allow_types=['png', 'jpg', 'jpeg']):
        allow_types += [i.upper() for i in allow_types]
        mask = '.*\.['+'|'.join(allow_types) +']'     
        self._files = [file for file in os.listdir(self._dir_name) if re.match(mask, file)]
        return self._files
    
    def get_exist_annotation_files(self):
        self._annotations_files = [file for file in os.listdir(self._dir_name) if re.match('.*.xml', file)]
        return self._annotations_files
    
    def set_all_files(self, files):
        self._files = files
    
    def set_annotation_files(self, files):
        self._annotations_files = files
    
    def get_image(self, index):
        return self._files[index]
    
    def get_next_annotation_image(self, index):
        while index < len(self._files):
            index += 1
            image_file = self._files[index]
            image_file_name = image_file.split(".")[0]
            if f'{image_file_name}.xml' not in self._annotations_files:
                return index
        return None
