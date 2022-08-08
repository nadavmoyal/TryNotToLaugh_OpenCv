# Imports
import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
import time
import pygame
from pygame import mixer

# Initialization of the videos and the face detector:
cap = cv2.VideoCapture(0)
failsCap = cv2.VideoCapture("sources/failsVideo.mp4")
blue = cv2.VideoCapture("sources/blue.mp4")
lightBlue = cv2.VideoCapture("sources/light blue.mp4")
background = cv2.imread("sources/background.jpg", cv2.IMREAD_UNCHANGED)
detector = FaceMeshDetector(maxFaces=1)

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


# Setting the resolution of the elements
def screen_resolution():
    background[72:357, 12:547] = cv2.resize(light_background, (535, 285))
    background[74:562, 559:1247] = cv2.resize(fails, (688, 488))
    background[90:337, 26:534] = cv2.resize(img, (508, 247))
    background[450:650, 20:520] = cv2.resize(blue_background, (500, 200))
    cv2.imshow("background", background)


# laugh detector algorithm
def laugh_detector_algorithm():
    middle_up = face[13]
    middle_down = face[14]
    left = face[78]
    right = face[308]
    vertical, _ = detector.findDistance(middle_up, middle_down)
    horizontal, _ = detector.findDistance(left, right)
    proportion = int((vertical / horizontal) * 100)
    ratioList.append(proportion)
    if len(ratioList) > 3:
        ratioList.pop(0)
    return sum(ratioList) / len(ratioList)


# displays "You win" on the screen:
def you_win_screen():
    screen_resolution()
    cvzone.putTextRect(background, "You Win", [677, 330], scale=7, thickness=7, offset=13, colorR=(0, 0, 0))
    cv2.imshow("background", background)


# Playing the "You Win" and "Victory" sounds:
def you_win_sound():
    failsAudio.stop()
    lose = mixer.Sound('sources/victory.wav')
    lose.set_volume(0.2)
    lose.play()
    time.sleep(1)
    win_sound = mixer.Sound('sources/youWin.wav')
    win_sound.play()
    return False


# Shows the result when the game is over:
def game_over_screen():
    screen_resolution()
    cvzone.putTextRect(background, "Game Over", [633, 280], scale=6, thickness=5, offset=9, colorR=(0, 0, 0))
    cvzone.putTextRect(background, f'Your Score:{total}', [605, 375], scale=5, thickness=5, offset=9, colorR=(0, 0, 0))
    cv2.imshow("background", background)


# Playing the "you lose" and "game over" sounds:
def game_over_sound():
    failsAudio.stop()
    lose = mixer.Sound('sources/LoseSoundEffect.wav')
    lose.play()
    time.sleep(1)
    mixer.Sound('sources/gameOverSound.wav').play()
    return False


# Running the game:
while True:
    # Initializes the face recognition and the fails video.
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success_fails, fails = failsCap.read()
    success_blue, blue_background = blue.read()
    success_light, light_background = lightBlue.read()
    success_img, img = cap.read()
    img = cv2.flip(img, 1)  # flip the camera (mirror effect).
    img, faces = detector.findFaceMesh(img, draw=False)

    # In case that the player has won
    if winner:
        if firstRound:
            firstRound = you_win_sound()
        you_win_screen()

    # In case that the player has lost
    if gameOver:
        if firstRound:
            firstRound = game_over_sound()
        game_over_screen()

    else:
        # Displays a green points around the player's mouth
        if faces:
            face = faces[0]
            for index in mouthPoints:
                cv2.circle(img, face[index], 3, (0, 200, 0))

            # laugh detector algorithm
            ratioAvg = laugh_detector_algorithm()

            # Check if the person is laughing, and reduce the HP scale.
            # If the ratioAvg is more than 10 it's mean that his mouth is open -> laughing.
            if ratioAvg >= 10:
                i += 15

                # Displays a white rectangle around the player's screen
                if winner is False:
                    cv2.rectangle(light_background, pt1=(20, 27), pt2=(941, 506), color=(255, 255, 255), thickness=12)

                if (i >= 850) and gameOver is False and winner is False:
                    # In "Game Over" case:
                    end = time.time()  # Stop the time for calculate the score.
                    total = round(end - start, 2)  # round the time for calculate the score
                    total = int(total * 5.3)
                    gameOver = True  # End the game.

            timeLimit = round(time.time() - start, 0)
            if timeLimit > 140:  # If the player watched the all video
                end = time.time()  # Stop the time for calculate the score.
                winner = True  # End the game.

            # Drawing the HP scale.
            # Variable j is for changing the color of the HP scale
            if not winner:
                if i < 450:
                    j = i * 0.1
                else:
                    j = i * 0.3
                cv2.line(blue_background, [50, 50], [900 - i, 50], (0, 255 - j, i), 100)

            # Show all the elements
            screen_resolution()

    cv2.waitKey(2)
