data = [
    [(584.2385786802031, 172.46192893401016), (682.0, 233.95939086294416), (773.010152284264, 287.98477157360406),
     (859.015306122449, 337.0), (498.0, 271.3265306122449), (597.3128205128205, 324.0), (689.7179487179487, 369.0),
     (776.0204081632653, 411.9642857142857), (417.0, 355.0), (520.0, 403.0051020408163), (611.2233502538071, 440.0),
     (696.0, 480.0)],
    [(544.0, 296.0), (480.0, 368.0), (-1.0, -1.0), (376.0, 488.0), (408.0, 264.0), (352.0, 344.0), (312.0, 408.0),
     (-1.0, -1.0), (269.1015228426396, 230.0), (216.0, 314.0), (184.0, 384.0), (-1.0, -1.0)],
    [(317.995, 196.34), (448.5925, 161.1875), (592.42, 119.0), (755.1975, 75.5), (367.0, 337.04),
     (498.45137157107234, 303.02493765586036), (639.0, 267.815), (800.215, 219.175), (407.0, 468.0), (542.0, 441.0),
     (676.9625935162095, 404.8927680798005), (830.9501246882793, 370.9800498753117)]]

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

chessboard_size = (4, 3)

objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), dtype=np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2) * 2

colors = range(len(objp))

imageSize = (1024, 768)


def main():
    print(len(data[0]), len(objp))

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

    cam1ImgPoints, cam1ObjPoints = getPointsForCamera(0)
    cam2ImgPoints, cam2ObjPoints = getPointsForCamera(1)
    cam3ImgPoints, cam3ObjPoints = getPointsForCamera(2)

    # Calibrate each camera for its intrinsic and extrinsic parameters
    error1, cam1Matrix, cam1DistCoeff, _, _ = cv2.calibrateCamera(cam1ObjPoints, cam1ImgPoints, imageSize,
                                                                  np.zeros((3, 3), np.float32), np.zeros(4, np.float32))
    error2, cam2Matrix, cam2DistCoeff, _, _ = cv2.calibrateCamera(cam2ObjPoints, cam2ImgPoints, imageSize,
                                                                  np.zeros((3, 3), np.float32), np.zeros(4, np.float32))
    error3, cam3Matrix, cam3DistCoeff, _, _ = cv2.calibrateCamera(cam3ObjPoints, cam3ImgPoints, imageSize,
                                                                  np.zeros((3, 3), np.float32), np.zeros(4, np.float32))

    print(error1, error2, error3)

    # Calibrate two cameras to each other
    cam12_1ImgPoints, cam12_2ImgPoints, objPoints12 = getPointsForCameras(0, 1)
    cam13_1ImgPoints, cam13_2ImgPoints, objPoints13 = getPointsForCameras(0, 2)
    error12, _, _, _, _, r12, t12, e12, f12 = cv2.stereoCalibrate(objPoints12, cam12_1ImgPoints, cam12_2ImgPoints,
                                                                  cam1Matrix, cam1DistCoeff,
                                                                  cam2Matrix, cam2DistCoeff, imageSize)
    error13, _, _, _, _, r13, t13, e13, f13 = cv2.stereoCalibrate(objPoints13, cam13_1ImgPoints, cam13_2ImgPoints,
                                                                  cam2Matrix, cam2DistCoeff,
                                                                  cam3Matrix, cam3DistCoeff, imageSize)
    print(error12, error13)

    # Rectify (?) each two-camera calibration
    _, _, p12_1, p12_2, q12, _, _ = cv2.stereoRectify(cam1Matrix, cam1DistCoeff, cam2Matrix, cam2DistCoeff, imageSize,
                                                      r12, t12)
    _, _, p13_1, p13_2, q13, _, _ = cv2.stereoRectify(cam1Matrix, cam1DistCoeff, cam3Matrix, cam3DistCoeff, imageSize,
                                                      r13, t13)

    print(p12_1, p12_2, q12)
    print(p13_1, p13_2, q13)

    # Triangulate 3d world points, based on the two-camera calibration
    # This step can run in realtime
    wp12 = cv2.triangulatePoints(p12_1, p12_2, np.array(data[0][0]).T, np.array(data[1][0]).T)
    wp13 = cv2.triangulatePoints(p13_1, p13_2, np.array(data[0][0]).T, np.array(data[2][0]).T)

    cp12 = homogeneous_to_cartesian(wp12)
    cp13 = homogeneous_to_cartesian(wp13)
    dist = np.sqrt(np.sum(np.array(cp12) - np.array(cp13)) ** 2)
    print("WELT:")
    print(dist, cp12, cp13)
    plt.show()


def homogeneous_to_cartesian(wp: [[float], [float], [float], [float]]):
    [[x], [y], [z], [w]] = wp
    return [x / w, y / w, z / w]


def getPointsForCamera(index: int):
    camObjPoints = []
    camImgPoints = []
    imgPoint = []
    objPoint = []
    for j in range(len(data[index])):
        (x, y) = data[index][j]
        if x > -1 and y > -1:
            imgPoint.append([x, y])
            objPoint.append(objp[j])
    camImgPoints.append(np.array(imgPoint, dtype=np.float32))
    camObjPoints.append(np.array(objPoint, dtype=np.float32))
    return camImgPoints, camObjPoints


def getPointsForCameras(index1: int, index2: int):
    objPoints = []
    objPoint = []

    cam1ImgPoints = []
    img1Point = []
    cam2ImgPoints = []
    img2Point = []
    for j in range(len(data[index1])):
        (x1, y1) = data[index1][j]
        (x2, y2) = data[index2][j]
        if x1 > -1 and y1 > -1 and x2 > -1 and y2 > -1:
            img1Point.append([x1, y1])
            img2Point.append([x2, y2])
            objPoint.append(objp[j])
    cam1ImgPoints.append(np.array(img1Point, dtype=np.float32))
    cam2ImgPoints.append(np.array(img2Point, dtype=np.float32))
    objPoints.append(np.array(objPoint, dtype=np.float32))
    return cam1ImgPoints, cam2ImgPoints, objPoints


if __name__ == '__main__':
    main()
