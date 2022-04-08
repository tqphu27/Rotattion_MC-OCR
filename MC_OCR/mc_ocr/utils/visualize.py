import matplotlib
matplotlib.rc('font', family='TakaoPGothic')
from matplotlib import pyplot as plt

import matplotlib.patches as patches
import cv2, os, csv
from mc_ocr.utils.common import poly, get_list_file_in_folder, get_list_gt_poly, type_map


color_map = {1: 'r', 15: 'green', 16: 'blue', 17: 'm', 18: 'cyan'}
txt_color_map = {1: 'b', 15: 'green', 16: 'blue', 17: 'm', 18: 'cyan'}
inv_type_map = {v: k for k, v in type_map.items()}

def get_list_error_imgs(list_path):
    with open(list_path, mode='r', encoding='utf-8') as f:
        list_file = f.readlines()
    list_file = [f.rstrip('\n') for f in list_file]
    return list_file

def viz_poly(img, list_poly, save_viz_path=None, ignor_type=[1]):
    
    fig, ax = plt.subplots(1)
    fig.set_size_inches(20, 20)
    plt.imshow(img)

    for polygon in list_poly:
        ax.add_patch(
            patches.Polygon(polygon.list_pts, linewidth=2, edgecolor=color_map[polygon.type], facecolor='none'))
        draw_value = polygon.value
        if polygon.type in ignor_type:
            draw_value = ''
        plt.text(polygon.list_pts[0][0], polygon.list_pts[0][1], draw_value, fontsize=20,
                 fontdict={"color": txt_color_map[polygon.type]})
    # plt.show()

    if save_viz_path is not None:
        print('Save visualized result to', save_viz_path)
        fig.savefig(save_viz_path, bbox_inches='tight')


def viz_icdar(img_path, anno_path, save_viz_path=None, extract_kie_type=False, ignor_type=[1]):
    if not isinstance(img_path, str):
        image = img_path
    else:
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    list_poly = []
    with open(anno_path, 'r', encoding='utf-8') as f:
        anno_txt = f.readlines()

    for anno in anno_txt:
        anno = anno.rstrip('\n')

        idx = -1
        for i in range(0, 8):
            idx = anno.find(',', idx + 1)

        coordinates = anno[:idx]
        val = anno[idx + 1:]
        type = 1
        if extract_kie_type:
            last_comma_idx = val.rfind(',')
            type_str = val[last_comma_idx + 1:]
            val = val[:last_comma_idx]
            if type_str in inv_type_map.keys():
                type = inv_type_map[type_str]

        coors = [int(f) for f in coordinates.split(',')]
        pol = poly(coors, type=type, value=val)
        list_poly.append(pol)
    viz_poly(img=image,
             list_poly=list_poly,
             save_viz_path=save_viz_path,
             ignor_type=ignor_type)


def viz_icdar_multi(img_dir, anno_dir, save_viz_dir, extract_kie_type=False, ignor_type=[1]):
    list_files = get_list_file_in_folder(img_dir)
    for idx, file in enumerate(list_files):
        if idx < 0:
            continue
        # if 'mcocr_public_145014smasw' not in file:
        #     continue
        print(idx, file)
        img_path = os.path.join(img_dir, file)
        anno_path = os.path.join(anno_dir, file.replace('.jpg', '.txt'))
        save_img_path = os.path.join(save_viz_dir, file)
        viz_icdar(img_path, anno_path, save_img_path, extract_kie_type, ignor_type)


def viz_same_img_in_different_dirs(first_dir, second_dir, list_path=None, resize_ratio=1.0):
    list_files = get_list_file_in_folder(first_dir)
    list_err_images = None
    if list_path is not None:
        list_err_images = get_list_error_imgs(list_path)
    for n, file in enumerate(list_files):
        if list_err_images is not None:
            if file.replace('.jpg', '') not in list_err_images:
                continue
        print(n, file)
        # if n<160:
        #     continue
        first_img_path = os.path.join(first_dir, file)
        first_img = cv2.imread(first_img_path)
        first_img_res = cv2.resize(first_img,
                                   (int(resize_ratio * first_img.shape[1]), int(resize_ratio * first_img.shape[0])))
        cv2.imshow('first_img', first_img_res)

        second_img_path = os.path.join(second_dir, file.replace('.jpg', '') + '_ model_epoch_639_minibatch_243000_ 0.1.jpg')
        second_img = cv2.imread(second_img_path)
        second_img_res = cv2.resize(second_img,
                                    (int(resize_ratio * second_img.shape[1]), int(resize_ratio * second_img.shape[0])))
        cv2.imshow('second_img', second_img_res)
        cv2.waitKey(0)


def viz_csv(csv_file, img_dir, viz_dir):
    with open(csv_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        first_line = True
        for n, row in enumerate(csv_reader):
            if first_line:
                first_line = False
                continue
            img_name = row[0]
            # if img_name!='mcocr_public_145014smasw.jpg':
            #     continue
            list_poly = get_list_gt_poly(row, add_key_to_value=True)

            image = cv2.imread(os.path.join(img_dir, img_name))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            viz_poly(img=image,
                     list_poly=list_poly,
                     save_viz_path=os.path.join(viz_dir, img_name))


def viz_csv2(csv_file, img_dir):
    with open(csv_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        first_line = True
        for n, row in enumerate(csv_reader):
            if first_line:
                first_line = False
                continue
            img_name = row[0]
            key, value = row[3].split('|||'), row[2].split('|||')
            num_box, score = row[4], row[5]
            for val in value:
                if val == 'Saigon Co.op':
                    print('\n', img_name, 'Score', score)
                    print('value', value)
                    image = cv2.imread(os.path.join(img_dir, img_name))
                    cv2.imshow('img', image)
                    cv2.waitKey(0)


def viz_output_of_pick(img_dir, output_txt_dir, output_viz_dir):
    list_output_txt = get_list_file_in_folder(output_txt_dir, ext=['txt'])
    list_output_txt = sorted(list_output_txt)
    for n, file in enumerate(list_output_txt):
        print(n, file)
        # if n <60:
        #     continue
        with open(os.path.join(output_txt_dir, file), mode='r', encoding='utf-8') as f:
            output_txt = f.readlines()

        list_poly = []
        for line in output_txt:
            coordinates, type, text = line.replace('\n', '').split('\t')
            find_poly = poly(coordinates, type=inv_type_map[type], value=text)
            list_poly.append(find_poly)

        img_name = file.replace('.txt', '.jpg')
        image = cv2.imread(os.path.join(img_dir, img_name))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        viz_poly(img=image,
                 list_poly=list_poly,
                 save_viz_path=os.path.join(output_viz_dir, img_name))

