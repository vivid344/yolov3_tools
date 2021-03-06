#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# usage: ./increase_picture.py hogehoge.jpg
#

import cv2
import numpy as np
import sys
import os
from shutil import copyfile
from PIL import Image


def main(data_dir, file_name, class_num, class_name, out_dir):
    # # ルックアップテーブルの生成
    # min_table = 50
    # max_table = 205
    # diff_table = max_table - min_table
    # gamma1 = 0.75
    # gamma2 = 1.5
    #
    # LUT_HC = np.arange(256, dtype = 'uint8' )
    # LUT_LC = np.arange(256, dtype = 'uint8' )
    # LUT_G1 = np.arange(256, dtype = 'uint8' )
    # LUT_G2 = np.arange(256, dtype = 'uint8' )
    #
    # LUTs = []
    #
    # # 平滑化用
    # average_square = (10,10)
    #
    # # ハイコントラストLUT作成
    # for i in range(0, min_table):
    #     LUT_HC[i] = 0
    #
    # for i in range(min_table, max_table):
    #     LUT_HC[i] = 255 * (i - min_table) / diff_table
    #
    # for i in range(max_table, 255):
    #     LUT_HC[i] = 255
    #
    # # その他LUT作成
    # for i in range(256):
    #     LUT_LC[i] = min_table + i * (diff_table) / 255
    #     LUT_G1[i] = 255 * pow(float(i) / 255, 1.0 / gamma1)
    #     LUT_G2[i] = 255 * pow(float(i) / 255, 1.0 / gamma2)
    #
    # LUTs.append(LUT_HC)
    # LUTs.append(LUT_LC)
    # LUTs.append(LUT_G1)
    # LUTs.append(LUT_G2)

    # 画像の読み込み
    img_src = cv2.imread(
        "{0}/images/{1}/{2}".format(data_dir, class_num, file_name), 1)
    trans_img = []
    trans_img.append(img_src)

    # 反転
    flip_img = []
    for img in trans_img:
        flip_img.append(cv2.flip(img, 0))  # 縦反転
        flip_img.append(cv2.flip(img, 1))  # 横反転

        height_y_rev = cv2.flip(img, 0).shape[0]
        width_y_rev = cv2.flip(img, 0).shape[1]

        height_x_rev = cv2.flip(img, 1).shape[0]
        width_x_rev = cv2.flip(img, 1).shape[1]

    # 回転
    rotate_img = []
    for img in trans_img:
        rotate_img.append(img.transpose(1,0,2)[:,::-1])  # 90
        rotate_img.append(np.rot90(np.rot90(img)))  # 180
        rotate_img.append(img.transpose(1,0,2)[::-1])  # 270

    for img in flip_img:
        rotate_img.append(img.transpose(1, 0, 2)[:, ::-1])  # 90
        rotate_img.append(np.rot90(np.rot90(img)))  # 180
        rotate_img.append(img.transpose(1, 0, 2)[::-1])  # 270

    # ディレクトリを作り、反転と回転イメージをリストに追加
    trans_img.extend(flip_img)
    trans_img.extend(rotate_img)
    if not os.path.exists("{0}/{1}".format(data_dir, out_dir)):
        os.makedirs("{0}/{1}".format(data_dir, out_dir))
    if not os.path.exists("{0}/inflated_labels".format(data_dir)):
        os.makedirs("{0}/inflated_labels".format(data_dir))

    # 保存
    base = os.path.splitext(os.path.basename(file_name))[0] + "_"
    img_src.astype(np.float64)

    height = img_src.shape[0]
    width = img_src.shape[1]

    y_rev_x1 = 0
    y_rev_y1 = 0
    y_rev_x2 = 0
    y_rev_y2 = 0

    x_rev_x1 = 0
    x_rev_y1 = 0
    x_rev_x2 = 0
    x_rev_y2 = 0

    for i, img in enumerate(trans_img):
        if not os.path.exists("{0}/{1}/{2}".format(data_dir, out_dir, class_name)):
            os.makedirs("{0}/{1}/{2}".format(data_dir, out_dir, class_name))
        if not os.path.exists("{0}/inflated_labels/{1}".format(data_dir, class_name)):
            os.makedirs("{0}/inflated_labels/{1}".format(data_dir, class_name))
        new_file_name = base + str(i)
        text_file_name = file_name.replace(".jpg", ".txt")
        cv2.imwrite(
            "{0}/{1}/{2}/{3}".format(data_dir, out_dir, class_name, new_file_name + ".jpg"), img)
        if i == 0:  # 画像変更なし
            copyfile("{0}/labels/{1}/{2}".format(data_dir, class_num, text_file_name),
                     "{0}/inflated_labels/{1}/{2}".format(data_dir, class_name, new_file_name + ".txt"))
        elif i == 1:  # 縦反転
            with open("{0}/inflated_labels/{1}/{2}".format(data_dir,
                                                           class_name,
                                                           new_file_name + ".txt"), "w") as new_bb_data:
                with open("{0}/labels/{1}/{2}".format(data_dir, class_num, text_file_name), "r") as bb_data:
                    for line in bb_data.readlines():
                        elems = line.split(' ')
                        if len(elems) != 4:
                            new_bb_data.write(line)
                            continue
                        x1 = int(elems[0])
                        y1 = int(elems[1])
                        x2 = int(elems[2])
                        y2 = int(elems[3])

                        y_rev_x1 = x1
                        y_rev_y1 = height - y2
                        y_rev_x2 = x2
                        y_rev_y2 = height - y1

                        new_bb_data.write("{0} {1} {2} {3}\n".format(
                            x1, height - y2, x2, height - y1))
        elif i == 2:  # 横反転
            with open("{0}/inflated_labels/{1}/{2}".format(data_dir,
                                                           class_name,
                                                           new_file_name + ".txt"), "w") as new_bb_data:
                with open("{0}/labels/{1}/{2}".format(data_dir, class_num, text_file_name), "r") as bb_data:
                    for line in bb_data.readlines():
                        elems = line.split(' ')
                        if len(elems) != 4:
                            new_bb_data.write(line)
                            continue
                        x1 = int(elems[0])
                        y1 = int(elems[1])
                        x2 = int(elems[2])
                        y2 = int(elems[3])

                        x_rev_x1 = width - x2
                        x_rev_y1 = y1
                        x_rev_x2 = width - x1
                        x_rev_y2 = y2

                        new_bb_data.write("{0} {1} {2} {3}\n".format(
                            width - x2, y1, width - x1, y2))
        elif i == 3:  # 90度回転
            with open("{0}/inflated_labels/{1}/{2}".format(data_dir,
                                                           class_name,
                                                           new_file_name + ".txt"), "w") as new_bb_data:
                with open("{0}/labels/{1}/{2}".format(data_dir, class_num, text_file_name), "r") as bb_data:
                    for line in bb_data.readlines():
                        elems = line.split(' ')
                        if len(elems) != 4:
                            new_bb_data.write(line)
                            continue
                        x1 = int(elems[0])
                        y1 = int(elems[1])
                        x2 = int(elems[2])
                        y2 = int(elems[3])
                        new_bb_data.write("{0} {1} {2} {3}\n".format(
                            height - y2, x2, height - y1, x1))
        elif i == 4:  # 180度回転
            with open("{0}/inflated_labels/{1}/{2}".format(data_dir,
                                                           class_name,
                                                           new_file_name + ".txt"), "w") as new_bb_data:
                with open("{0}/labels/{1}/{2}".format(data_dir, class_num, text_file_name), "r") as bb_data:
                    for line in bb_data.readlines():
                        elems = line.split(' ')
                        if len(elems) != 4:
                            new_bb_data.write(line)
                            continue
                        x1 = int(elems[0])
                        y1 = int(elems[1])
                        x2 = int(elems[2])
                        y2 = int(elems[3])
                        new_bb_data.write("{0} {1} {2} {3}\n".format(
                            width - x2, height - y2, width - x1, height - y1))
        elif i == 5:  # 270度回転
            with open("{0}/inflated_labels/{1}/{2}".format(data_dir,
                                                           class_name,
                                                           new_file_name + ".txt"), "w") as new_bb_data:
                with open("{0}/labels/{1}/{2}".format(data_dir, class_num, text_file_name), "r") as bb_data:
                    for line in bb_data.readlines():
                        elems = line.split(' ')
                        if len(elems) != 4:
                            new_bb_data.write(line)
                            continue
                        x1 = int(elems[0])
                        y1 = int(elems[1])
                        x2 = int(elems[2])
                        y2 = int(elems[3])
                        new_bb_data.write("{0} {1} {2} {3}\n".format(
                            y2, width - x2, y1, width - x1))

        elif i == 6:  # y rev 90度回転
            with open("{0}/inflated_labels/{1}/{2}".format(data_dir,
                                                           class_name,
                                                           new_file_name + ".txt"), "w") as new_bb_data:
                with open("{0}/labels/{1}/{2}".format(data_dir, class_num, text_file_name), "r") as bb_data:
                    for line in bb_data.readlines():
                        elems = line.split(' ')
                        if len(elems) != 4:
                            new_bb_data.write(line)
                            continue
                        x1 = int(elems[0])
                        y1 = int(elems[1])
                        x2 = int(elems[2])
                        y2 = int(elems[3])
                        new_bb_data.write("{0} {1} {2} {3}\n".format(
                            height - y_rev_y2, y_rev_x2, height - y_rev_y1, y_rev_x1))
        elif i == 7:  # y rev 180度回転
            with open("{0}/inflated_labels/{1}/{2}".format(data_dir,
                                                           class_name,
                                                           new_file_name + ".txt"), "w") as new_bb_data:
                with open("{0}/labels/{1}/{2}".format(data_dir, class_num, text_file_name), "r") as bb_data:
                    for line in bb_data.readlines():
                        elems = line.split(' ')
                        if len(elems) != 4:
                            new_bb_data.write(line)
                            continue
                        x1 = int(elems[0])
                        y1 = int(elems[1])
                        x2 = int(elems[2])
                        y2 = int(elems[3])
                        new_bb_data.write("{0} {1} {2} {3}\n".format(
                            width - y_rev_x2, height - y_rev_y2, width - y_rev_x1, height - y_rev_y1))
        elif i == 8:  # y rev 270度回転
            with open("{0}/inflated_labels/{1}/{2}".format(data_dir,
                                                           class_name,
                                                           new_file_name + ".txt"), "w") as new_bb_data:
                with open("{0}/labels/{1}/{2}".format(data_dir, class_num, text_file_name), "r") as bb_data:
                    for line in bb_data.readlines():
                        elems = line.split(' ')
                        if len(elems) != 4:
                            new_bb_data.write(line)
                            continue
                        x1 = int(elems[0])
                        y1 = int(elems[1])
                        x2 = int(elems[2])
                        y2 = int(elems[3])
                        new_bb_data.write("{0} {1} {2} {3}\n".format(
                            y_rev_y2, width - y_rev_x2, y_rev_y1, width - y_rev_x1))
        elif i == 9:  # x rev 90度回転
            with open("{0}/inflated_labels/{1}/{2}".format(data_dir,
                                                           class_name,
                                                           new_file_name + ".txt"), "w") as new_bb_data:
                with open("{0}/labels/{1}/{2}".format(data_dir, class_num, text_file_name), "r") as bb_data:
                    for line in bb_data.readlines():
                        elems = line.split(' ')
                        if len(elems) != 4:
                            new_bb_data.write(line)
                            continue
                        x1 = int(elems[0])
                        y1 = int(elems[1])
                        x2 = int(elems[2])
                        y2 = int(elems[3])
                        new_bb_data.write("{0} {1} {2} {3}\n".format(
                            height - x_rev_y2, x_rev_x2, height - x_rev_y1, x_rev_x1))
        elif i == 10:  # x rev 180度回転
            with open("{0}/inflated_labels/{1}/{2}".format(data_dir,
                                                           class_name,
                                                           new_file_name + ".txt"), "w") as new_bb_data:
                with open("{0}/labels/{1}/{2}".format(data_dir, class_num, text_file_name), "r") as bb_data:
                    for line in bb_data.readlines():
                        elems = line.split(' ')
                        if len(elems) != 4:
                            new_bb_data.write(line)
                            continue
                        x1 = int(elems[0])
                        y1 = int(elems[1])
                        x2 = int(elems[2])
                        y2 = int(elems[3])
                        new_bb_data.write("{0} {1} {2} {3}\n".format(
                            width - x_rev_x2, height - x_rev_y2, width - x_rev_x1, height - x_rev_y1))
        elif i == 11:  # x rev 270度回転
            with open("{0}/inflated_labels/{1}/{2}".format(data_dir,
                                                           class_name,
                                                           new_file_name + ".txt"), "w") as new_bb_data:
                with open("{0}/labels/{1}/{2}".format(data_dir, class_num, text_file_name), "r") as bb_data:
                    for line in bb_data.readlines():
                        elems = line.split(' ')
                        if len(elems) != 4:
                            new_bb_data.write(line)
                            continue
                        x1 = int(elems[0])
                        y1 = int(elems[1])
                        x2 = int(elems[2])
                        y2 = int(elems[3])
                        new_bb_data.write("{0} {1} {2} {3}\n".format(
                            x_rev_y2, width - x_rev_x2, x_rev_y1, width - x_rev_x1))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("please set data directory path.")
        print("python inflate_images.py [input_dir] [out_dir]")
        exit(-1)

    # 増幅するフォルダ名の決定
    out_dir = "obj"
    if len(sys.argv) > 2:
        out_dir = sys.argv[2]

    data_dir = sys.argv[1]

    # クラス名のファイルの読み込み
    classes = []
    classes = [line.rstrip() for line in open('{0}/classes.txt'.format(data_dir), 'r')]

    print('class name = ', end='')
    for i in classes:
        print(i, end=' ')
    print("")

    for _, dirs, _ in os.walk("{0}/images/".format(data_dir)):
        for class_name in classes:
            for class_num in dirs:
                if class_num == class_name:
                    print("{0}/images/{1}".format(data_dir, class_name))
                    for _, _, files in os.walk("{0}/images/{1}".format(data_dir, class_num)):
                        for file_name in files:
                            try:
                                main(data_dir, file_name, class_num, class_name, out_dir)
                            except:
                                continue