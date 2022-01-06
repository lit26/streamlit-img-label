import os
from pascal_voc_writer import Writer
from xml.etree import ElementTree as ET

"""
.. module:: streamlit_img_label
   :synopsis: annotation.
.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""


def read_xml(img_file):
    """read_xml
    Read the xml annotation file and extract the bounding boxes if exists.

    Args:
        img_file(str): the image file.
    Returns:
        rects(list): the bounding boxes of the image.
    """
    file_name = img_file.split(".")[0]
    if not os.path.isfile(f"{file_name}.xml"):
        return []
    tree = ET.parse(f"{file_name}.xml")
    root = tree.getroot()

    rects = []

    for boxes in root.iter("object"):
        label = boxes.find("name").text
        ymin = int(boxes.find("bndbox/ymin").text)
        xmin = int(boxes.find("bndbox/xmin").text)
        ymax = int(boxes.find("bndbox/ymax").text)
        xmax = int(boxes.find("bndbox/xmax").text)
        rects.append(
            {
                "left": xmin,
                "top": ymin,
                "width": xmax - xmin,
                "height": ymax - ymin,
                "label": label,
            }
        )
    return rects


def output_xml(img_file, img, rects):
    """output_xml
    Output the xml image annotation file

    Args:
        img_file(str): the image file.
        img(PIL.Image): the image object.
        rects(list): the bounding boxes of the image.
    """
    file_name = img_file.split(".")[0]
    writer = Writer(img_file, img.width, img.height)
    for box in rects:
        xmin = box["left"]
        ymin = box["top"]
        xmax = box["left"] + box["width"]
        ymax = box["top"] + box["height"]

        writer.addObject(box["label"], xmin, ymin, xmax, ymax)
    writer.save(f"{file_name}.xml")
