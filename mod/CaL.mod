TITLE low-voltage-activated (L-type) calcium channel for STN neuron

COMMENT
 modeled by Otsuka et al., 2004
 implemented in NEURON by Kitano, 2017
ENDCOMMENT

UNITS {
    (mV) = (millivolt)
    (mA) = (milliamp)
    (mM) = (milli/liter)
    (nS) = (nanosiemens)
}

NEURON {
 SUFFIX CaL
 USEION ca READ cai,cao WRITE ica
 RANGE gmax, iCaL
}

PARAMETER {
 v (mV)
 dt (ms)
 cai (mM)
 cao (mM)
 gmax  = 3.31e-6 (mho/cm2):Publio 
 iCaL (mA/cm2)
 e = 40 (mV)
}

STATE {
 m h
}

ASSIGNED { 
 ica (mA/cm2)
 minf
 taum
 hinf
 tauh
}

BREAKPOINT {
 SOLVE states METHOD cnexp
 ica  = gmax*m*h*(v-e)
 iCaL = ica
}

UNITSOFF

INITIAL {
 settables(v)
 m = minf
 h = hinf 
}

DERIVATIVE states {  
 settables(v)
 m' = (minf - m)/taum
 h' = (hinf - h)/tauh
}

PROCEDURE settables(vm) {
    LOCAL a, b, d, g 
        :TABLE minf, taum, hinf, tauh: FROM -100 TO 100 WITH 400
    a = alpha(vm, -10, 0.1, 6)
    b = beta(vm, -10, 0.1, 6)
    d = delta(vm, -10, 0.0005, 9)
    g = gamma(vm, -10, 0.01, 9)
	minf = a / (a + b)
	taum = 1 / (a + b)
	hinf = d / (d + g)
	tauh = 1 / (d + g)
}

FUNCTION alpha(v, vhalf, a0, s) { 
    alpha = a0 * (exp((v - vhalf) / 2*s))
}   

FUNCTION beta(v, vhalf, b0, s) { 
    beta = b0 * (exp(-(v - vhalf) / 2*s))
}

FUNCTION delta(v, vhalf, d0, s) { 
    delta = d0 * (exp((v - vhalf) / 2*s))
}   

FUNCTION gamma(v, vhalf, g0, s) { 
    gamma = g0 * (exp(-(v - vhalf) / 2*s))
}

UNITSON
