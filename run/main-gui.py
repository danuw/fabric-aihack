from ultralytics import YOLO
import cv2

import util
from sort.sort import *
from util import get_car, read_license_plate, write_csv


results = {}

mot_tracker = Sort()

seen_plates = {}

# load models
coco_model = YOLO('yolov8n.pt')
license_plate_detector = YOLO('./models/license_plate_detector.pt')

# load video
cap = cv2.VideoCapture('./sample.mp4')
cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

# Get the frame size from the video capture
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID'
out = cv2.VideoWriter('output.mp4', fourcc, 30.0, (frame_width, frame_height))

## choose the classes you want to detect
vehicles = [2, 3, 5, 7]
number_plate_text = ""

# read frames
frame_nmr = -1
ret = True
frame_interval = 1.0 / 30.0  # Process one frame every 1/30 second for 30 FPS
last_time = time.time()
frame_skip = 5  # Skip every 10 frames
while ret:
    frame_nmr += 1
    ret, frame = cap.read()
    if ret and frame_nmr % frame_skip == 0:  # Only process every nth frame
        last_time = time.time()
        results[frame_nmr] = {}
        # detect vehicles
        detections = coco_model(frame)[0]
        detections_ = []
        for detection in detections.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection
            if int(class_id) in vehicles:
                detections_.append([x1, y1, x2, y2, score])

        # cv show on images with bounding boxes
        # for detection in detections_:
        #     x1, y1, x2, y2, score = detection
        #     cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        # cv2.imshow('frame', frame)
        # cv2.waitKey(1)


        # track vehicles
        track_ids = mot_tracker.update(np.asarray(detections_))

        # detect license plates
        license_plates = license_plate_detector(frame)[0]

        for license_plate in license_plates.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = license_plate

            # assign license plate to car
            xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)

            if car_id != -1:

                # crop license plate
                license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]

                # process license plate
                license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                # display an image of license_plate_gray   
                _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 40, 100, cv2.THRESH_BINARY_INV)
                
                cv2.imshow('license_plate_crop_thresh', license_plate_crop_thresh)

                # read license plate number
                license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)

                if license_plate_text is not None:
                    results[frame_nmr][car_id] = {'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
                                                  'license_plate': {'bbox': [x1, y1, x2, y2],
                                                                    'text': license_plate_text,
                                                                    'bbox_score': score,
                                                                    'text_score': license_plate_text_score}}
                    number_plate_text = license_plate_text[:-5] + 'XXXXX'

                if license_plate_text is not None and license_plate_text not in seen_plates:
                    # This is the first time this plate is seen
                    # Get the current timestamp
                    timestamp = time.time()

                    # Add the plate and timestamp to seen_plates
                    seen_plates[license_plate_text] = timestamp

                    ## Make a call to the webhook
                    #requests.post(webhook_url, data={"plate": license_plate_text, "timestamp": timestamp})

                    ## Make a call to the webhook
                    #requests.post(webhook_url, data={"plate": license_plate_text})

                # cv show on images with bounding boxes
                # (int(x1), int(y1)), (int(x2), int(y2))
                blur_width = int(x2-x1)
                blur_height = int(y2-y1)
                blur_x = int(x1)
                blur_y = int(y1)

                roi = frame[blur_y:blur_y+blur_height, blur_x:blur_x+blur_width]
                blur_image = cv2.GaussianBlur(roi,(87,87),0)

                roi[:,:] = blur_image
                
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                # Calculate the position for the text
                text_position = (int(x1), int(y1) - 10)
                # Draw the text
                cv2.putText(frame, number_plate_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.rectangle(frame, (int(xcar1), int(ycar1)), (int(xcar2), int(ycar2)), (0, 0, 255), 2)
                cv2.imshow('frame', frame)
                
                #cv2.imshow('roi', roi)

                # Write the frame to the output file
                out.write(frame)

                cv2.waitKey(1)

# Release the VideoWriter and VideoCapture objects
out.release()
cap.release()

# write results
write_csv(results, './test.csv')
print(seen_plates)
#write_csv(seen_plates, './seen_plates.csv')
cv2.waitKey(0)
cv2.destroyAllWindows()