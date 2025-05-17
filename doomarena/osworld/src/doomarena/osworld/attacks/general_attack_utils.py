import re
import math
import os
from PIL import Image
import numpy as np
import io
import pytesseract


def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def shortest_distance_to_corners(x, y):
    # Coordinates of the four corners
    corners = [(0, 0), (1920, 0), (0, 1080), (1920, 1080)]

    # Calculate distances to each corner
    distances = [euclidean_distance(x, y, corner[0], corner[1]) for corner in corners]

    # Return the shortest distance
    return min(distances)


def find_files_with_prefix(directory, prefix):
    def find_shortest_string(strings):
        if not strings:  # Check if the list is empty
            return None

        shortest = strings[0]  # Assume the first string is the shortest
        for string in strings:
            if len(string) < len(shortest):
                shortest = (
                    string  # Update the shortest string if a shorter one is found
                )

        return shortest

    matching_files = []
    for file in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, file)) and file.startswith(prefix):
            matching_files.append(os.path.join(directory, file))

    # return the shorted match
    return find_shortest_string(matching_files)


def ensure_list(variable):
    if not isinstance(variable, list):
        variable = [variable]
    return variable


def extract_coordinates(code_string):
    # Pattern to match coordinates in pyautogui.click(980, 160
    click_pattern = re.compile(r"pyautogui\.click\(\s*(\d+)\s*,\s*(\d+)\s*")

    # Pattern to match coordinates in pyautogui.click(x=250, y=750
    click_keyword_pattern = re.compile(
        r"pyautogui\.click\(\s*x\s*=\s*(\d+)\s*,\s*y\s*=\s*(\d+)\s*"
    )

    # Pattern to match coordinates in pyautogui.moveTo(500, 300
    move_pattern = re.compile(r"pyautogui\.moveTo\(\s*(\d+)\s*,\s*(\d+)\s*")

    # Pattern to match coordinates in pyautogui.moveTo(x=250, y=750
    move_keyword_pattern = re.compile(
        r"pyautogui\.moveTo\(\s*x\s*=\s*(\d+)\s*,\s*y\s*=\s*(\d+)\s*"
    )

    # Pattern to match coordinate assignment like x, y = 500, 300
    assignment_pattern = re.compile(r"x\s*,\s*y\s*=\s*(\d+)\s*,\s*(\d+)")

    # Search for coordinates in the code string
    click_match = click_pattern.search(code_string)
    click_keyword_match = click_keyword_pattern.search(code_string)
    move_match = move_pattern.search(code_string)
    move_keyword_match = move_keyword_pattern.search(code_string)
    assignment_match = assignment_pattern.search(code_string)

    # Extract coordinates from the matches
    if click_match:
        x, y = click_match.groups()
    elif click_keyword_match:
        x, y = click_keyword_match.groups()
    elif move_match:
        x, y = move_match.groups()
    elif move_keyword_match:
        x, y = move_keyword_match.groups()
    elif assignment_match:
        x, y = assignment_match.groups()
    else:
        return None  # No coordinates found

    # Convert coordinates to integers
    return int(x), int(y)


def is_point_in_bbox(x, y, bboxes):
    def point_in_bbox(px, py, bbox):
        return bbox["xmin"] <= px <= bbox["xmax"] and bbox["ymin"] <= py <= bbox["ymax"]

    def distance_to_bbox(px, py, bbox):
        if px < bbox["xmin"]:
            if py < bbox["ymin"]:
                return math.sqrt((px - bbox["xmin"]) ** 2 + (py - bbox["ymin"]) ** 2)
            elif py > bbox["ymax"]:
                return math.sqrt((px - bbox["xmin"]) ** 2 + (py - bbox["ymax"]) ** 2)
            else:
                return bbox["xmin"] - px
        elif px > bbox["xmax"]:
            if py < bbox["ymin"]:
                return math.sqrt((px - bbox["xmax"]) ** 2 + (py - bbox["ymin"]) ** 2)
            elif py > bbox["ymax"]:
                return math.sqrt((px - bbox["xmax"]) ** 2 + (py - bbox["ymax"]) ** 2)
            else:
                return px - bbox["xmax"]
        else:
            if py < bbox["ymin"]:
                return bbox["ymin"] - py
            elif py > bbox["ymax"]:
                return py - bbox["ymax"]
            else:
                return 0

    in_bbox = False
    min_distance = float("inf")

    for bbox in bboxes:
        bbox = {k: float(v) for k, v in bbox.items()}
        if point_in_bbox(x, y, bbox):
            in_bbox = True
            break
        else:
            distance = distance_to_bbox(x, y, bbox)
            if distance < min_distance:
                min_distance = distance

    return in_bbox, min_distance if not in_bbox else 0.0


def mark_bounding_boxes(image, bounding_boxes):
    """
    Mark the pixels in the image matrix that are occupied by bounding boxes.

    Args:
    image (numpy.ndarray): 2D binary image where 1 represents occupied and 0 represents empty.
    bounding_boxes (list): List of bounding boxes in the format [x, y, w, h].
    """
    for box in bounding_boxes:
        x, y, w, h = box
        image[y : y + h, x : x + w] = 1  # Mark the area covered by each bounding box


def largest_empty_rectangle(image, squareness_preference_factor=1.0):
    """
    Find the largest empty rectangle in a 2D binary matrix with a preference for square-like rectangles.

    Args:
    image (numpy.ndarray): 2D binary matrix representing occupied (1) and empty (0) cells.
    squareness_preference_factor (float): A factor that adjusts the score for squareness.

    Returns:
    tuple: The coordinates of the top-left corner and the dimensions of the largest empty rectangle (x, y, w, h).
    """
    rows, cols = image.shape
    height = np.zeros((rows, cols), dtype=int)

    # Calculate the height of consecutive empty cells in each column
    for i in range(rows):
        for j in range(cols):
            if image[i, j] == 0:
                height[i, j] = height[i - 1, j] + 1 if i > 0 else 1

    # Now find the largest rectangle in each row using the height histogram method
    max_score = 0
    best_rectangle = (0, 0, 0, 0)  # (x, y, w, h)

    for i in range(rows):
        stack = []
        for j in range(cols + 1):
            cur_height = (
                height[i, j] if j < cols else 0
            )  # Sentinel value for the last column
            while stack and cur_height < height[i, stack[-1]]:
                h = height[i, stack.pop()]
                w = j if not stack else j - stack[-1] - 1
                area = h * w

                squareness_score = 1.0
                # we prefer wider with enough height
                if h > w:
                    squareness_score = min(h, w) / max(h, w)
                if h < 100:
                    squareness_score = min(squareness_score, 0.5)

                score = area * (squareness_score**squareness_preference_factor)

                if score > max_score:
                    max_score = score
                    best_rectangle = (stack[-1] + 1 if stack else 0, i - h + 1, w, h)
            stack.append(j)

    return best_rectangle


def extract_bounding_boxes_from_image(image_input):
    boxes = []

    # Convert input to PIL Image if it's in bytes
    if isinstance(image_input, bytes):
        image_input = Image.open(io.BytesIO(image_input))
    elif not isinstance(image_input, Image.Image):
        print("Invalid input: Input must be either bytes or a PIL Image object.")
        return boxes

    if image_input.mode == "RGBA":
        image_input = image_input.convert("RGB")

    # Perform OCR with bounding box output
    try:
        data = pytesseract.image_to_data(
            image_input, output_type=pytesseract.Output.DICT
        )

        for i in range(len(data["level"])):
            text = data["text"][i].strip()
            if text:  # Only include boxes with non-empty text
                x, y, w, h = (
                    data["left"][i],
                    data["top"][i],
                    data["width"][i],
                    data["height"][i],
                )
                if w > 0 and h > 0:
                    boxes.append([x, y, w, h])
    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return boxes

    return boxes


def find_largest_non_overlapping_box(
    image_size, bounding_boxes, squareness_preference_factor=1.0
):
    """
    Finds the largest non-overlapping bounding box in a given image with preference for square-like rectangles.

    Args:
    image_size (tuple): The size of the image (width, height).
    bounding_boxes (list): List of bounding boxes in the format [x, y, w, h].
    squareness_preference_factor (float): A factor that adjusts the score for squareness.

    Returns:
    tuple: Coordinates and size of the largest bounding box that can be drawn without overlap (x, y, w, h).
    """
    width, height = image_size
    image = np.zeros(
        (height, width), dtype=int
    )  # Create an empty grid representing the image

    # Mark occupied areas
    mark_bounding_boxes(image, bounding_boxes)

    # Find the largest empty rectangle
    largest_box = largest_empty_rectangle(image, squareness_preference_factor)

    return largest_box
