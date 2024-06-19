import cv2
from ultralytics import YOLO
import numpy as np
import os


def predict(model, frame):
    results = model(source=frame, show=False, conf=0.5, classes=[0], boxes=True)
    return results


def get_coordinates_people(results):
    results_object = results[0]
    list_coordinates_all_detected_objects = []
    for box in results_object.boxes.xyxy:
        x_min, y_min, x_max, y_max = box
        coordinates = (x_min.item(), y_min.item(), x_max.item(), y_max.item())
        list_coordinates_all_detected_objects.append(coordinates)
    return list_coordinates_all_detected_objects


def parse_coordinates_od_danger_zone(input_text):
    coordinates_list = []
    input_text = input_text.replace("(", "").replace(")", "").replace(",", "")
    coordinates_text = input_text.split()

    if len(coordinates_text) % 8 != 0:
        print("Неверное количество координат")
        return []

    for i in range(0, len(coordinates_text), 8):
        try:
            x1, y1, x2, y2, x3, y3, x4, y4 = map(float, coordinates_text[i:i + 8])
            coordinates_list.append((x1, y1, x2, y2, x3, y3, x4, y4))
        except ValueError:
            print("Ошибка преобразования координат")
            return []

    return coordinates_list


def calculate_intersection_ratio(object_coordinates, danger_zone_coordinates):
    x_min_obj, y_min_obj, x_max_obj, y_max_obj = object_coordinates
    object_area = (x_max_obj - x_min_obj) * (y_max_obj - y_min_obj)
    intersection_area = max(0, min(x_max_obj, danger_zone_coordinates[2]) - max(x_min_obj, danger_zone_coordinates[0])) * \
                        max(0, min(y_max_obj, danger_zone_coordinates[5]) - max(y_min_obj, danger_zone_coordinates[1]))
    intersection_ratio = intersection_area / object_area * 100
    return intersection_ratio


def check_for_danger(object_coordinates, danger_zone_coordinates, is_in_danger):
    intersection_ratio = calculate_intersection_ratio(object_coordinates, danger_zone_coordinates)
    if intersection_ratio >= 20:
        is_in_danger = True
    return is_in_danger


def save_image(frame, list_coordinates_all_detected_objects, list_coordinates_all_danger_zones, file_name):
    overlay = frame.copy()

    for coordinates in list_coordinates_all_danger_zones:
        pts = np.array(coordinates, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.fillPoly(overlay, [pts], (0, 0, 255))

    for coordinates in list_coordinates_all_detected_objects:
        x_min, y_min, x_max, y_max = coordinates[:4]
        cv2.rectangle(overlay, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), thickness=-1)

    alpha = 0.3
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    return frame


def process_image(image_path, model, coordinates_from_input):
    frame = cv2.imread(image_path)
    detected_objects = get_coordinates_people(predict(model, frame))
    danger_zones = parse_coordinates_od_danger_zone(coordinates_from_input)
    is_in_danger = False

    for obj_coords in detected_objects:
        for danger_zone_coords in danger_zones:
            is_in_danger = check_for_danger(obj_coords, danger_zone_coords, is_in_danger)

    frame_with_rectangles = save_image(frame, detected_objects, danger_zones, os.path.basename(image_path) + "_processed")
    cv2.imwrite(os.path.join("../danger_zone/results", "processed_images", os.path.basename(image_path) + "_processed.jpg"), frame_with_rectangles)

    return is_in_danger


def process_video(video_path, model, coordinates_from_input):
    cap = cv2.VideoCapture(video_path)
    is_in_danger = False
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    out = cv2.VideoWriter(os.path.join("../danger_zone/results", "processed_videos", os.path.basename(video_path) + "_processed.mp4"),
                          cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        detected_objects = get_coordinates_people(predict(model, frame))
        danger_zones = parse_coordinates_od_danger_zone(coordinates_from_input)

        for obj_coords in detected_objects:
            for danger_zone_coords in danger_zones:
                is_in_danger = check_for_danger(obj_coords, danger_zone_coords, is_in_danger)

        frame_with_rectangles = save_image(frame, detected_objects, danger_zones, os.path.basename(video_path) + "_processed")
        out.write(frame_with_rectangles)

        cv2.imshow('Frame', frame_with_rectangles)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    return is_in_danger

def main(name_file, user_input, media_type):
    model = YOLO("runs/detect/train5/weights/best.pt")
    file_path = f"save_media/{media_type}/{name_file}"
    coordinates_from_input = user_input

    if not os.path.exists("../danger_zone/results"):
        os.makedirs("../danger_zone/results")
    if not os.path.exists(os.path.join("../danger_zone/results", "processed_images")):
        os.makedirs(os.path.join("../danger_zone/results", "processed_images"))
    if not os.path.exists(os.path.join("../danger_zone/results", "processed_videos")):
        os.makedirs(os.path.join("../danger_zone/results", "processed_videos"))

    if file_path.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        is_in_danger = process_image(file_path, model, coordinates_from_input)
    elif file_path.endswith(('.mp4', '.avi', '.mov')):
        is_in_danger = process_video(file_path, model, coordinates_from_input)
    else:
        print("Неподдерживаемый формат файла")

    return is_in_danger





# (0, 0) (640, 0) (640, 480) (0, 480)
# (100, 100) (400, 200) (600, 500) (200, 400)
# (100, 100) (900, 200) (700, 800) (100, 700)