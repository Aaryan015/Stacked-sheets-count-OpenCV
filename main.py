import streamlit as st
import cv2
import numpy as np
import math
from PIL import Image

def count_horizontal_lines(image_path):
    img = cv2.imread(image_path)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    for _ in range(2):
        gray_img = cv2.GaussianBlur(img, (3, 3), cv2.BORDER_DEFAULT)
    edges = cv2.Canny(gray_img, 100, 200)

    blank_img = np.zeros(edges.shape)
    lines = cv2.HoughLinesP(edges.copy(), 1, np.pi/180, 100, minLineLength=300, maxLineGap=100)
    horizontal_lines = []

    if lines is not None:
        for x1, y1, x2, y2 in lines.reshape(-1, 4):
            if x1 == x2:
                continue
            slope = (y2 - y1) / (x2 - x1)
            angle = math.degrees(math.atan(abs(slope)))
            if angle < 10:
                horizontal_lines.append([x1, y1, x2, y2])
                cv2.line(blank_img, (x1, y1), (x2, y2), (255, 255, 255), 2)

        for i in range(len(horizontal_lines)):
            if horizontal_lines[i][1] > horizontal_lines[i][3]:
                horizontal_lines[i][1], horizontal_lines[i][3] = horizontal_lines[i][3], horizontal_lines[i][1]

        sorted_lines = sorted(horizontal_lines, key=lambda x: x[1])

        differences = []

        for i in range(len(sorted_lines) - 1):
            differences.append(sorted_lines[i][3] - sorted_lines[i][1])

        median_gap = np.median(differences)

        start = 0
        final_lines = []

        for line in sorted_lines:
            if start < line[1]:
                start = line[1] + 10
                final_lines.append(line)

        return len(final_lines)
    else:
        return 0

st.title('Counting sheets in a stack using OpenCV')

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "mp4"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image = np.array(image)
    temp_image_path = "temp_image.jpg"
    cv2.imwrite(temp_image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

    num_sheets = count_horizontal_lines(temp_image_path)

    st.image(image, width=500, caption='Uploaded Image')
    st.write(f"Number of sheets detected: {num_sheets}")