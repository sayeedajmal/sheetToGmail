import cv2
import numpy as np

# ------------------------------
# Load YOLOv3 model
# ------------------------------
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")

# Load COCO class labels (80 objects YOLO can detect)
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Get YOLO output layers
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# ------------------------------
# Detection function
# ------------------------------
def detect_objects(frame):
    height, width = frame.shape[:2]

    # Prepare input blob
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)

    # Run forward pass
    outs = net.forward(output_layers)

    # Parse detections
    boxes, confidences, class_ids = [], [], []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x, center_y, w, h = (detection[0:4] * np.array([width, height, width, height])).astype("int")
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, int(w), int(h)])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Non-max suppression
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Draw boxes
    if len(indexes) > 0:
        for i in np.array(indexes).flatten():  # works with tuple/list/ndarray
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            conf = round(confidences[i], 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {conf}", (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame


# ------------------------------
# Choose mode: IMAGE or CAMERA
# ------------------------------

USE_CAMERA = False  # 🔹 set True for webcam, False for single image

if USE_CAMERA:
    cap = cv2.VideoCapture(0)  # open webcam
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = detect_objects(frame)
        cv2.imshow("YOLOv3 Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
else:
    # Detect from an image
    img = cv2.imread("images.webp")   # replace with your image
    result = detect_objects(img)
    cv2.imwrite("result.jpg", result)
    cv2.imshow("YOLOv3 Detection", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
