# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['Droid Sans Fallback']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负

x = np.linspace(-180, 180, 1000)
y1 = np.exp(-8 * (np.cos(np.deg2rad(x)) + 0.25))

# y2 = np.exp(-3 * np.cos(np.deg2rad(x))) + 10
y2_0 = np.abs(20 / 180.0 * x)
y2 = np.abs(20 / 180.0 * x) + 30
y3 = np.ones_like(x) * 10

p1 = plt.subplot(111)

p1.plot(x, y1, label=u'$G_w$ 风向损失')
p1.plot(x, y2_0, ':', label=u'$G_t$ 顺风转向损失')
p1.plot(x, y2, '-.',label=u'$G_t$ 逆风转向损失')
p1.plot(x, y3,'--', label=u'$G_f$ 路程固定损失')
p1.set_xlabel(r'$\alpha_a$  or  $\alpha_t$')
p1.set_ylabel(u'损失')
p1.axis([-180, 180, -1, 100])
# p1.legend(loc='upper right', fontsize=8)
p1.legend()
plt.savefig('gloss.svg')
plt.show()

