from sxl import spacetime

class DilationField(spacetime.Scalar):

    name = "dilation field"

class ShiftField(spacetime.Rank1Tensor):

    name = "shift field"

class ContractionField(spacetime.Rank1Tensor):

    name = "contraction field"

class ShearField(spacetime.Rank1Tensor):

    name = "shear field"

class WarpTensor(spacetime.Rank2Tensor):

    name = "warp tensor"

    def __init__(self, metric: spacetime.MetricTensor, d: DilationField=None, s: ShiftField=None, c: ContractionField=None, h: ShearField=None):
        spacetime.Rank2Tensor.__init__(self, metric, [
            [d(), s.co(1), s.co(2), s.co(3)],
            [s.co(1), c.co(1), h.co(3), h.co(2)],
            [s.co(2), h.co(3), c.co(2), h.co(1)],
            [s.co(3), h.co(2), h.co(1), c.co(3)]
        ], "dd")
        self.dilation = d
        self.shift = s
        self.contraction = c
        self.shear = h

    # extra attributes:
    # - constructor that builds from fields
    # - metric tensor builder from background metric

class NormalizedWarpTensor(WarpTensor):

    name = "normalized warp tensor"

    def __init__(self, metric, d, s, c, h):
        WarpTensor.__init__(self, metric, d, s / 2, c, h / 2)

    def apply(self):
        pass