INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
 SUFFIX IAbip
 USEION k READ ek WRITE ik
 RANGE gkabar
 RANGE m_inf, h_inf
 RANGE tau_m, tau_h
 RANGE m_exp, h_exp
 RANGE ika
}


UNITS {
 (molar) = (1/liter)
 (mM) = (millimolar)
 (mA) = (milliamp)
 (mV) = (millivolt)
}

PARAMETER {
 gkabar	= 0.0175 (mho/cm2)
 ek (mV)
 dt (ms)
 v  (mV)
}

STATE {
 m h 
}

INITIAL {
 m = 0.115
 h = 0.755
}

ASSIGNED {
 ik	(mA/cm2)
 ika (mA/cm2)
 m_inf 
 h_inf
 tau_m 
 tau_h
 m_exp 
 h_exp
}

BREAKPOINT {
 SOLVE states
 ika = gkabar * m*m*m *h* (v - ek)
 ik = ika
}

PROCEDURE states() {	: exact when v held constant
 evaluate_fct(v)
 m = m + m_exp * (m_inf - m)
 h = h + h_exp * (h_inf - h)

 VERBATIM
 return 0;
 ENDVERBATIM
}

UNITSOFF

PROCEDURE evaluate_fct(v(mV)) { LOCAL am,bm,ah,bh
 am = (1200) / ((exp(-(v-50)/28)) + 1)
 bm = 6 * (exp((-v/10)))
 tau_m = 1 / (am + bm)
 m_inf = am * tau_m
 m_exp = 1 - exp(-dt/tau_m)

 ah = 0.045 * (exp((-v/13)))
 bh = (75) / ((exp(-(v+50)/15)) + 1)
 tau_h = 1 / (ah + bh)
 h_inf = ah * tau_h
 h_exp = 1 - exp(-dt/tau_h)
}

UNITSON
