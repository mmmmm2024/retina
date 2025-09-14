:Yonemoto /* H channel */

NEURON {
    SUFFIX IHyone
    NONSPECIFIC_CURRENT ih
    :USEION h READ eh WRITE ih       : Uses hyperpolarization-activated current
    RANGE gH, EH, ih                : Parameters for maximum conductance, reversal potential, and current
    RANGE nH, n_inf, tau_n          : Activation variable, steady-state value, and time constant for nH
}

UNITS {
    (mV) = (millivolt)
    (mA) = (milliamp)
    (mS) = (millisiemens)
}

PARAMETER {
    gH = 0.0025 (mho/cm2)               : Maximum conductance of the H channel
    EH = -32.0 (mV)                 : Reversal potential for H current
    ao_nH = 0.001 (/ms)                : Rate constant for nH activation
    Vhalf_nH = -82.0 (mV)           : Half-activation voltage
    S_nH = -5.33 (mV)               : Slope factor for activation
}

ASSIGNED {
    v (mV)                          : Membrane potential
    eh (mV)                         : Reversal potential for H current
    ih (mA/cm2)                     : H current
    n_inf                           : Steady-state activation variable
    tau_n (ms)                      : Time constant for nH
}

STATE {
    nH                               : Activation variable for the H channel
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    ih = gH * nH * (v - EH)        : Calculate H current based on activation
}

DERIVATIVE states {
    trates(v)
    nH' = (n_inf - nH) / tau_n      : Differential equation for nH
}

INITIAL {
    trates(v)
    nH = n_inf                      : Set initial value of nH to steady-state
}

PROCEDURE trates(v) {
    LOCAL alpha_n, beta_n
    alpha_n = alpha_nH_RPR(v)
    beta_n = beta_nH_RPR(v)
    n_inf = alpha_n / (alpha_n + beta_n)
    tau_n = 1.0 / (alpha_n + beta_n)
}

FUNCTION alpha_nH_RPR(v){
    alpha_nH_RPR = 0.001 * ao_nH * exp((v - Vhalf_nH) / (2 * S_nH))
}

FUNCTION beta_nH_RPR(v){
    beta_nH_RPR = 0.001 * ao_nH * exp(-(v - Vhalf_nH) / (2 * S_nH))
}
