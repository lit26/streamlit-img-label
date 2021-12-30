import React, { useEffect, useState } from "react"
import {
    ComponentProps,
    Streamlit,
    withStreamlitConnection,
} from "streamlit-component-lib"
import { fabric } from "fabric"
import styles from "./StreamlitImgLabel.module.css"

interface RectProps {
    top: number
    left: number
    width: number
    height: number
    label?: string
}

interface PythonArgs {
    canvasWidth: number
    canvasHeight: number
    rects: RectProps[]
    boxColor: string
    imageData: Uint8ClampedArray
    lockAspect: boolean
}

const StreamlitImgLabel = (props: ComponentProps) => {
    const [mode, setMode] = useState("light")
    const [canvas, setCanvas] = useState(new fabric.Canvas(""))
    const { canvasWidth, canvasHeight, imageData }: PythonArgs = props.args
    /*
     * Translate Python image data to a JavaScript Image
     */
    var invisCanvas = document.createElement("canvas")
    var ctx = invisCanvas.getContext("2d")

    invisCanvas.width = canvasWidth
    invisCanvas.height = canvasHeight

    // create imageData object
    let dataUri: any
    if (ctx) {
        var idata = ctx.createImageData(canvasWidth, canvasHeight)

        // set our buffer as source
        idata.data.set(imageData)

        // update canvas with new data
        ctx.putImageData(idata, 0, 0)
        dataUri = invisCanvas.toDataURL()
    } else {
        dataUri = ""
    }

    /**
     * Initialize canvas on mount and add a rectangle
     */
    useEffect(() => {
        const { rects, boxColor, lockAspect }: PythonArgs = props.args
        const canvasTmp = new fabric.Canvas("c", {
            enableRetinaScaling: false,
            backgroundImage: dataUri,
            uniScaleTransform: lockAspect,
        })

        rects.forEach((rect) => {
            const { top, left, width, height } = rect
            canvasTmp.add(
                new fabric.Rect({
                    left: left,
                    top: top,
                    fill: "",
                    width: width,
                    height: height,
                    objectCaching: true,
                    stroke: boxColor,
                    strokeWidth: 1,
                    strokeUniform: true,
                    hasRotatingPoint: false,
                })
            )
        })

        setCanvas(canvasTmp)
        Streamlit.setFrameHeight()
        // eslint-disable-next-line
    }, [canvasHeight, canvasWidth, dataUri])

    const addBoxHandler = () => {
        canvas.add(
            new fabric.Rect({
                left: 100,
                top: 100,
                fill: "",
                width: 100,
                height: 100,
                objectCaching: true,
                stroke: props.args.boxColor,
                strokeWidth: 1,
                strokeUniform: true,
                hasRotatingPoint: false,
            })
        )
        sendCoordinates()
    }

    const removeBoxHandler = () => {
        canvas.getActiveObjects().forEach((obj) => {
            canvas.remove(obj)
        })
        sendCoordinates()
    }

    /**
     * Send the coordinates of the rectangle
     * back to streamlit.
     */
    const sendCoordinates = () => {
        // console.log(canvas.getObjects())
        // const selectObject = canvas.getActiveObject()
        // console.log(canvas.getObjects().indexOf(selectObject))
        const rects = canvas.getObjects().map((rect) => rect.getBoundingRect())
        Streamlit.setComponentValue({ rects })
    }

    useEffect(() => {
        if (!canvas) {
            return
        }
        const handleEvent = () => {
            canvas.renderAll()
            sendCoordinates()
        }

        canvas.on("object:modified", handleEvent)
        return () => {
            canvas.off("object:modified")
        }
    })

    const onSelectMode = (mode: string) => {
        setMode(mode)
        if (mode === "dark") document.body.classList.add("dark-mode")
        else document.body.classList.remove("dark-mode")
    }

    useEffect(() => {
        // Add listener to update styles
        window
            .matchMedia("(prefers-color-scheme: dark)")
            .addEventListener("change", (e) =>
                onSelectMode(e.matches ? "dark" : "light")
            )

        // Setup dark/light mode for the first time
        onSelectMode(
            window.matchMedia("(prefers-color-scheme: dark)").matches
                ? "dark"
                : "light"
        )

        // Remove listener
        return () => {
            window
                .matchMedia("(prefers-color-scheme: dark)")
                .removeEventListener("change", () => {})
        }
    }, [])

    return (
        <>
            <canvas
                id="c"
                className={mode === "dark" ? styles.dark : ""}
                width={canvasWidth}
                height={canvasHeight}
            />
            <div className={mode === "dark" ? styles.dark : ""}>
                <button
                    className={mode === "dark" ? styles.dark : ""}
                    onClick={addBoxHandler}
                >
                    Add bounding box
                </button>
                <button
                    className={mode === "dark" ? styles.dark : ""}
                    onClick={removeBoxHandler}
                >
                    Remove select
                </button>
            </div>
        </>
    )
}

export default withStreamlitConnection(StreamlitImgLabel)
