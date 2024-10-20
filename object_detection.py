import csv
import cv2
import os
import requests
import time
import urllib.request
from ultralytics import YOLO
from ultralytics.engine.results import Results
import numpy as np

def main():
    # open yolov8 object detection model
    model = YOLO("yolov8n.pt")
    # capture video
    test_sample = 'banana_30cm'
    video_path = "http://192.168.1.119/cam.jpg"
    folder_name=f"images/{test_sample}"
    file_name = f"results/{test_sample}.csv"
    cv2.namedWindow("live Object Detection", cv2.WINDOW_AUTOSIZE)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Failed to open the IP camera stream")
        return
    # open csv file for saving data
    with open(file_name, 'w') as file:
        field_names = ['width', 'height', 'top', 'bottom', 'left', 'right', 'name', 'confidence', 'distance',]
        writer = csv.writer(file)
        writer.writerow(field_names)
        # loop through video frames
        while True:
            # get start time for a code
            start_time = time.time()
            # Read a frame from the video stream
            img_resp=urllib.request.urlopen(video_path)
            imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
            width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            # if frame capture is successful
            frame = cv2.imdecode(imgnp,-1)
            # run model on frame
            # results = model.track(frame, persist=True)
            results = model.track(frame, persist=True)
            # process image
            process_data = process_image(results[0], frame, width, height)
            distance = get_distance()
            end_time = time.time()-start_time
            # quit if q is pressed close the app
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            # if cv2.waitKey(1) & 0xFF == ord("s"):
            if(len(process_data)> 0):
                writer.writerow(['Detection', '', 'interval', end_time])
                if not os.path.isdir(folder_name):
                    os.makedirs(folder_name)
                cv2.imwrite(f"{folder_name}/{end_time}.jpg", frame);
                # pick the result with most confidence
                useful_row = []
                max_confidence = 0.0;
                for data in process_data:
                    csv_row = [width, height, data.top, data.bottom, data.left, data.right, data.name, data.confidence, distance]
                    if data.confidence > max_confidence:
                        useful_row = csv_row
                        max_confidence = data.confidence
                # save data
                writer.writerow(useful_row)
    # release the video capture
    cap.release()
    cv2.destroyAllWindows()

def process_image(result:Results,frame,width, height, minimum_confidence = 0.15):
    cordinate_list = result.boxes.xyxy
    confidence_list = result.boxes.conf
    class_list = result.boxes.cls
    
    results = []
    img = frame
    for conf_index in range(len(confidence_list)):
        confidence = confidence_list[conf_index]
        coordinate = cordinate_list[conf_index]
        name = result.names[int(class_list[conf_index])]
        
        
        if confidence >= minimum_confidence:
            left = int(coordinate[0])
            top = int(coordinate[1])
            right = int(coordinate[2])
            bottom = int(coordinate[3])
            img = cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
            img = cv2.putText(img, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,0), 2)
            cv2.imshow('prediction', img)
            data = ProcessData(float(confidence), left, top, right, bottom, name)
            results.append(data)
            
        else:
            cv2.imshow('prediction', img)
    return results

def get_distance():
    response = requests.get("http://192.168.1.145/")
    distance = response.json()['distance_cm']
    return distance;
        

class ProcessData:
    def __init__(self, confidence:float, left:int, top:int, right:int, bottom:int, name:str):
        self.confidence = confidence
        self.top = top
        self.bottom = bottom
        self.right= right
        self.left = left
        self.name = name

if __name__ == "__main__":
    main()



