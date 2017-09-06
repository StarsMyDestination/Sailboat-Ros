from math import *

lat_ori = 59.427139999999994
lon_ori = 10.466663333333332


def d2r(d):
    return d / 180.0 * pi


def w84_calc_ne(lat2, lon2):
    lat1, lon1 = d2r(lat_ori), d2r(lon_ori)
    lat2, lon2 = d2r(lat2), d2r(lon2)
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1

    a = 6378137.0
    e_2 = 6.69437999014e-3
    r1 = a * (1 - e_2) / (1 - e_2 * (sin(lat1)) ** 2) ** 1.5
    r2 = a / sqrt(1 - e_2 * (sin(lat1)) ** 2)

    north = r1 * d_lat
    east = r2 * cos(lat1) * d_lon
    return north, east


if __name__ == '__main__':

    n0, e0 = w84_calc_ne(lat_ori, lon_ori)
    print(n0, e0)

    ## fleet race
    # lat1, lon1 = 59.427667, 10.468694000000028
    # lat2, lon2 = 59.427722, 10.468278000000055
    # lat3, lon3 = 59.429385, 10.46864000000005
    # lat4, lon4 = 59.429058, 10.47031400000003
    # n1, e1 = w84_calc_ne(lat1, lon1)
    # print('n1: {}, e1: {}'.format(n1, e1))
    # n2, e2 = w84_calc_ne(lat2, lon2)
    # print('n2: {}, e2: {}'.format(n2, e2))
    # n3, e3 = w84_calc_ne(lat3, lon3)
    # print('n3: {}, e3: {}'.format(n3, e3))
    # n4, e4 = w84_calc_ne(lat4, lon4)
    # print('n4: {}, e4: {}'.format(n4, e4))

    ## station keeping
    lat5, lon5 = 59.425784, 10.4731249
    n5, e5 = w84_calc_ne(lat5, lon5)
    print('n5: {}, e5: {}'.format(n5, e5)) # n5:-151.061785525, e5: 366.770497586