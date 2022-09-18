import math

from ObjLoader import OBJ
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from FunctionLibrary import *

class Transform:
    def __init__(self, position = [0, 0, 0], rotation = [0, 0, 0], scale = [1, 1, 1]):
        self.position = position
        self.rotation = rotation
        self.scale = scale

class GameObjectManager:
    def __init__(self):
        self.gameObjects = []

    def createGameObject(self, transform, meshPath = "", velocity = [0, 0, 0], mass = 1, bGravityEnabled = False):
        go = GameObject(transform, meshPath, velocity, mass, bGravityEnabled)
        self.addGameObject(go)
        return go

    def addGameObject(self, gameObject):
        self.gameObjects.append(gameObject)

    def removeGameObject(self, gameObject):
        self.gameObjects.remove(gameObject)

    def tick(self, deltaTime):
        for go in self.gameObjects:
            go.tick(deltaTime)


class GameObject:
    def __init__(self, transform, meshPath = "", velocity = [0, 0, 0], mass = 1, bGravityEnabled = False):
        self.transform = transform
        if meshPath != "":
            self.mesh = OBJ(meshPath)
        else:
            self.mesh = None
        self.velocity = velocity
        self.mass = mass
        self.energyLoss = 0.3
        self.bGravityEnabled = bGravityEnabled
        self.bDebug = True
        self.deltaTime = 0

    def tick(self, deltaTime):
        self.deltaTime = deltaTime
        if self.bGravityEnabled:
            self.velocity = np.array(self.velocity) + np.array([0, -0.00025, 0]) * self.deltaTime  # 应用重力
        else:
            self.velocity[1] = 0  # 清除竖直方向的速度

        self.transform.position = np.array(self.transform.position) + np.array(self.velocity) * self.deltaTime * 0.05  # 物体的移动
        self.render() # 渲染物体

    def render(self):
        # 变换矩阵
        glTranslatef(self.transform.position[0], self.transform.position[1], self.transform.position[2])
        glRotatef(self.transform.rotation[0], 1,0,0)
        glRotatef(self.transform.rotation[1], 0,1,0)
        glRotatef(self.transform.rotation[2], 0,0,1)

        # 如果物体拥有网格，则绘制网格，否则绘制一个glut球体
        if self.mesh != None:
            glCallList(self.mesh.gl_list)
        else:
            glutSolidSphere(0.1, 24, 24)

        glRotatef(-self.transform.rotation[2], 0,0,1)
        glRotatef(-self.transform.rotation[1], 0,1,0)
        glRotatef(-self.transform.rotation[0], 1,0,0)
        glTranslatef(-self.transform.position[0], -self.transform.position[1], -self.transform.position[2])

    def onCollision(self, other, selfLocation, otherLocation):
        # 移回进入AABB前的位置
        self.transform.position = np.array(self.transform.position) - np.array(self.velocity) * self.deltaTime * 0.05
        # 动量守恒公式，非弹性碰撞
        # 获取法线速度
        selfNormalVelocity = self.getCollisionNormalVelocity(selfLocation, otherLocation)
        otherNormalVelocity = other.getCollisionNormalVelocity(otherLocation, selfLocation)
        # 计算新的法线速度
        newNormalVelocity = self.energyLoss * np.array(
            ((self.mass - other.mass) * np.array(selfNormalVelocity) + 2 * other.mass * np.array(otherNormalVelocity))) * (
                                    1 / (self.mass + other.mass))
        # 速度减去之前的法线速度，加上新的法线速度
        # 如果速度接近0，则不进行修改，避免抖动
        if getMagnitude(newNormalVelocity) > 0.0001:
            self.velocity = np.array(self.velocity) - np.array(selfNormalVelocity) + newNormalVelocity


    def getCollisionNormalVelocity(self, selfLocation, otherLocation):
        if getMagnitude(self.velocity) == 0:
            return self.velocity
        # 法线方向单位向量
        normalDirection = normalize(np.array(otherLocation) - np.array(selfLocation))
        # 归一化的速度
        normalizedVelocity = normalize(np.array(self.velocity))
        # 速度和法线方向的夹角
        cos = np.dot(normalizedVelocity, normalDirection)
        # 法线速度的模
        normalVelocityMagnitude = getMagnitude(self.velocity) * cos
        # 法线速度
        normalVelocity = normalVelocityMagnitude * normalDirection
        return normalVelocity

    # 获取AABB的最大最小坐标
    def getAABB(self):
        x_min, y_min, z_min, x_max, y_max, z_max = 0, 0, 0, 0, 0, 0
        for vertex in self.mesh.vertices:
            if vertex[0] < x_min:
                x_min = vertex[0]
            if vertex[0] > x_max:
                x_max = vertex[0]

            if vertex[1] < y_min:
                y_min = vertex[1]
            if vertex[1] > y_max:
                y_max = vertex[1]

            if vertex[2] < z_min:
                z_min = vertex[2]
            if vertex[2] > z_max:
                z_max = vertex[2]

        return np.array((x_min, y_min, z_min)) + np.array(self.transform.position), np.array((x_max, y_max, z_max)) + np.array(self.transform.position)

    # 检测一个点是否在AABB中
    def checkCollision(self, other):
        point = other.transform.position
        #print(point)
        # AABB的坐标最小点
        min, max = self.getAABB()
        #if self.bDebug:
            #print("AABB min : " + str(min))
            #print("AABB max : " + str(max))
        # 如果一个点的坐标处于最小点和最大点之间，说明其处于AABB中
        if point[0] > min[0] and point[1] > min[1] and point[2] > min[2]:
            if point[0] < max[0] and point[1] < max[1] and point[2] < max[2]:
                # 记录打入AABB中的位置
                collideLocation = point
                # 将撞击点和撞击点竖直向上的一个位置传递到onCollision方法中，用于计算碰撞点位置和碰撞平面法线（竖直向上）
                self.onCollision(other, collideLocation, np.array([0, 0.1, 0]) + np.array(collideLocation))
                other.onCollision(self, np.array([0, 0.1, 0]) + np.array(collideLocation), collideLocation)
                return True
        return False

