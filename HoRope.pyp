"""
Rope Setup Generator
Copyright: Pasha Ho
Created by Pasha Ho
Written for Cinema 4D R18 and higher
Modified Date: 31/01/2018
"""

import os
import c4d
from c4d import bitmaps, plugins, utils


PLUGIN_ID = 1040416

class HoRope(plugins.ObjectData):
    """HoRope"""


    def Init(self, node):
        self.InitAttr(node, int, [c4d.HOROPE_RES])
        self.InitAttr(node, float, [c4d.HOROPE_RAD])
        self.InitAttr(node, int, [c4d.HOROPE_FSUB])
        self.InitAttr(node, int, [c4d.HOROPE_SEG])
        self.InitAttr(node, bool, [c4d.HOROPE_CTRL])
        self.InitAttr(node, bool, [c4d.HOROPE_SKIN])
        self.InitAttr(node, bool, [c4d.HOROPE_SKIN_ON])

        node[c4d.HOROPE_RES] = 16
        node[c4d.HOROPE_RAD] = 15
        node[c4d.HOROPE_FSUB] = 3
        node[c4d.HOROPE_SEG] = 8
        node[c4d.HOROPE_CTRL] = 1
        node[c4d.HOROPE_SKIN] = 0
        node[c4d.HOROPE_SKIN_ON] = 1
        return True



    def GetDEnabling(self, node, id, t_data, flags, itemdesc):


        # !! Figure out what to do with last return line !!


        if id[0].id == c4d.HOROPE_SKIN_ON:
            return node[c4d.HOROPE_SKIN] == 1
        else:
            return True



    @staticmethod
    def LookAt(slave, target):
        # Returns matrix that "looks at" target position from slave position

        tm = c4d.Matrix()
        tg_d = target - slave  # Target direction vector
        up_d = c4d.Vector(0, 1, 0) - slave  # Up-vector direction vector

        tm.v1 = tg_d.GetNormalized()
        tm.v2 = tm.v1.Cross(up_d).GetNormalized()
        tm.v3 = tm.v1.Cross(tm.v2).GetNormalized()
        return tm

    @staticmethod
    def SwapAxis(obj):

        m = obj.GetMg()
        m.v3, m.v1 = -m.v1, m.v3
        obj.SetMg(m)

    @staticmethod
    def CreateGroups():
        # Creates groups(Null objects)

        rope = c4d.BaseObject(c4d.Onull)            # Main group
        rope.SetName('HoRope')
        bones = c4d.BaseObject(c4d.Onull)           # Parts group
        bones.SetName('Bones')
        bones.InsertUnder(rope)
        connectors = c4d.BaseObject(c4d.Onull)      # Connectors group
        connectors.SetName('Connectors')
        connectors.InsertUnder(rope)
        controls = c4d.BaseObject(c4d.Onull)        # Controls group
        controls.SetName('Controls')
        controls.InsertUnder(rope)

        return rope, bones, connectors, controls

    @staticmethod
    def AssignDynamicTag(rope):
        # Dynamic tag

        rope.InsertTag(c4d.BaseTag(180000102))
        tag = rope.GetFirstTag()
        tag[c4d.RIGID_BODY_HIERARCHY] = 1
        tag[c4d.RIGID_BODY_SHAPE] = 6
        tag[c4d.RIGID_BODY_AERODYNAMICS_DRAG] = .30
        tag[c4d.RIGID_BODY_ANGULAR_DAMPING] = .15
        tag[c4d.RIGID_BODY_LINEAR_DAMPING] = .1
        tag[c4d.RIGID_BODY_ANGULAR_FOLLOW_STRENGTH] = 10
        tag[c4d.RIGID_BODY_SLEEPING_LINEAR_VELOCITY] = 0
        tag[c4d.RIGID_BODY_SLEEPING_ANGULAR_VELOCITY] = 0

    @staticmethod
    def TargetPointList(res, spl):
        # Optimises spline,
        # Returns target point position list (c4d.Vector) and spline length

        proxySpl = spl.GetClone()
        if spl[c4d.SPLINEOBJECT_INTERPOLATION] == 0: 
            proxySpl[c4d.SPLINEOBJECT_TYPE] = 0
            proxySpl[c4d.SPLINEOBJECT_INTERPOLATION] = 2
        else:
            proxySpl[c4d.SPLINEOBJECT_INTERPOLATION] = 2
        proxySpl[c4d.SPLINEOBJECT_SUB] = res

        sh = utils.SplineHelp()
        sh.InitSpline(proxySpl)
        targlist = []
        for i in xrange(res + 1):
            index = float(i) / res
            point_pos = sh.GetMatrix(index).off
            targlist.append(point_pos)

        bonelenth = sh.GetSegmentLength(0) / res

        return targlist, bonelenth

    @staticmethod
    def EqualizeDistances(res, bonelen, plist):
        # Sets points in equal distances from each other

        EDList = list(range(res + 1))
        EDList[0] = plist[0]
        for i in xrange(1, res + 1):
            trg = plist[i] - EDList[i - 1]
            EDList[i] = trg.GetNormalized() * bonelen + EDList[i - 1]
        return EDList

    def CreateBones(self, resolution, bones, bonelen, poslist, op):
        # Create geometry, settings

        radius = op[c4d.HOROPE_RAD]
        if bonelen < radius * 2.5:                     # Limits the radius relative to resolution
            radius = op[c4d.HOROPE_RAD] = bonelen / 2.5

        bone = c4d.BaseObject(c4d.Ocapsule)
        bone[c4d.PRIM_CAPSULE_RADIUS] = radius
        bone[c4d.PRIM_CAPSULE_HEIGHT] = bonelen + radius * 2
        bone[c4d.PRIM_CAPSULE_HSUB] = 1
        bone[c4d.PRIM_CAPSULE_FSUB] = op[c4d.HOROPE_FSUB]
        bone[c4d.PRIM_CAPSULE_SEG] = op[c4d.HOROPE_SEG]
        bone[c4d.PRIM_AXIS] = 0

        for i in xrange(resolution):
            boneclone = bone.GetClone()
            boneTM = self.LookAt(poslist[i], poslist[i + 1])  # Each part looks at next
            boneTM.off = (poslist[i] + poslist[i + 1]) / 2
            boneclone.SetMg(boneTM)
            boneclone.SetName('bone' + str(i))
            boneclone.InsertUnderLast(bones)

    def CreateConnects(self, resolution, connectors, bones, poslist, op):
        # Generates connectors

        obj = c4d.BaseObject(180000011)  # Connector
        obj[c4d.FORCE_TYPE] = 3  # Ragdoll
        obj[c4d.FORCE_SIZE] = op[c4d.HOROPE_RAD] * 2
        obj[c4d.FORCE_ALWAYS_VISIBLE] = 0
        bone = bones.GetDown()

        for i in xrange(resolution - 1):
            connector = obj.GetClone()
            connector.SetMg(bone.GetNext().GetMg())
            self.SwapAxis(connector)
            connector.SetAbsPos(poslist[i + 1])
            connector[c4d.FORCE_OBJECT_B] = bone
            connector[c4d.FORCE_OBJECT_A] = bone.GetNext()
            connector.SetName('connector' + str(i))
            connector.InsertUnderLast(connectors)
            bone = bone.GetNext()

    def CreateControls(self, poslist, controls, bones, op):
        # Generates control nulls

        root = c4d.BaseObject(c4d.Onull)
        root.SetName('root')
        root[c4d.NULLOBJECT_DISPLAY] = 13
        root[c4d.NULLOBJECT_RADIUS] = op[c4d.HOROPE_RAD] * 3
        root.InsertTag(c4d.BaseTag(180000102))
        root.GetFirstTag()[c4d.RIGID_BODY_DYNAMIC] = 0
        root.SetAbsPos(poslist[0])
        root.InsertUnderLast(controls)

        connector = c4d.BaseObject(180000011)  # Connector
        connector[c4d.FORCE_TYPE] = 2  # Ball and Socket
        connector[c4d.FORCE_SIZE] = op[c4d.HOROPE_RAD] * 2
        connector[c4d.FORCE_OBJECT_A] = root
        connector[c4d.FORCE_OBJECT_B] = bones.GetChildren()[0]
        connector.SetName('root connector')
        connector.InsertUnder(root)
        connector.SetAbsPos(c4d.Vector(0,0,0))

        target = root.GetClone()
        target.SetAbsPos(poslist[-1])
        target.SetName('target')
        target.GetDown().SetName('target connector')
        target.InsertUnderLast(controls)
        target.GetDown()[c4d.FORCE_OBJECT_A] = target
        target.GetDown()[c4d.FORCE_OBJECT_B] = bones.GetChildren()[-1]

    def CreateSkin(self, rope, connectors, op):
        # Generates simple sweep based on tracer and connectors positions


        sweep = c4d.BaseObject(c4d.Osweep) # Sweep object
        sweep[c4d.CAP_START] = sweep[c4d.CAP_END] = 0
        sweep.InsertTag(c4d.BaseTag(c4d.Tphong))
        sweep.InsertTag(c4d.BaseTag(180000102))
        sweep.InsertUnder(rope)
        tag = sweep.GetFirstTag()
        tag[c4d.RIGID_BODY_ENABLED] = 0

        tracer = c4d.BaseObject(1018655)  # Tracer object
        tracer[c4d.MGTRACEROBJECT_MODE] = 1
        tracer[c4d.SPLINEOBJECT_TYPE] = 3
        tracer[c4d.SPLINEOBJECT_INTERPOLATION] = 2
        tracer[c4d.SPLINEOBJECT_SUB] = 1
        InExData = c4d.InExcludeData()
        for obj in connectors.GetChildren():
            InExData.InsertObject(obj, 15)
        tracer[c4d.MGTRACEROBJECT_OBJECTLIST] = InExData
        tracer[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        tracer.InsertUnder(sweep)

        circle = c4d.BaseObject(c4d.Osplinecircle)
        circle[c4d.PRIM_CIRCLE_RADIUS] = op[c4d.HOROPE_RAD]
        circle[c4d.SPLINEOBJECT_INTERPOLATION] = 2
        circle[c4d.SPLINEOBJECT_SUB] = 2
        circle[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        circle.InsertUnder(sweep)
        return sweep


    def GetVirtualObjects(self, op, hh):

        spline = op.GetDown()
        if not spline or not spline.GetRealSpline(): return None

        dirty = op.CheckCache(hh)\
                or op.IsDirty(c4d.DIRTY_DATA)\
                or spline.IsDirty(c4d.DIRTY_DATA)\
                or spline.IsDirty(c4d.DIRTY_MATRIX)
        if not dirty: return op.GetCache(hh)


        resolution = op[c4d.HOROPE_RES]
        if resolution <= 0: resolution = 2

        rope, bones, connectors, controls = self.CreateGroups()
        targlist, bonelen = self.TargetPointList(resolution, spline)
        poslist = self.EqualizeDistances(resolution, bonelen, targlist)
        self.CreateBones(resolution, bones, bonelen, poslist, op)
        self.CreateConnects(resolution, connectors, bones, poslist, op)
        self.AssignDynamicTag(rope)
        if op[c4d.HOROPE_CTRL]:
            self.CreateControls(poslist, controls, bones, op)
        if op[c4d.HOROPE_SKIN]:
            skin = self.CreateSkin(rope, connectors, op)
            if op[c4d.HOROPE_SKIN_ON]:
                bones[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
                skin[c4d.ID_BASEOBJECT_GENERATOR_FLAG] = 1
            else:
                skin[c4d.ID_BASEOBJECT_GENERATOR_FLAG] = 0
                bones[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 2

        return rope


if __name__ == "__main__":

    dir, file = os.path.split(__file__)
    icon = bitmaps.BaseBitmap()
    icon.InitWith(os.path.join(dir, "res", "Icon.tif"))
    plugins.RegisterObjectPlugin(id=PLUGIN_ID,
                                 str="HoRope",
                                 g=HoRope,
                                 description="Ohorope",
                                 icon=icon,
                                 info=c4d.OBJECT_GENERATOR)
