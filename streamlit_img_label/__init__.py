import os
import streamlit.components.v1 as components
from PIL import Image
import numpy as np
from manage import ImageManager

_RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "st_img_label",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("st_img_label", path=build_dir)

# def _recommended_box(img: Image):
#     # Find a recommended box for the image (could be replaced with image detection)
#     box = (img.width * 0.2, img.height * 0.2, img.width * 0.8, img.height * 0.8)
#     box = [int(i) for i in box]
#     height = box[3] - box[1]
#     width = box[2] - box[0]

#     left, top = box[0], box[1]
#     return {'left' : int(left), 'top' : int(top), 'width' : int(width), 'height' : int(height)}


def st_img_label(resized_img: Image, box_color: str = "blue", rects=[], key=None):
    """Create a new instance of "st_img_label".

    Parameters
    ----------
    img_file: PIL.Image
        The image to be croppepd
    box_color: string
        The color of the cropper's bounding box. Defaults to blue, can accept
        other string colors recognized by fabric.js or hex colors in a format like
        '#ff003c'
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    PIL.Image
    The cropped image in PIL.Image format
    """
    # Get arguments to send to frontend
    canvasWidth = resized_img.width
    canvasHeight = resized_img.height

    # Translates image to a list for passing to Javascript
    imageData = np.array(resized_img.convert("RGBA")).flatten().tolist()

    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # Defaults to a box whose vertices are at 20% and 80% of height and width.
    # The _recommended_box function could be replaced with some kind of image
    # detection algorith if it suits your needs.
    component_value = _component_func(
        canvasWidth=canvasWidth,
        canvasHeight=canvasHeight,
        rects=rects,
        boxColor=box_color,
        imageData=imageData,
        key=key,
    )
    # Return a cropped image using the box from the frontend
    if component_value:
        return component_value["rects"]
    else:
        return rects


# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/__init__.py`
if not _RELEASE:
    import streamlit as st
    st.set_option("deprecation.showfileUploaderEncoding", False)
    custom_labels = ["", "Food", "Science", "Research", 'Sports']

    img_file_name = "test.png"
    im = ImageManager(img_file_name)
    img = im.get_img()
    resized_img = im.resizing_img()
    resized_rects = im.get_resized_rects()
    rects = st_img_label(resized_img, box_color="red", rects=resized_rects)
    if rects:
        st.button(label="Save", on_click=im.save_annotation)
        preview_imgs = im.init_annotation(rects)

        for i, prev_img in enumerate(preview_imgs):
            prev_img[0].thumbnail((200, 200))
            col1, col2 = st.columns(2)
            with col1:
                col1.image(prev_img[0])
            with col2:
                default_index = custom_labels.index(prev_img[1])

                select_label = col2.selectbox("Label", custom_labels, key=f"label_{i}", index=default_index)
                im.set_annotation(i, select_label)
