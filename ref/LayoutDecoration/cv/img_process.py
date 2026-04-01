# from PIL import Image, ImageFont, ImageDraw
# import cv2
# import numpy as np
# import time
# import io
#
#
# def generate_img_ui(screen_size, bg_img_path, font_path, user_location, user_string):
#     bg_img = cv2.imread(bg_img_path)
#     screen_v_h_rate = screen_size[1] / screen_size[0]
#     img_width = 720
#     bg_img = cv2.resize(bg_img, (img_width, int(img_width * screen_v_h_rate)))
#
#     img_size = bg_img.shape
#     size_scale = img_size[1] / 360
#
#     # prepare front image for time canvas
#     front_image = bg_img.copy()
#     time_front_start = (0.05 * img_size[1], 0.2 * img_size[0])
#     time_front_size = (0.3 * img_size[1], 0.6 * img_size[0])
#     time_front_area = np.array([(time_front_start[0], time_front_start[1]), (
#         time_front_start[0] + time_front_size[0], time_front_start[1] + time_front_size[1])]).astype(np.int32)
#
#     front_color = 50
#     front_image[time_front_area[0][1]:time_front_area[1][1], time_front_area[0][0]:time_front_area[1][0]] \
#         = np.array([front_color, front_color, front_color])
#
#     user_char_front_start = (time_front_start[0] + time_front_size[0] + 2, 0.2 * img_size[0])
#     user_char_front_size = (0.9 * img_size[1] - time_front_size[0] - 2, 0.6 * img_size[0])
#     user_char_front_area = np.array([(user_char_front_start[0], user_char_front_start[1]),
#                                      (user_char_front_start[0] + user_char_front_size[0],
#                                       user_char_front_start[1] + user_char_front_size[1])]).astype(np.int32)
#     front_image[user_char_front_area[0][1]:user_char_front_area[1][1],
#     user_char_front_area[0][0]:user_char_front_area[1][0]] = np.array([front_color, front_color, front_color])
#
#     # combine image
#     combined_img = (((bg_img.astype(np.int32) + front_image.astype(np.int32)) * (
#             front_image > 1)) * 0.5).astype(
#         np.uint8)
#     combined_img = Image.fromarray(cv2.cvtColor(combined_img, cv2.COLOR_BGR2RGB))
#
#     # draw char
#     # font_area = ((np.array(front_area) - np.mean(front_area, axis=0)) * 0.9 + np.mean(front_area, axis=0)).astype(
#     #     np.int32)
#     # draw hour minute
#     vertical_bias = int(8 * size_scale)
#     hour_minutes = time.strftime("%H:%M")
#     mon_day_week = time.strftime("%m-%d %a")
#     hour_font_size = int(35 * size_scale)
#     mon_font_size = int(15 * size_scale)
#     city_font_size = int(30 * size_scale)
#     draw = ImageDraw.Draw(combined_img)
#     font = ImageFont.truetype(font_path, hour_font_size)
#     w, h = draw.textsize(hour_minutes, font)
#     center_align_x_start = (time_front_area[0][0] + time_front_area[1][0]) / 2. - w / 2.
#     center_align_y_start = vertical_bias + (time_front_area[1][1] - time_front_area[0][1]) / 4 - (
#             hour_font_size + mon_font_size) * 1.2 / 2. + time_front_area[0][1]
#     draw.text((center_align_x_start, center_align_y_start), hour_minutes, font=font, fill=(255, 255, 255))
#
#     # draw mon_day char
#     font = ImageFont.truetype(font_path, mon_font_size)
#     w, h = draw.textsize(mon_day_week, font)
#     center_align_x_start = (time_front_area[0][0] + time_front_area[1][0]) / 2. - w / 2.
#     center_align_y_start = vertical_bias / 2. + center_align_y_start + 1. * hour_font_size
#     draw.text((center_align_x_start, center_align_y_start), mon_day_week, font=font, fill=(255, 255, 255))
#
#     # draw city char
#     font = ImageFont.truetype(font_path, city_font_size)
#     w, h = draw.textsize(user_location, font)
#     center_align_x_start = (time_front_area[0][0] + time_front_area[1][0]) / 2. - w / 2.
#     center_align_y_start = vertical_bias + (time_front_area[0][1] + time_front_area[1][1]) * 0.5 + (
#             -time_front_area[0][1] + time_front_area[1][1]) / 4. - city_font_size / 2.
#     draw.text((center_align_x_start, center_align_y_start), user_location, font=font, fill=(255, 255, 255))
#
#     # put文字
#     font_area = ((np.array(user_char_front_area) - np.mean(user_char_front_area, axis=0)) * 0.9 + np.mean(
#         user_char_front_area, axis=0)).astype(np.int32)
#     font_size = int(20 * size_scale)
#     user_string = '  ' + user_string
#
#     line_width = font_area[1][0] - font_area[0][0]
#     num_char_per_line = line_width // font_size
#     num_line = len(user_string) // num_char_per_line + 1
#     if len(user_string) % (line_width // font_size) < 4:
#         num_line = len(user_string) // num_char_per_line
#         num_char_per_line = int(len(user_string) / num_line + 0.5)
#         font_size = int(line_width / num_char_per_line + 0.5)
#     font = ImageFont.truetype(font_path, font_size)
#     # print(indent_w, font_area[1][0] - font_area[0][0])
#     # print(indent_h, font_area[1][1] - font_area[0][1])
#
#     line_height_scale = 1.2
#     center_align_y_start = -num_line * font_size * line_height_scale / 2. + (
#             font_area[0][1] + font_area[1][1]) / 2.
#     draw = ImageDraw.Draw(combined_img)
#     for i in range(num_line):
#         cur_line_str = user_string[i * num_char_per_line: (i + 1) * num_char_per_line]
#         draw.text((font_area[0][0], center_align_y_start + i * font_size * line_height_scale), cur_line_str,
#                   font=font, fill=(255, 255, 255))
#
#     img_bytes = io.BytesIO()
#     combined_img.save(img_bytes, format="PNG")
#     image_bytes = img_bytes.getvalue()
#
#     return image_bytes
