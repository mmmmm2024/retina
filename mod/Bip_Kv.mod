INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
 SUFFIX IKvbip
 USEION k READ ek WRITE ik
 RANGE gkvbar
 RANGE m_inf, h_inf
 RANGE tau_m, tau_h, tau_m1, tau_h1
 RANGE m_exp, h_exp
 RANGE ikv
}


UNITS {
 (molar) = (1/liter)
 (mM) = (millimolar)
 (mA) = (milliamp)
 (mV) = (millivolt)
}

PARAMETER {
 gkvbar	= 0.001	(mho/cm2)
 ek (mV)
 dt (ms)
 v  (mV)
 tau_m1 = 1000
 tau_h1 = 10000
}

STATE {
 m h 
}

INITIAL {
 m = 0.755
 h = 0.001
}

ASSIGNED {
 ik	(mA/cm2)
 ikv	(mA/cm2)
 m_inf 
 h_inf
 tau_m 
 tau_h
 m_exp 
 h_exp
}

BREAKPOINT {
 SOLVE states
 ikv = gkvbar * m*m*m *h* (v - ek)
 ik = ikv
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
	
 am = (400) / ((exp(-(v-15)/36)) + 1)
 bm = (exp((-v/13)))
 tau_m = 1 / (am + bm)
 m_inf = am * tau_m
 m_exp = 1 - exp(-dt/tau_m/tau_m1)

 ah = 0.0003 * (exp((-v/7)))
 bh = ((80) / ((exp(-(v+115)/15)) + 1))+0.02
 tau_h = 1 / (ah + bh)
 h_inf = ah * tau_h
 h_exp = 1 - exp(-dt/tau_h/tau_h1)

}

UNITSON
