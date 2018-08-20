from Box2D import *

world = b2World(gravity = (0, -10), doSleep = True)

ground1BodyDef = b2BodyDef()
ground1BodyDef.position.Set(0, 0)
ground1Body = world.CreateBody(ground1BodyDef)
ground1Shape = b2PolygonShape()
ground1Shape.SetAsBox(50, 1)
ground1Body.CreateFixture(shape = ground1Shape)

box1BodyDef = b2BodyDef()
box1BodyDef.type = b2_dynamicBody
box1BodyDef.position.Set(0, 5)
box1Body = world.CreateBody(box1BodyDef)
box1Shape = b2PolygonShape()
box1Shape.SetAsBox(1, 1)
box1FixtureDef = b2FixtureDef()
box1FixtureDef.shape = box1Shape
box1FixtureDef.density = 1
box1FixtureDef.friction = 0.3
box1Body.CreateFixture(box1FixtureDef)

timeStep = 1.0 / 60
velIters = 6
posIters = 2

for i in range(60):
    world.Step(timeStep, velIters, posIters)
    world.ClearForces()
    print(box1Body.position)
