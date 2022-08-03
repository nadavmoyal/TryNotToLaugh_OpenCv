# Imports
import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
import time
import pygame
import numpy as np
from pygame import mixer

# Initialization of the videos and the face detector:
cap = cv2.VideoCapture(0)
failsCap = cv2.VideoCapture("sources/failsVideo.mp4")
detector = FaceMeshDetector(maxFaces=1)
name = cv2.imread("sources/lightName2.png", cv2.IMREAD_UNCHANGED)

# Variables
mouthPoints = [78, 191, 80, 81, 82, 13, 14, 312, 311, 402, 310, 317, 318, 415, 324, 308, 324, 87, 178, 95, 88]
ratioList = []
total = 0
i = 0
firstRound = True
gameOver = False
winner = False
start = time.time()

# Playing the background audio:
pygame.init()
pygame.mixer.init()
failsAudio = mixer.Sound('sources/failsAudio.wav')
failsAudio.play()


def you_win_screen():
    cvzone.putTextRect(fails, "You win", [150, 330], scale=10, thickness=12, offset=15, colorR=(0, 0, 0))
    f = cv2.resize(fails, (1280, 720))
    cv2.imshow("FailsVideo", f)

def you_win_sound():
    failsAudio.stop()
    lose = mixer.Sound('sources/victory.wav')
    lose.set_volume(0.2)
    lose.play()
    time.sleep(1)
    YouWinSound = mixer.Sound('sources/youWin.wav')
    YouWinSound.play()
    return False


# Playing the "you lose" and "game over" sounds:
def game_over_sound():
    failsAudio.stop()
    lose = mixer.Sound('sources/LoseSoundEffect.wav')
    lose.play()
    time.sleep(1)
    mixer.Sound('sources/gameOverSound.wav').play()
    return False


# Displaying the score when the game has ended:
def game_over_screen():
    cvzone.putTextRect(fails, "Game Over", [160, 250], scale=7, thickness=7, offset=10, colorR=(0, 0, 0))
    cvzone.putTextRect(fails, f'Your Score:{total}', [115, 360], scale=6, thickness=6, offset=10, colorR=(0, 0, 0))
    f = cv2.resize(fails, (1280, 720))
    cv2.imshow("FailsVideo", f)


def cameraFilter(frame):
    try:
        frame.shape[3]
    except IndexError:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    frame_h, frame_w, frame_c = frame.shape
    overlay = np.full((frame_h, frame_w, 4), (0, 0, 255, 1), dtype='uint8')
    cv2.addWeighted(overlay, 1, frame, 1.0, 0, frame)
    return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)




while True:
    # Initializes the face recognition and the fails video.
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    succ, fails = failsCap.read()
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img, faces = detector.findFaceMesh(img, draw=False)

    if winner:
        if firstRound:
            firstRound = you_win_sound()
        you_win_screen()

    if gameOver:
        if firstRound:
            firstRound = game_over_sound()
        game_over_screen()

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

            # Check if the person is laughing, and reduce the HP scale.
            # If the ratioAvg is more than 10 it's mean that his mouth is open -> laughing.
            if ratioAvg >= 10:
                i += 5
                # Displaying the "Laugh Alert"
                if winner is False:
                    if i % 2 ==0:
                        cvzone.putTextRect(fails, f'Laugh Alert', (10, 120), colorR=(0, 0, 255), offset=5, scale=3,
                                       thickness=3)
                        img = cameraFilter(img)

                if (i >= 240) and gameOver is False and winner is False:
                    # In "Game Over" case:
                    end = time.time()  # Stop the time for calculate the score.
                    total = round(end - start, 2)
                    total = int(total * 5.3)
                    gameOver = True  # End the game.

            timeLimit = round(time.time() - start, 0)
            if timeLimit > 140:
                end = time.time()  # Stop the time for calculate the score.
                total = round(end - start, 2)
                total = int(total * 5.3)
                winner = True

            # Drawing the HP scale.
            if not winner:
                cv2.line(fails, [50, 45], [300 - i, 45], (0, 0, 255), 37)
                cvzone.putTextRect(fails, f'HP:', (10, 60), scale=3, colorR=(0, 0, 255), offset=4, thickness=4)
                fails = cvzone.overlayPNG(fails, name, [7, 450])

            # Initialization of the resolution and background:
            img = cv2.resize(img, (1280, 720))
            fails = cv2.resize(fails, (1280, 720))
            fails[400:720, 820:1280] = cv2.resize(img, (460, 320))
            cv2.imshow("FailsVideo", fails)
    cv2.waitKey(2)
