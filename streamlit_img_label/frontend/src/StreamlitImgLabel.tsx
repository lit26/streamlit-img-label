import React, { useEffect, useState } from "react"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"
import { fabric } from "fabric"

interface PythonArgs {
  canvasWidth: number
  canvasHeight: number
  rectTop: number
  rectLeft: number
  rectWidth: number
  rectHeight: number
  boxColor: string
  imageData: Uint8ClampedArray
  lockAspect: boolean
}

const StreamlitImgLabel = (props: ComponentProps) => {
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
    const {
      rectTop,
      rectLeft,
      rectWidth,
      rectHeight,
      boxColor,
      lockAspect,
    }: PythonArgs = props.args
    const canvas = new fabric.Canvas("c", {
      enableRetinaScaling: false,
      backgroundImage: dataUri,
      uniScaleTransform: lockAspect,
    })

    const rect = new fabric.Rect({
      left: rectLeft,
      top: rectTop,
      fill: "",
      width: rectWidth,
      height: rectHeight,
      objectCaching: true,
      stroke: boxColor,
      strokeWidth: 3,
      hasRotatingPoint: false,
    })
    canvas.add(rect)

    setCanvas(canvas)
    Streamlit.setFrameHeight()
    // eslint-disable-next-line
  }, [canvasHeight, canvasWidth, dataUri])

  /**
   * Send the coordinates of the rectangle
   * back to streamlit.
   */
  useEffect(() => {
    if (!canvas) {
      return
    }
    const handleEvent = () => {
      canvas.renderAll()
      const coords = canvas.getObjects()[0].getBoundingRect()
      Streamlit.setComponentValue({ coords: coords })
    }

    canvas.on("object:modified", handleEvent)
    return () => {
      canvas.off("object:modified")
    }
  })

  return <canvas id="c" width={canvasWidth} height={canvasHeight} />
}

export default withStreamlitConnection(StreamlitImgLabel)
