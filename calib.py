# data = [
#     [(584.2385786802031, 172.46192893401016), (682.0, 233.95939086294416), (773.010152284264, 287.98477157360406),
#      (859.015306122449, 337.0), (498.0, 271.3265306122449), (597.3128205128205, 324.0), (689.7179487179487, 369.0),
#      (776.0204081632653, 411.9642857142857), (417.0, 355.0), (520.0, 403.0051020408163), (611.2233502538071, 440.0),
#      (696.0, 480.0)],
#     [(544.0, 296.0), (480.0, 368.0), (-1.0, -1.0), (376.0, 488.0), (408.0, 264.0), (352.0, 344.0), (312.0, 408.0),
#      (-1.0, -1.0), (269.1015228426396, 230.0), (216.0, 314.0), (184.0, 384.0), (-1.0, -1.0)],
#     [(317.995, 196.34), (448.5925, 161.1875), (592.42, 119.0), (755.1975, 75.5), (367.0, 337.04),
#      (498.45137157107234, 303.02493765586036), (639.0, 267.815), (800.215, 219.175), (407.0, 468.0), (542.0, 441.0),
#      (676.9625935162095, 404.8927680798005), (830.9501246882793, 370.9800498753117)]]

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import linalg
import ast
from os import listdir

chessboard_size = (4, 3)

objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), dtype=np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2) * 2

colors = range(len(objp))

imageSize = (1024, 768)

calib_files = [
    ['weiss_raum', 'weiss_raum_2'],
    ['schwarz', 'schwarz_2'],
    ['weiss_fenster', 'weiss_fenster_2']
]

stereo_calib_files = listdir('stereo_improved')


def main():
    P12_1, P12_2 = calibrate(1, 0)
    P13_1, P13_2 = calibrate(1, 2)

    # print(p12_1, p12_2, q12)
    # print(p13_1, p13_2)

    with open(f'stereo_improved/{stereo_calib_files[0]}', 'r') as f:
        data = ast.literal_eval(f.read())
        for i in range(len(data[0])):
            cord12 = triangulate(P12_1, P12_2, np.array(data[1][i]).T, np.array(data[0][i]).T)
            cord13 = triangulate(P13_1, P13_2, np.array(data[1][i]).T, np.array(data[2][i]).T)
            dist = np.sqrt(np.sum((np.array(cord13) - np.array(cord12)) ** 2))
            print(dist, cord12, cord13)

        coords = np.array(
            [np.array(triangulate(P12_1, P12_2, np.array(data[1][i]).T, np.array(data[0][i]))) for i in
             range(len(data[0]))]) - np.array([0, 0, 37])
        coords2 = np.array(
            [np.array(triangulate(P13_1, P13_2, np.array(data[1][i]).T, np.array(data[2][i]))) for i in
             range(len(data[0]))]) - np.array([0, 0, 37])

        print(coords)
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        points = coords.T
        ax.scatter3D(points[0], points[1], points[2], color='red')
        points2 = coords2.T
        ax.scatter3D(points2[0], points2[1], points2[2], color='blue')
        for i in range(len(coords)):
            ax.text(coords[i][0], coords[i][1], coords[i][2], str(i))
        ax.set_xlabel('X axis')
        ax.set_ylabel('Y axis')
        ax.set_zlabel('Z axis')
        ax.set_zlim(-1, 45)

        fig = plt.figure()
        gs = fig.add_gridspec(len(data), hspace=0)
        axs = gs.subplots(sharex=True, sharey=True)

        for i in range(len(axs)):
            ax = axs[i]
            ax.set_xlim((0, 1024))
            ax.set_ylim((0, 768))
            x, y = np.array(data[i]).T
            ax.scatter(x, y, c=colors)
            # ax.plot(x, y)
            for j in range(len(objp)):
                ax.text(data[i][j][0], data[i][j][1] + 30, str(objp[j]), horizontalalignment='center')

        plt.show()
    #
    #     # Triangulate 3d world points, based on the two-camera calibration
    #     # This step can run in realtime
    #     wp12 = cv2.triangulatePoints(p12_1, p12_2, np.array(data[0][0]).T, np.array(data[1][0]).T)
    #     wp13 = cv2.triangulatePoints(p13_1, p13_2, np.array(data[2][0]).T, np.array(data[1][0]).T)
    #
    #     cp12 = homogeneous_to_cartesian(wp12)
    #     cp13 = homogeneous_to_cartesian(wp13)
    #     dist = np.sqrt(np.sum(np.array(cp12) - np.array(cp13)) ** 2)
    #     print("WELT:")
    #     print(dist, cp12, cp13)
    #     plt.show()
    #     print(homogeneous_to_cartesian(
    #         cv2.triangulatePoints(p12_1, p12_2, np.array(data[1][1]).T, np.array(data[0][1]).T)))
    #     print(homogeneous_to_cartesian(
    #         cv2.triangulatePoints(p12_1, p12_2, np.array(data[1][2]).T, np.array(data[0][2]).T)))


def calibrate_camera(files: list[str]):
    """
    Calibrate each camera for its intrinsic and extrinsic parameters
    :param files: list of file names in ./wii_calib folder
    :return: (cam_dist_coeff, cam_matrix)
    """
    cam_img_points, cam_obj_points = getPointsForCamera(files)
    error, cam_matrix, cam_dist_coeff, _, _ = cv2.calibrateCamera(cam_obj_points, cam_img_points, imageSize,
                                                                        np.zeros((3, 3), np.float32),
                                                                        np.zeros(4, np.float32))
    print('error', error)
    return cam_dist_coeff, cam_matrix


def stereo_calibrate(idx1: int, idx2: int, cam1_matrix, cam1_dist_coeff,
                     cam2_matrix, cam2_dist_coeff):
    """
    Calibrate two cameras to each other
    Rectify (?) each two-camera calibration
    :param ix1: index of first camera
    :param idx2: index of second camera
    :param cam1_matrix: first camera matrix
    :param cam1_dist_coeff: first camera distance coefficients
    :param cam2_matrix: second camera matrix
    :param cam2_dist_coeff: second camera distance coefficients
    :return: (p1, p2)
    """

    cam12_1_img_points, cam12_2_img_points, obj_points12 = getPointsForCameras(idx1, idx2)

    error, _, _, _, _, r, t, e, f = cv2.stereoCalibrate(obj_points12, cam12_1_img_points, cam12_2_img_points,
                                                        cam1_matrix, cam1_dist_coeff,
                                                        cam2_matrix, cam2_dist_coeff, imageSize)

    print('stereo error', idx1, idx2, len(obj_points12), error)
    return r, t


def triangulate(p1, p2, point1: [float, float], point2: [float, float]):
    A = [point1[1] * p1[2, :] - p1[1, :],
         p1[0, :] - point1[0] * p1[2, :],
         point2[1] * p2[2, :] - p2[1, :],
         p2[0, :] - point2[0] * p2[2, :]
         ]
    A = np.array(A).reshape((4, 4))
    # print('A: ')
    # print(A)

    B = A.transpose() @ A
    U, s, Vh = linalg.svd(B, full_matrices=False)
    return Vh[3, 0:3] / Vh[3, 3]


def calibrate(idx1: int, idx2: int):
    cam1_dist_coeff, cam1_matrix = calibrate_camera(calib_files[idx1])
    cam2_dist_coeff, cam2_matrix = calibrate_camera(calib_files[idx2])

    r, t = stereo_calibrate(idx1, idx2,
                            cam1_matrix, cam1_dist_coeff,
                            cam2_matrix, cam2_dist_coeff)

    RT1 = np.concatenate([np.eye(3), [[0], [0], [0]]], axis=-1)
    P1 = cam1_matrix @ RT1

    RT2 = np.concatenate([r, t], axis=-1)
    P2 = cam2_matrix @ RT2

    return P1, P2


def homogeneous_to_cartesian(wp: [[float], [float], [float], [float]]):
    [[x], [y], [z], [w]] = wp
    return [x / w, y / w, z / w]


def getPointsForCamera(files: list[str]):
    camObjPoints = []
    camImgPoints = []
    imgPoint = []
    objPoint = []
    for file in files:
        with open(f'wii_calib/{file}.txt', 'r') as f:
            data = ast.literal_eval(f.read())
            for j in range(len(data[0])):
                (x, y) = data[0][j]
                if x > -1 and y > -1:
                    imgPoint.append([x, y])
                    objPoint.append(objp[j])
            camImgPoints.append(np.array(imgPoint, dtype=np.float32))
            camObjPoints.append(np.array(objPoint, dtype=np.float32))
    return camImgPoints, camObjPoints


def getPointsForCameras(idx1: int, idx2: int):
    objPoints = []

    cam1ImgPoints = []
    objPoint = []
    img1Point = []
    img2Point = []
    cam2ImgPoints = []

    for file in stereo_calib_files:
        with open(f'stereo_improved/{file}', 'r') as f:
            data = ast.literal_eval(f.read())
            j = 0
            for d1, d2 in zip(data[idx1], data[idx2]):
                (x1, y1) = d1
                (x2, y2) = d2
                if x1 > -1 and y1 > -1 and x2 > -1 and y2 > -1:
                    img1Point.append([x1, y1])
                    img2Point.append([x2, y2])
                    objPoint.append(objp[j])
                j += 1
        print(len(objPoint))
        if len(objPoint) > 0:
            cam1ImgPoints.append(np.array(img1Point, dtype=np.float32))
            cam2ImgPoints.append(np.array(img2Point, dtype=np.float32))
            objPoints.append(np.array(objPoint, dtype=np.float32))
            objPoint = []
            img1Point = []
            img2Point = []
    return cam1ImgPoints, cam2ImgPoints, objPoints


if __name__ == '__main__':
    main()
