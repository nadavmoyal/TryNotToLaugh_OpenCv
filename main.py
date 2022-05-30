import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
import time
import pygame
from pygame import mixer

cap = cv2.VideoCapture(0)
failsCap = cv2.VideoCapture("fails.mp4")
detector = FaceMeshDetector(maxFaces=1)
name = cv2.imread("name.png", cv2.IMREAD_UNCHANGED)

# variables
mouthPoints = [78, 191, 80, 81, 82, 13, 14, 312, 311, 402, 310, 317, 318, 415, 324, 308, 324, 87, 178, 95]
ratioList = []
counter = 0
total = 0
i = 0
once = True
gameOver = False
start = time.time()


def game_over_sound(once):
    pygame.init()
    pygame.mixer.init()
    gos = mixer.Sound('gameOverSound.wav')
    gos.play()
    return False


def game_over_screen():
    cvzone.putTextRect(img, "Game Over", [100, 200], scale=5, thickness=5, offset=10, colorR=(0, 0, 0))
    cvzone.putTextRect(img, f'Your Score:{total}', [85, 300], scale=4, thickness=4, offset=10, colorR=(0, 0, 0))


while True:
    # Initializes the face recognition and the fails video.
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    succ, fails = failsCap.read()
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img, faces = detector.findFaceMesh(img, draw=False)

    if gameOver:
        if once:
            once = game_over_sound(once)
        else:
            game_over_screen()
            pass
    else:
        if faces:
            face = faces[0]
            for index in mouthPoints:
                cv2.circle(img, face[index], 3, (0, 200, 0))
            # laugh detector algorithm
            MiddleUp = face[13]
            MiddleDown = face[14]
            left = face[78]
            Right = face[308]
            Vertical, _ = detector.findDistance(MiddleUp, MiddleDown)
            Horizontal, _ = detector.findDistance(left, Right)
            proportion = int((Vertical / Horizontal) * 100)
            ratioList.append(proportion)
            if len(ratioList) > 3:
                ratioList.pop(0)
            ratioAvg = sum(ratioList) / len(ratioList)

            if ratioAvg >= 10 and counter == 0:
                i += 15
                if (i >= 280) and gameOver is False:
                    # In "Game Over" case:
                    end = time.time()  # Stop the time for calculate the score.
                    total = round(end - start, 2)
                    total = int(total * 5.3)
                    gameOver = True
                counter = 1
            # Displaying the "Laugh Alert".
            if counter != 0 and gameOver is False:
                counter += 1
                if counter > 5:
                    counter = 0
                    cvzone.putTextRect(img, f'Laugh Alert', (10, 120), colorR=(0, 0, 255), offset=4, scale=2, thickness=2)

            # Drawing the HP scale.
            cv2.line(img, [50, 50], [300 - i, 50], (0, 0, 255), 30)
            cvzone.putTextRect(img, f'HP:', (10, 60),
                               scale=2, colorR=(0, 0, 255), offset=5, thickness=2)

            # Initialization of the resolution and background:
            img = cv2.resize(img, (720, 480))
            fails = cv2.resize(fails, (720, 480))
            imgStack = cvzone.stackImages([fails, img], 2, 1)
            cv2.imshow("FailsVideo", fails)
            img = cvzone.overlayPNG(img, name, [7, 390])

    cv2.imshow("Challenge", img)
    cv2.waitKey(2)
