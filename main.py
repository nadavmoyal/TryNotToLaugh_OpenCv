import cv2
import cvzone

from cvzone.FaceMeshModule import FaceMeshDetector
import time

cap = cv2.VideoCapture(0)
failsCap = cv2.VideoCapture("fails.mp4")
detector = FaceMeshDetector(maxFaces=1)
imgBackground = cv2.imread("cleanBackground.png")
name = cv2.imread("name.png", cv2.IMREAD_UNCHANGED)

# plotY = LivePlot(640, 360, [20, 50], invert=True)

# arguments
idList = [78, 191, 80, 81, 82, 13, 14, 312, 311, 402, 310, 317, 318, 415, 324, 308, 324, 87, 178, 95]
ratioList = []
loughCounter = 0
counter = 0
total = 0
i = 0
gameOver = False
color = (250, 0, 0)
start = time.time()


def gameOverFunc():
    cvzone.putTextRect(img, "Game Over", [100, 200],
                       scale=5, thickness=5, offset=10, colorR=(0, 0, 0))
    cvzone.putTextRect(img, f'Your Score:{total}', [20, 300],
                       scale=5, thickness=5, offset=10, colorR=(0, 0, 0))


while True:

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    succ, fails = failsCap.read()
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img, faces = detector.findFaceMesh(img, draw=False)

    if gameOver:
        gameOverFunc()
    else:
        if faces:
            face = faces[0]
            for id in idList:
                cv2.circle(img, face[id], 5, (0,200,0))

            leftUp = face[13]
            leftDown = face[14]
            leftLeft = face[78]
            leftRight = face[308]
            lenghtVer, _ = detector.findDistance(leftUp, leftDown)
            lenghtHor, _ = detector.findDistance(leftLeft, leftRight)

            ratio = int((lenghtVer / lenghtHor) * 100)
            ratioList.append(ratio)
            if len(ratioList) > 3:
                ratioList.pop(0)
            ratioAvg = sum(ratioList) / len(ratioList)
            hpLine = cv2.line(img, [50, 50], [300 - i, 50],(0, 0, 255), 30)

            if ratioAvg >= 10 and counter == 0:
                i += 15
                if (i >= 280) and gameOver == False:
                    print("game over")
                    end = time.time()
                    total = round(end - start, 2)
                    total = int(total * 5.3)
                    gameOver = True
                    continue
                loughCounter += 1
                counter = 1
            if counter != 0 and gameOver == False:
                counter += 1
                if counter > 5:
                    counter = 0
                    color = (0, 0, 255)
                    cvzone.putTextRect(img, f'Lough Alert', (10, 120),colorR=color, offset=4,scale=2)


            cvzone.putTextRect(img, f'HP:', (10, 60),
                               scale=2, colorR=(0, 0, 255), offset=5)


            # imgPlot = plotY.update(ratioAvg, color)
            img = cv2.resize(img, (720, 480))
            fails = cv2.resize(fails, (720, 480))
            # img = cv2.addWeighted(img, 0.4, imgBackground, 0.4, 0)
            imgStack = cvzone.stackImages([fails, img], 2, 1)
            cv2.imshow("FailsVideo", fails)
            img = cvzone.overlayPNG(img, name, [7 ,390])

    # else:
    #     img = cv2.resize(img, (640, 360))
    #     imgStack = cvzone.stackImages([img, img], 2, 1)

    cv2.imshow("Challenge", img)
    cv2.waitKey(2)
