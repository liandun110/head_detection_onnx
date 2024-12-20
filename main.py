# Import Packages
import onnxruntime
import cv2
import numpy as np

# Global Variables
confidence = 80
conf_thresold = 0.8
iou_thresold = 0.3
Display_Confidence = True
Display_Class = True

Display_Confidence = True
Display_Class = True


# load image
def load_image(image_path, input_shape):
    image = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    input_height, input_width = input_shape[2:]
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(image_rgb, (input_width, input_height))
    # Scale input pixel value to 0 to 1
    input_image = resized / 255.0
    input_image = input_image.transpose(2, 0, 1)
    input_tensor = input_image[np.newaxis, :, :, :].astype(np.float32)
    input_tensor.shape

    return [image, input_tensor, rgb_image]


# load model
def load_model(model_path):
    opt_session = onnxruntime.SessionOptions()
    opt_session.enable_mem_pattern = False
    opt_session.enable_cpu_mem_arena = False
    opt_session.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_DISABLE_ALL
    model_path = model_path
    EP_list = ['CPUExecutionProvider']
    ort_session = onnxruntime.InferenceSession(model_path, providers=EP_list)
    model_inputs = ort_session.get_inputs()
    input_shape = model_inputs[0].shape

    return [ort_session, input_shape]


# run inference using the onnx model
def predict(image, ort_session, input_tensor):
    global conf_thresold

    model_inputs = ort_session.get_inputs()
    input_names = [model_inputs[i].name for i in range(len(model_inputs))]
    input_shape = model_inputs[0].shape
    input_height, input_width = input_shape[2:]
    image_height, image_width = image.shape[:2]
    model_output = ort_session.get_outputs()
    output_names = [model_output[i].name for i in range(len(model_output))]
    outputs = ort_session.run(output_names, {input_names[0]: input_tensor})[0]
    predictions = np.squeeze(outputs).T

    # Filter out object confidence scores below threshold
    scores = np.max(predictions[:, 4:], axis=1)
    predictions = predictions[scores > conf_thresold, :]
    scores = scores[scores > conf_thresold]
    # Get the class with the highest confidence
    class_ids = np.argmax(predictions[:, 4:], axis=1)
    # Get bounding boxes for each object
    boxes = predictions[:, :4]
    # rescale box
    input_shape = np.array([input_width, input_height, input_width, input_height])
    boxes = np.divide(boxes, input_shape, dtype=np.float32)
    boxes *= np.array([image_width, image_height, image_width, image_height])
    boxes = boxes.astype(np.int32)

    return [boxes, scores, class_ids]


def annotate(image, boxes, scores, class_ids):
    # Apply non-maxima suppression to suppress weak, overlapping bounding boxes
    global iou_thresold
    global Display_Confidence
    global Display_Class

    indices = nms(boxes, scores, iou_thresold)
    # Define classes
    CLASSES = ['head']
    image_draw = image.copy()
    for (bbox, score, label) in zip(xywh2xyxy(boxes[indices]), scores[indices], class_ids[indices]):
        bbox = bbox.round().astype(np.int32).tolist()
        cls_id = int(label)
        cls = CLASSES[cls_id]
        x1, y1, w, h = bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]
        display_message = ""
        if Display_Class:
            display_message = display_message + cls
        if Display_Confidence:
            display_message = f"{display_message} {score:.2f}"
        cv2.rectangle(image_draw, (x1, y1), (x1 + w, y1 + h), (0, 255, 0), 1)
        if Display_Confidence or Display_Class:
            # Calculate text width and height
            (text_width, text_height), _ = cv2.getTextSize(display_message, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            # Put text background
            cv2.rectangle(image_draw, (x1, y1), (x1 + text_width, y1 - text_height - 10), (0, 255, 0), -1)
            # Put text
            cv2.putText(image_draw, display_message, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

    rgb_image_draw = cv2.cvtColor(image_draw, cv2.COLOR_BGR2RGB)
    return rgb_image_draw


def nms(boxes, scores, iou_threshold):
    # Sort by score
    sorted_indices = np.argsort(scores)[::-1]
    keep_boxes = []
    while sorted_indices.size > 0:
        # Pick the last box
        box_id = sorted_indices[0]
        keep_boxes.append(box_id)
        # Compute IoU of the picked box with the rest
        ious = compute_iou(boxes[box_id, :], boxes[sorted_indices[1:], :])
        # Remove boxes with IoU over the threshold
        keep_indices = np.where(ious < iou_threshold)[0]
        sorted_indices = sorted_indices[keep_indices + 1]

    return keep_boxes


def compute_iou(box, boxes):
    # Compute xmin, ymin, xmax, ymax for both boxes
    xmin = np.maximum(box[0], boxes[:, 0])
    ymin = np.maximum(box[1], boxes[:, 1])
    xmax = np.minimum(box[2], boxes[:, 2])
    ymax = np.minimum(box[3], boxes[:, 3])

    # Compute intersection area
    intersection_area = np.maximum(0, xmax - xmin) * np.maximum(0, ymax - ymin)

    # Compute union area
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    boxes_area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    union_area = box_area + boxes_area - intersection_area

    # Compute IoU
    iou = intersection_area / union_area

    return iou


def xywh2xyxy(x):
    # Convert bounding box (x, y, w, h) to bounding box (x1, y1, x2, y2)
    y = np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2
    y[..., 1] = x[..., 1] - x[..., 3] / 2
    y[..., 2] = x[..., 0] + x[..., 2] / 2
    y[..., 3] = x[..., 1] + x[..., 3] / 2
    return y


def prediction(image_path, conf=80, disp_Class=True, disp_Confidence=True,
               iou_thresh_=30, model_path="model.onnx"):
    global confidence
    global conf_thresold
    global iou_thresold
    global Display_Confidence
    global Display_Class

    Display_Confidence = disp_Confidence
    Display_Class = disp_Class
    confidence = conf
    conf_thresold = confidence / 100
    iou_thresold = iou_thresh_
    # *Calling Functions*
    model = load_model(model_path)
    input_I = load_image(image_path, model[1])  # path and input shape is passed
    predictions = predict(input_I[0], model[0], input_I[1])  # image, ort_session, and input tensor is passed
    annotated_image = annotate(input_I[0], predictions[0], predictions[1],
                               predictions[2])  # boxes, and scores are passed

    return annotated_image


def predict_from_terminal(image_path="img.jpg"):
    annotatedImage = prediction(image_path)
    annotatedImage = cv2.cvtColor(annotatedImage, cv2.COLOR_RGB2BGR)
    cv2.imshow('Annotated Image', annotatedImage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    predict_from_terminal()
