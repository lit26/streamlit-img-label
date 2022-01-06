import os
import streamlit.components.v1 as components
import numpy as np
from .manage import ImageManager, ImageDirManager

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "st_img_label",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("st_img_label", path=build_dir)


def st_img_label(resized_img, box_color="blue", rects=[], key=None):
    """Create a new instance of "st_img_label".

    Parameters
    ----------
    img_file: PIL.Image
        The image to be croppepd
    box_color: string
        The color of the cropper's bounding box. Defaults to blue.
    rects: list
        list of bounding boxes that already exists.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    rects: list
        list of bounding boxes.
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
    custom_labels = ["", "dog", "cat"]

    img_dir = "img_dir"

    idm = ImageDirManager(img_dir)

    if "files" not in st.session_state:
        st.session_state["files"] = idm.get_all_files()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["image_index"] = 0
    else:
        idm.set_all_files(st.session_state["files"])
        idm.set_annotation_files(st.session_state["annotation_files"])

    def rehresh():
        st.session_state["files"] = idm.get_all_files()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["image_index"] = 0

    def next_image():
        image_index = st.session_state["image_index"]
        if image_index < len(st.session_state["files"]) - 1:
            st.session_state["image_index"] += 1
        else:
            st.warning("This is the last image.")

    def previous_image():
        image_index = st.session_state["image_index"]
        if image_index > 0:
            st.session_state["image_index"] -= 1
        else:
            st.warning("This is the first image.")

    def next_annotate_file():
        image_index = st.session_state["image_index"]
        next_image_index = idm.get_next_annotation_image(image_index)
        if next_image_index:
            st.session_state["image_index"] = idm.get_next_annotation_image(image_index)
        else:
            st.warning("All images are annotated.")
            next_image()

    def go_to_image():
        file_index = st.session_state["files"].index(st.session_state["file"])
        st.session_state["image_index"] = file_index

    # Sidebar: show status
    n_files = len(st.session_state["files"])
    n_annotate_files = len(st.session_state["annotation_files"])
    st.sidebar.write("Total files:", n_files)
    st.sidebar.write("Total annotate files:", n_annotate_files)
    st.sidebar.write("Remaining files:", n_files - n_annotate_files)

    st.sidebar.selectbox(
        "Files",
        st.session_state["files"],
        index=st.session_state["image_index"],
        on_change=go_to_image,
        key="file",
    )
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.button(label="Previous image", on_click=previous_image)
    with col2:
        st.button(label="Next image", on_click=next_image)
    st.sidebar.button(label="Next need annotate", on_click=next_annotate_file)
    st.sidebar.button(label="Rehresh", on_click=rehresh)

    # Main content: annotate images
    img_file_name = idm.get_image(st.session_state["image_index"])
    img_path = os.path.join(img_dir, img_file_name)
    im = ImageManager(img_path)
    img = im.get_img()
    resized_img = im.resizing_img()
    resized_rects = im.get_resized_rects()
    rects = st_img_label(resized_img, box_color="red", rects=resized_rects)

    def annotate():
        im.save_annotation()
        image_annotate_file_name = img_file_name.split(".")[0] + ".xml"
        if image_annotate_file_name not in st.session_state["annotation_files"]:
            st.session_state["annotation_files"].append(image_annotate_file_name)
        next_annotate_file()

    if rects:
        st.button(label="Save", on_click=annotate)
        preview_imgs = im.init_annotation(rects)

        for i, prev_img in enumerate(preview_imgs):
            prev_img[0].thumbnail((200, 200))
            col1, col2 = st.columns(2)
            with col1:
                col1.image(prev_img[0])
            with col2:
                default_index = 0
                if prev_img[1]:
                    default_index = custom_labels.index(prev_img[1])

                select_label = col2.selectbox(
                    "Label", custom_labels, key=f"label_{i}", index=default_index
                )
                im.set_annotation(i, select_label)
