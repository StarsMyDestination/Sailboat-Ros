# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.interpolate import splprep, splev
import os

plt.rcParams['font.sans-serif'] = ['Droid Sans Fallback']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负

quiver_settings_1 = {'scale': 1,
                     'units': 'xy',
                     'width': 0.1}


def get_spline(path_x, path_y, heading):
    headingVecLength = 0.5
    headingVec = [headingVecLength * math.cos(math.pi - heading), headingVecLength * math.sin(math.pi - heading)]
    pts = []
    for i, (x, y) in enumerate(zip(path_x, path_y)):
        if i == 1:
            pts.append((path_x[0] + headingVec[0], path_y[0] + headingVec[1]))
        pts.append([x, y])
    pts = np.array(pts)
    tck, u = splprep(pts.T, u=None, s=0.2, per=0)
    u_new = np.linspace(u.min(), u.max(), 1000)
    x_new, y_new = splev(u_new, tck, der=0)
    return x_new, y_new


if __name__ == '__main__':

    obs_x, obs_y = [], []
    with open('map.txt', 'r') as f:
        for row, line in enumerate(f.readlines()):
            line = line.rstrip('\n').rstrip(' ').split(' ')
            for col, num in enumerate(line):
                if int(num) == 1:
                    obs_x.append(row)
                    obs_y.append(col)
    n_row, n_col = row + 1, col + 1
    print(n_row, n_col)
    print(obs_x)
    print(obs_y)

    heading_list = []
    heading_name_list = []
    wind_list = []
    wind_name_list = []
    path_x_list, path_y_list = [], []
    path_x_f_list, path_y_f_list = [], []
    with open('path.txt', 'r') as f:
        path_x, path_y = [], []
        path_x_f, path_y_f = [], []
        for line in f.readlines():
            if line.startswith('heading'):
                heading_tmp = line.rstrip('\n').split(',')
                heading_name_list.append(heading_tmp[1])
                heading = float(heading_tmp[2])
                heading_list.append(heading)
                continue
            elif line.startswith('wind'):
                wind_tmp = line.rstrip('\n').split(',')
                wind_name_list.append(wind_tmp[1])
                wind_list.append(float(wind_tmp[2]))
                continue
            elif line == '####\n':
                path_x_list.append(path_x)
                path_y_list.append(path_y)
                path_x_f, path_y_f = get_spline(path_x, path_y, heading)
                path_x_f_list.append(path_x_f)
                path_y_f_list.append(path_y_f)
                path_x, path_y = [], []
                continue
            line = line.rstrip('\n').split(',')
            path_x.append(int(line[0]))
            path_y.append(int(line[1]))
            # path_x_f.append(float(line[2]))
            # path_y_f.append(float(line[3]))

    print('wind: {}'.format(wind_list))
    print('heading: {}'.format(heading_list))
    print(len(path_x_list))
    print(path_y_list)
    print(wind_name_list)

    for i in range(len(heading_list)):
    # for i in range(1):
        heading = heading_list[i]
        heading_name = heading_name_list[i]
        wind = wind_list[i]
        wind_name = wind_name_list[i]
        path_x = path_x_list[i]
        path_y = path_y_list[i]
        path_x_f = path_x_f_list[i]
        path_y_f = path_y_f_list[i]

        windVecLength = 1
        windVec = [windVecLength * math.cos(wind), windVecLength * math.sin(wind)]

        headingVecLength = 1
        headingVec = [headingVecLength * math.cos(heading), headingVecLength * math.sin(heading)]

        # plt.figure(dpi=300)
        plt.figure()
        # plt.figure(figsize=(6, 4), dpi=98)
        p1 = plt.subplot(111)
        p1.plot(np.array(path_y), np.array(path_x), label=u'规划路径')
        # p1.plot(np.array(path_y_f), np.array(path_x_f), label=u'规划路径(光滑)')
        p1.plot(np.array(obs_y), np.array(obs_x), 'ro', label=u'障碍物')
        p1.scatter([path_y[0], path_y[-1]], [path_x[0], path_x[-1]], s=50, c='green')

        p1.quiver(np.array(0), np.array(0), np.ones((1, 1)) * windVec[1], np.ones((1, 1)) * windVec[0],
                  **quiver_settings_1)
        p1.text(0.1, -0.1, s=u'风向', fontsize=12, color='magenta')

        # x, y = np.array([path_y[0], path_y[0] + headingVec[1]]), np.array([path_x[0], path_x[0] + headingVec[0]])
        # p1.quiver(x[:-1], y[:-1], x[1:] - x[:-1], y[1:] - y[:-1], color='green')


        x = path_x[0]
        y = path_y[0]
        u, v = np.zeros((8, 8)), np.zeros((8, 8))
        u[0, 0] = -1
        v[0, 0] = 0
        u[1, 1] = 0
        v[1, 1] = + 1
        u[2, 2] = + 1
        v[2, 2] = 0
        u[3, 3] = 0
        v[3, 3] = - 1
        u[4, 4] = - 1
        v[4, 4] = + 1
        u[5, 5] = + 1
        v[5, 5] = + 1
        u[6, 6] = + 1
        v[6, 6] = - 1
        u[7, 7] = - 1
        v[7, 7] = - 1
        p1.quiver(np.array(y), np.array(x), u, v, scale=1, units='xy', color='g')

        p1.text(path_y[0] + 0.1, path_x[0] - 0.1, s=u'起点', fontsize=12, color='black')
        p1.text(path_y[-1] + 0.1, path_x[-1] - 0.1, s=u'终点', fontsize=12, color='black')

        # p1.set_title('upwind')
        p1.legend()
        p1.axis([0, n_col - 1, n_row - 1, 0])
        p1.set_xticks(np.arange(-1, n_col + 1, 1))
        p1.set_yticks(np.arange(-1, n_row + 1, 1))
        p1.xaxis.tick_top()
        p1.grid(linestyle='--', linewidth=0.5)
        p1.set_aspect(1)


        file_folder = 'test_imgs/{}'.format(heading_name)
        if not os.path.exists(file_folder):
            os.system('mkdir -p ' + file_folder)
        file_path = os.path.join(file_folder, '{}.svg'.format(wind_name))
        print("saving file {} ...".format(file_path))
        plt.savefig(file_path)
        # plt.show()

        plt.close('all')
