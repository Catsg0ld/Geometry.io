# Copyright (c) Catsgold 
# License: GPL-3.0 

from vec2 import Vec2

def ClosestPointOnSegment(p, a, b):
    ab = b - a
    abLen2 = ab.x * ab.x + ab.y * ab.y
    if abLen2 < 1e-12:
        return a
    t = ((p.x - a.x) * ab.x + (p.y - a.y) * ab.y) / abLen2
    t = max(0.0, min(1.0, t))
    return a + ab * t

def PolygonCircleCollision(poly, circle, restitution=0.8, correction=0.8):
    points = poly.GetPoints()
    closest = None
    minDist2 = float("inf")
    n = len(points)

    circlePos = circle.transform.position
    radius = circle.transform.scale

    for i in range(n):
        p1 = Vec2(*points[i])
        p2 = Vec2(*points[(i + 1) % n])

        dist2 = (circlePos - p1).Length()**2
        if dist2 < minDist2:
            minDist2 = dist2
            closest = p1

        cp = ClosestPointOnSegment(circlePos, p1, p2)
        dist2 = (circlePos - cp).Length()**2
        if dist2 < minDist2:
            minDist2 = dist2
            closest = cp

    if closest is None:
        return False

    dist = minDist2 ** 0.5
    if dist >= radius:
        return False

    normal = (circlePos - closest).Normalized()
    if normal.Length() < 1e-8:
        normal = Vec2(0, 1)

    penetration = radius - dist
    circle.transform.position += normal * penetration * correction

    velAlongNormal = circle.physics.linearVelocity.Dot(normal)
    if velAlongNormal > 0:
        return False

    j = -(1 + restitution) * velAlongNormal
    j /= (1 / circle.physics.mass + 1 / poly.physics.mass)

    impulse = normal * j
    circle.physics.linearVelocity += impulse / circle.physics.mass
    poly.physics.linearVelocity -= impulse / poly.physics.mass

    r = closest - poly.transform.position
    angularImpulse = (r.x * normal.y - r.y * normal.x) * (velAlongNormal * restitution / poly.physics.mass) * 0.01
    poly.physics.angularVelocity += angularImpulse

    return True


def GetAABB(poly):
    points = poly.GetPoints()
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)

def AABBCollision(polyA, polyB):
    minAx, minAy, maxAx, maxAy = GetAABB(polyA)
    minBx, minBy, maxBx, maxBy = GetAABB(polyB)

    return not (maxAx < minBx or maxBx < minAx or maxAy < minBy or maxBy < minAy)

def ProjectPolygon(points, axis):
    minProj = float('inf')
    maxProj = -float('inf')
    for p in points:
        proj = Vec2(*p).Dot(axis)
        minProj = min(minProj, proj)
        maxProj = max(maxProj, proj)
    return minProj, maxProj

def Overlap1D(minA, maxA, minB, maxB):
    return min(maxA, maxB) - max(minA, minB)

def SATCollision(polyA, polyB):
    pointsA = polyA.GetPoints()
    pointsB = polyB.GetPoints()
    smallestOverlap = float('inf')
    collisionNormal = None

    for shape in (pointsA, pointsB):
        for i in range(len(shape)):
            p1 = Vec2(*shape[i])
            p2 = Vec2(*shape[(i+1) % len(shape)])
            edge = p2 - p1
            axis = Vec2(-edge.y, edge.x).Normalized()

            minA, maxA = ProjectPolygon(pointsA, axis)
            minB, maxB = ProjectPolygon(pointsB, axis)

            overlap = Overlap1D(minA, maxA, minB, maxB)
            if overlap <= 0:
                return None  
            elif overlap < smallestOverlap:
                smallestOverlap = overlap
                collisionNormal = axis

    centerA = polyA.transform.position
    centerB = polyB.transform.position
    direction = (centerB - centerA)
    if direction.Dot(collisionNormal) < 0:
        collisionNormal = collisionNormal * -1

    return collisionNormal, smallestOverlap

def PolygonCollision(polyA, polyB, restitution=0.8, percent=1.0, angularFactor=0.05):
    if not AABBCollision(polyA, polyB):
        return False

    satResult = SATCollision(polyA, polyB)
    if satResult is None:
        return False

    normal, penetration = satResult

    invMassA = 1 / polyA.physics.mass if polyA.physics.mass > 0 else 0
    invMassB = 1 / polyB.physics.mass if polyB.physics.mass > 0 else 0

    correction = normal * penetration * percent
    polyA.transform.position -= correction * invMassA
    polyB.transform.position += correction * invMassB

    velA = polyA.physics.linearVelocity
    velB = polyB.physics.linearVelocity
    relVel = velA - velB
    velAlongNormal = relVel.Dot(normal)
    if velAlongNormal > 0:
        return True

    j = -(1 + restitution) * velAlongNormal
    j /= invMassA + invMassB if invMassA + invMassB != 0 else 1
    impulse = normal * j
    polyA.physics.linearVelocity += impulse * invMassA
    polyB.physics.linearVelocity -= impulse * invMassB

    centerOffsetA = polyA.transform.position - ((polyA.transform.position + polyB.transform.position) * 0.5)
    centerOffsetB = polyB.transform.position - ((polyA.transform.position + polyB.transform.position) * 0.5)
    polyA.physics.angularVelocity += centerOffsetA.x * normal.y * angularFactor - centerOffsetA.y * normal.x * angularFactor
    polyB.physics.angularVelocity += centerOffsetB.x * normal.y * angularFactor - centerOffsetB.y * normal.x * angularFactor

    return True
