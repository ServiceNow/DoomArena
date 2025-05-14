import xmltodict
from PIL import Image, ImageDraw, ImageFont

def ensure_list(variable):
    if not isinstance(variable, list):
        variable = [variable]
    return variable

def fill_bounding_box_with_text(image, bounding_box, text, init_font_size=20, fill_color="lightgray", edge_thickness=2):
    draw = ImageDraw.Draw(image)
    
    # Define the bounding box coordinates
    xmin, ymin, xmax, ymax = (float(bounding_box['xmin']), float(bounding_box['ymin']), 
                              float(bounding_box['xmax']), float(bounding_box['ymax']))
    
    # Calculate the bounding box dimensions
    box_width = xmax - xmin - 2 * edge_thickness
    box_height = ymax - ymin - 2 * edge_thickness

    # Function to calculate if text fits in the box
    def text_fits(draw, text, font, box_width, box_height):
        _, _, text_width, text_height = draw.textbbox((0, 0), text=text, font=font)
        return text_width <= box_width and text_height <= box_height

    def calculate_area(text_bbox):
        return text_bbox[2] * text_bbox[3]

    # Initial horizontal fitting
    font_size = init_font_size
    font = ImageFont.truetype("DejaVuSansMono-Bold.ttf", font_size)
    while not text_fits(draw, text, font, box_width, box_height) and font_size > 1:
        font_size -= 1
        font = ImageFont.truetype("DejaVuSansMono-Bold.ttf", font_size)

    # Calculate text size and area for initial horizontal fit
    bbox_horiz = draw.textbbox((0, 0), text=text, font=font)
    area_horiz = calculate_area(bbox_horiz)

    # print("font size", font_size)
    # print("area", area_horiz)

    # Attempt to remove '\n' and fit again
    font_size = init_font_size
    text_no_newline = text.replace("\n", " ")
    font_no_newline = ImageFont.truetype("DejaVuSansMono-Bold.ttf", font_size)
    while not text_fits(draw, text_no_newline, font_no_newline, box_width, box_height) and font_size > 1:
        font_size -= 1
        font_no_newline = ImageFont.truetype("DejaVuSansMono-Bold.ttf", font_size)
    
    bbox_no_newline = draw.textbbox((0, 0), text=text_no_newline, font=font_no_newline)
    area_no_newline = calculate_area(bbox_no_newline)

    # print("font size", font_size)
    # print("area", area_no_newline)
    # print("---------------------------------------------")

    # Determine the best fit and draw the text accordingly
    best_text = text
    best_font = font
    best_bbox = bbox_horiz
    best_area = area_horiz
    
    if area_no_newline > best_area:
        best_text = text_no_newline
        best_font = font_no_newline
        best_bbox = bbox_no_newline
        best_area = area_no_newline

    text_width = best_bbox[2]
    text_height = best_bbox[3]
    # plus edge for padding
    x = xmin + (box_width + 2 * edge_thickness - text_width) / 2
    y = ymin + (box_height + 2 * edge_thickness - text_height) / 2
    
    # Draw text within the bounding box
    draw.rectangle([xmin, ymin, xmax, ymax], fill=fill_color)
    draw.text((x, y), best_text, font=best_font, fill="black")
    
    return image


def get_largest_bounding_box_center(bounding_boxes):
    def get_area(box):
        return (float(box['xmax']) - float(box['xmin'])) * (float(box['ymax']) - float(box['ymin']))
    
    largest_box = max(bounding_boxes, key=get_area)
    
    center_x = (float(largest_box['xmin']) + float(largest_box['xmax'])) / 2
    center_y = (float(largest_box['ymin']) + float(largest_box['ymax'])) / 2
    
    return int(center_x), int(center_y)