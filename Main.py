import math
import random

from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from FunctionLibrary import *

from GameObject import *
from ObjLoader import *



if __name__ == '__main__':

    print("Loading Game...")
    pygame.init()
    size = (960,540)
    hx = size[0]/2
    hy = size[1]/2
    screen = pygame.display.set_mode(size, OPENGL | DOUBLEBUF)
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    print("Setting OpenGL...")
    glutInit()
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, 0.1,0.1,0.1,1)
    glEnable(GL_LIGHTING)
    glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (1, 1, 1, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60.0, size[0]/size[1], 0.001, 100.0)
    glMatrixMode(GL_MODELVIEW)


    print("Loading Models...")
    gameObjectManager = GameObjectManager()
    character = gameObjectManager.createGameObject(Transform([0, 0, 0], [0, 90, 0], [1, 1, 1]), "Character.obj", [0, 0, 0], 1)
    ground = gameObjectManager.createGameObject(Transform([0, -2, -5], [0, 0, 0], [1, 1, 1]), "Ground.obj", [0, 0, 0], 100000)
    bullets = []
    balls = []

    balls.append(gameObjectManager.createGameObject(Transform([0, 1, -5]), "Meshes\Ball_1.obj", [0, 0, 0], 0.1))
    balls.append(gameObjectManager.createGameObject(Transform([0, 1, -5]), "Meshes\Ball_2.obj", [0, 0, 0], 0.1))
    balls.append(gameObjectManager.createGameObject(Transform([0, 1, -5]), "Meshes\Ball_3.obj", [0, 0, 0], 0.1))
    balls.append(gameObjectManager.createGameObject(Transform([0, 1, -5]), "Meshes\Ball_4.obj", [0, 0, 0], 0.1))
    balls.append(gameObjectManager.createGameObject(Transform([0, 1, -5]), "Meshes\Ball_5.obj", [0, 0, 0], 0.1))
    balls.append(gameObjectManager.createGameObject(Transform([0, 1, -5]), "Meshes\Ball_6.obj", [0, 0, 0], 0.1))
    balls.append(gameObjectManager.createGameObject(Transform([0, 1, -5]), "Meshes\Ball_7.obj", [0, 0, 0], 0.1))
    balls.append(gameObjectManager.createGameObject(Transform([0, 1, -5]), "Meshes\Ball_8.obj", [0, 0, 0], 0.1))
    balls.append(gameObjectManager.createGameObject(Transform([0, 1, -5]), "Meshes\Ball_10.obj", [0, 0, 0], 0.1))
    balls.append(gameObjectManager.createGameObject(Transform([0, 1, -5]), "Meshes\Ball_9.obj", [0, 0, 0], 0.1))

    print("Loading Data...")

    # Character
    moveSpeed = 0.1
    chargeTime = 0
    bFired = False
    bInfinityAmmo = False
    bCharging = False
    bGameOver = True

    # Camera
    yaw, pitch = (0, 0)
    cameraPos = np.array([0, 0, 0])
    cameraFront = np.array([0, 0, 1])
    cameraUp = np.array([0, 1, 0])
    mouseSensitivity = 0.003

    print("Done!")
    bGameOver = False

    while True:
        deltaTime = clock.tick(60)

        # BackGround
        glClearColor(0.4, 0.6, 0.7, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # MouseInput
        for e in pygame.event.get():
            # 开始蓄力
            if e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    if not bFired or bInfinityAmmo:
                        bCharging = True
            # 结束蓄力
            elif e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    if not bFired or bInfinityAmmo:
                        bFired = True
                        # 枪口位置
                        offset = 0.6
                        muzzle = [cameraPos[0] + offset * cameraFront[0], cameraPos[1] + offset * cameraFront[1], cameraPos[2] + offset * cameraFront[2]]
                        # 将蓄力时间映射为速度乘数
                        speedMultiplier = (chargeTime + 1000) * 0.00015
                        # 生成子弹
                        bullets.append(gameObjectManager.createGameObject(Transform(muzzle), "", speedMultiplier * np.array([cameraFront[0], cameraFront[1], cameraFront[2]]), 100, True))
                        print("Fire!")
                        bCharging = False
                        chargeTime = 0
            # 摄像机输入
            elif e.type == MOUSEMOTION:
                i, j = e.rel
                yaw += i * mouseSensitivity * deltaTime * 0.05
                pitch -= j * mouseSensitivity * deltaTime * 0.05
                if pitch > 0.6:
                    pitch = 0.6
                if pitch < -0.6:
                    pitch = -0.6

        # KeyInput
        keys = pygame.key.get_pressed()
        # 移动输入
        if keys[K_w]:
            newMovement = np.array(cameraFront)
            newMovement[1] -= newMovement[1]
            cameraPos = np.array(cameraPos) + normalize(newMovement) * moveSpeed * deltaTime * 0.05
        if keys[K_s]:
            newMovement = np.array(cameraFront)
            newMovement[1] -= newMovement[1]
            cameraPos = np.array(cameraPos) - normalize(newMovement) * moveSpeed * deltaTime * 0.05
        if keys[K_a]:
            newMovement = np.array(np.cross(cameraFront, cameraUp))
            newMovement[1] -= newMovement[1]
            cameraPos = np.array(cameraPos) - normalize(newMovement) * moveSpeed * deltaTime * 0.05
        if keys[K_d]:
            newMovement = np.array(np.cross(cameraFront, cameraUp))
            newMovement[1] -= newMovement[1]
            cameraPos = np.array(cameraPos) + normalize(newMovement) * moveSpeed * deltaTime * 0.05
        if keys[K_ESCAPE]:
            sys.exit() # 退出游戏
        if keys[K_r]:
            for ball in balls:
                ball.bGravityEnabled = False
                ball.transform.position = [0, 1, -5]
                ball.velocity = [0, 0, 0]
            for bullet in bullets:
                gameObjectManager.removeGameObject(bullet)
                del bullet
                bullets = []
                bFired = False
                bGameOver = False

        if keys[K_f]:
            bInfinityAmmo = not bInfinityAmmo # 无限火力

        # Game Logic
        # Camera
        cameraFront = [math.sin(yaw) * math.cos(pitch), math.sin(pitch), -math.cos(pitch) * math.cos(yaw)]
        gluLookAt(cameraPos[0], cameraPos[1], cameraPos[2],
                  cameraPos[0] + cameraFront[0] , cameraPos[1] + cameraFront[1], cameraPos[2] + cameraFront[2]
                  , 0, 1, 0)

        # 枪的模型移动到摄像机位置
        character.transform.position = (cameraPos[0], cameraPos[1] - 0.25, cameraPos[2])
        character.transform.rotation = (0, -yaw * 180 / math.pi + 90, pitch * 60)

        # 蓄力时长计算
        if bCharging:
            # 最长蓄力时间为1s
            if chargeTime <= 1000:
                chargeTime += deltaTime
                if chargeTime > 1000:
                    chargeTime = 1000
            print(str(chargeTime / 10) + "%")
        # 无限火力蓄力修正
        if bInfinityAmmo:
            chargeTime = 1000
        # 游戏结束判定
        if not bGameOver:
            if bFired and not bInfinityAmmo:
                if bullets[0].transform.position[1] < -2:
                    bGameOver = True
                    print("Game Over!")

        else:
            # 没打着
            if not balls[0].bGravityEnabled:
                drawText(hx -30, hy, "Missed...")
                drawText(hx -40, hy - 36, "Try Again!")
            # 打中了
            else:
                drawText(hx -120, hy, "OHHHHHHHHHHHHHHHHHH")
                drawText(hx -140, hy - 36, "NI ZUO DE HAO A, NI ZUO DE HAO")

        # Collision Check
        # 地面
        for go in gameObjectManager.gameObjects:
            if go != ground:
                ground.checkCollision(go)

        # 子弹和球
        if len(bullets) != 0:
            for ball in balls:
                if ball.bGravityEnabled:
                    break

                # 如果有子弹击中任意碎片，则开启所有碎片的重力，并在现有速度的基础上添加一个随机爆炸速度，取值范围0.05 * (-1 ~ 1)
                else:
                    for bullet in bullets:
                        if ball.checkCollision(bullet):
                            for otherBall in balls:
                                otherBall.bGravityEnabled = True
                                otherBall.velocity = 0.05 * np.array([2 * np.random.random() - 1, 2 * np.random.random()
                                                                      - 1, 2 * np.random.random() - 1]) \
                                                                        + np.array(bullet.velocity) # 爆炸
                            break

        # Render Game Object
        gameObjectManager.tick(deltaTime)

        # Render UI
        drawText(20, 50, "Press R to Restart")
        drawText(20, 20, "Press F to Enable Infinity Ammo")
        drawText(20, 500, "Charging : " + str(chargeTime / 10) + "%")

        pygame.display.flip()

