NEURON {
    POINT_PROCESS gap2
    POINTER vgap
    RANGE g, i
    NONSPECIFIC_CURRENT i
}

PARAMETER {
    g = 1.0 (microsiemens)
}

ASSIGNED {
    v (millivolt)
    vgap (millivolt)
    i (nanoamp)
}

BREAKPOINT {
    i = (v - vgap)*g
}