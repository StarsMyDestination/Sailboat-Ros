# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import os

plt.rcParams['font.sans-serif'] = ['Droid Sans Fallback']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负

obs_x = [-40.0, -50.0, -35.0, -50.0, -60.0, -30.0, -20.0, -30.0, -40.0]
obs_y = [20.0, 0.0, -10.0, 25.0, 20.0, -20.0, 20.0, 5.0, 10.0]

target_x = [-60, -50, -20]
target_y = [30, -20, 0]

plt.figure()
p1 = plt.subplot(111)

p1.scatter(target_y, target_x, s=40, c='cyan', label=u'目标点')
p1.scatter(obs_y, obs_x, s=160, c='red', label=u'障碍物')
for i in range(3):
    p1.text(target_y[i] + 1, target_x[i] + 1, s=u'目标{}'.format(i + 1), fontsize=12, color='black')

u, v = np.zeros((1, 1)), np.zeros((1, 1))

p1.scatter([15], [-15], s=40, c='g')
p1.text(15.2, -14.8, u'当前位置')
u[0, 0] = target_y[0] - 15
v[0, 0] = target_x[0] + 15
p1.quiver(15, -15, u, v, scale=1, units='xy', color='g')
u[0, 0] = target_y[1] - target_y[0]
v[0, 0] = target_x[1] - target_x[0]
p1.quiver(target_y[0], target_x[0], u, v, scale=1, units='xy', color='g')
u[0, 0] = target_y[2] - target_y[1]
v[0, 0] = target_x[2] - target_x[1]
p1.quiver(target_y[1], target_x[1], u, v, scale=1, units='xy', color = 'g')


p1.set_xlabel(u'东向 /m')
p1.set_ylabel(u'北向 /m')

p1.set_aspect(1)
# p1.grid(linestyle='--', linewidth=0.5)
p1.legend(loc='lower left', fontsize=12)
p1.axis([-30, 40, -75, -10])

plt.savefig('setup.svg')

plt.show()
