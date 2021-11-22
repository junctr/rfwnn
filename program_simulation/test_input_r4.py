# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 17:14:10 2020

@author: satoj
"""
import numpy as np
import time
#import scipy.integrate as sp
from matplotlib import pyplot as plt


def system(t, q, p, l, g, tau):
    
    dq = np.empty((3, 2), dtype=np.float32)

    #dq = [[q1,q1_dot],[q2,q2_dot],[q3,q3_dot]]
    
    dq[:,[0]] = q[:,[1]]
    dq[:,[1]] = np.linalg.inv(M(t,q,p,l)) @ (tau - tau0(t) - np.dot(C(t,q,p,l), q[:,[1]]) - G(t,q,l,p,g) - F(t,q))

    return dq

def M(t, q, p, l):

    M = np.zeros((3,3), dtype=np.float32)

    M[0][0] = l[0]**2 * (p[0] + p[1]) + p[1] * l[1]**2 + 2 * p[0] * p[1] * np.cos(q[1][0])
    M[0][1] = p[1] * l[1]**2 + p[1] * l[0] * l[1] * np.cos(q[1][0])
    M[1][0] = M[0][1]
    M[1][1] = p[1] * l[1]**2
    M[2][2] = p[2]

    return M

def C(t, q, p, l):

    C = np.zeros((3,3), dtype=np.float32)

    C[0][0] = -p[1] * l[0] * l[1] * (2 * q[0][1] * q[1][1] + q[1][1]**2) * np.sin(q[1][0])
    C[1][0] = p[1] * l[0] * l[1] * q[0][1]**2 * np.sin(q[1][0])

    return C

def G(t, q, p, l, g):
    
    G = np.array([
        [(p[0] + p[1]) * g * l[0] * np.cos(q[0][0]) + p[1] * g * l[1] * np.cos(q[0][0] + q[1][0])],
        [p[1] * g * l[1] * np.cos(q[0][0] + q[1][0])],
        [-p[2] * g]],
        dtype=np.float32
    )

    return G

def F(t, q):

    F = np.array([
        [5*q[0][1] + 0.2 * np.sign(q[0][1])],
        [5*q[1][1] + 0.2 * np.sign(q[1][1])],
        [5*q[2][1] + 0.2 * np.sign(q[2][1])]],
        dtype=np.float32
    )

    return F
    
def qd(t):

    qd = np.array([
        [0.5*np.sin(2*np.pi*t), np.pi*np.cos(2*np.pi*t)], 
        [0.5*np.sin(2*np.pi*t), np.pi*np.cos(2*np.pi*t)], 
        [0.5*np.sin(2*np.pi*t), np.pi*np.cos(2*np.pi*t)]],
        dtype=np.float32
    )

    return qd

def tau0(t):
    
    tau0 = np.array([
        [2*np.sin(np.pi*t)],
        [2*np.sin(np.pi*t)],
        [2*np.sin(np.pi*t)]],
        dtype=np.float32
    )
    
    return tau0

def e_f(t, q):

    e = np.empty((3,2), dtype=np.float32)

    e = qd(t) - q

    return e

def s_f(e):

    s = np.empty((3,1), dtype=np.float32)

    s = e[:,[1]] + (5 * np.identity(3, dtype=np.float32)) @ e[:,[0]]

    return s

def x_f(t, q, s):

    x = np.empty((15,1), dtype=np.float32)

    x = np.concatenate([q.T.reshape(-1,1), qd(t).T.reshape(-1,1), s])

    return x

def xji_f(t, x, xold, odot, co, ro):

    xji = np.empty((15,5), dtype=np.float32)

    xji = x + odot * np.exp(A_f(t,xold,co,ro))

    return xji

def A_f(t, xji, co, ro):

    A = np.empty((15,5), dtype=np.float32)

    A = -(co**2) * ((xji - ro)**2)

    return A

def mu_f(A):

    mu = np.empty((1,5), dtype=np.float32)

    mu = np.prod((1 + A) * np.exp(A), axis=0)

    #muji = (1 + A) * np.exp(A)

    return mu

def muji_f(A):

    muji = (1 + A) * np.exp(A)

    return muji

def y(A, W):

    #y = np.empty((3,1), dtype=np.float32)

    y = W.T @ mu_f(A).reshape(5,1)

    return y

def omega_f(odot, co, ro, W):

    omega = np.array([
        [1],
        [np.linalg.norm(odot)],
        [np.linalg.norm(co)],
        [np.linalg.norm(ro)],
        [np.linalg.norm(W)]],
        dtype=np.float32
    )

    return omega

def taus(s, beta, zeta, omega):

    taus = ((beta.T @ omega)**2 / (np.linalg.norm(s) * beta.T @ omega + zeta)) * s

    return taus

def tau_f(s, A, beta, zeta, omega):
    
    tau = np.empty((3,1), dtype=np.float32)

    K = 100 * np.identity(3, dtype=np.float32)

    tau = taus(s,beta,zeta,omega) + K @ s + y(A,W)
    #tau = y(A,W)
    #tau = taus(s,beta,zeta,omega) + K @ s

    return tau    

def B_f(x, Aold, odot, ro):

    B = x + odot * np.exp(Aold) - ro

    return B    

def bk_f(mu, muji, A, Aold, B, co):

    bk = np.empty((5,75), dtype=np.float32)

    dmuji =(2 + A) * np.exp(A) *(-2 * co**2 * np.exp(Aold) * B)

    x = mu * dmuji / muji

    zeros0 = np.zeros((15,5), dtype=np.float32) 
    zeros1 = np.zeros((15,5), dtype=np.float32) 
    zeros2 = np.zeros((15,5), dtype=np.float32) 
    zeros3 = np.zeros((15,5), dtype=np.float32) 
    zeros4 = np.zeros((15,5), dtype=np.float32) 

    zeros0[:,[0]] = x[:,[0]]
    zeros1[:,[1]] = x[:,[1]]
    zeros2[:,[2]] = x[:,[2]]
    zeros3[:,[3]] = x[:,[3]]
    zeros4[:,[4]] = x[:,[4]]

    bk[0] = zeros0.T.reshape(1,-1)
    bk[1] = zeros1.T.reshape(1,-1)
    bk[2] = zeros2.T.reshape(1,-1)
    bk[3] = zeros3.T.reshape(1,-1)
    bk[4] = zeros4.T.reshape(1,-1)

    return bk.T

def ek_f(mu, muji, A, Aold, B ,odot, co, ro, xold):

    ek = np.empty((5,75), dtype=np.float32)

    dmuji =(2 + A) * np.exp(A) *(-2 * co * B**2 -2 * co**2 * B *(-2 * odot * co * (xold - ro)**2 ) * np.exp(Aold))

    x = mu * dmuji / muji

    zeros0 = np.zeros((15,5), dtype=np.float32) 
    zeros1 = np.zeros((15,5), dtype=np.float32) 
    zeros2 = np.zeros((15,5), dtype=np.float32) 
    zeros3 = np.zeros((15,5), dtype=np.float32) 
    zeros4 = np.zeros((15,5), dtype=np.float32) 

    zeros0[:,[0]] = x[:,[0]]
    zeros1[:,[1]] = x[:,[1]]
    zeros2[:,[2]] = x[:,[2]]
    zeros3[:,[3]] = x[:,[3]]
    zeros4[:,[4]] = x[:,[4]]

    ek[0] = zeros0.T.reshape(1,-1)
    ek[1] = zeros1.T.reshape(1,-1)
    ek[2] = zeros2.T.reshape(1,-1)
    ek[3] = zeros3.T.reshape(1,-1)
    ek[4] = zeros4.T.reshape(1,-1)

    return ek.T

def gk_f(mu, muji, A, Aold, B ,odot, co, ro):

    gk = np.empty((5,75), dtype=np.float32)

    dmuji =(2 + A) * np.exp(A) *(-2 * co**2 * B * (-1 -2 * odot * co**2 * ro * np.exp(Aold)))

    x = mu * dmuji / muji

    zeros0 = np.zeros((15,5), dtype=np.float32) 
    zeros1 = np.zeros((15,5), dtype=np.float32) 
    zeros2 = np.zeros((15,5), dtype=np.float32) 
    zeros3 = np.zeros((15,5), dtype=np.float32) 
    zeros4 = np.zeros((15,5), dtype=np.float32) 

    zeros0[:,[0]] = x[:,[0]]
    zeros1[:,[1]] = x[:,[1]]
    zeros2[:,[2]] = x[:,[2]]
    zeros3[:,[3]] = x[:,[3]]
    zeros4[:,[4]] = x[:,[4]]

    gk[0] = zeros0.T.reshape(1,-1)
    gk[1] = zeros1.T.reshape(1,-1)
    gk[2] = zeros2.T.reshape(1,-1)
    gk[3] = zeros3.T.reshape(1,-1)
    gk[4] = zeros4.T.reshape(1,-1)

    return gk.T

def rungekutta(t, q, xold, p, l, g, odot, co, ro, W, beta, zeta):
    
    e = e_f(t,q)
    s = s_f(e)
    x = x_f(t,q,s)
    xji = xji_f(t,x,xold,odot,co,ro)
    A = A_f(t,xji,co,ro)
    omega = omega_f(odot,co,ro,W)
    tau = tau_f(s,A,beta,zeta,omega)
    
    return system(t,q,p,l,g,tau)

alpha_w = 50 * np.identity(5, dtype=np.float32)
alpha_odot = 20 * np.identity(75, dtype=np.float32)
alpha_co = 20 * np.identity(75, dtype=np.float32)
alpha_ro = 20 * np.identity(75, dtype=np.float32)
alpha_beta = 0.001 * np.identity(5, dtype=np.float32)
alpha_zeta = 0.1

zeta = 1
omega = np.ones((5,1), dtype=np.float32)

p = np.array([4, 3, 1.5])
l = np.array([0.4, 0.3, 0.2])
g = 10


beta = 20 * np.array([
    [1],
    [1],
    [1],
    [1],
    [1]],
    dtype=np.float32
)

t = 0.0
end = 20
step = 0.001
i = 0

m = -0.001
n = 0.5
q = np.array([
    [m * 0.5, n * np.pi],
    [m * 0.5, n * np.pi],
    [m * 0.5, n * np.pi]],
    dtype=np.float32
)
xold = np.array([[m*0.5,m*0.5,m*0.5,n*np.pi,n*np.pi,n*np.pi,0,0,0,np.pi,np.pi,np.pi,(1-n)*np.pi-m*2.5,(1-n)*np.pi-m*2.5,(1-n)*np.pi-m*2.5]], dtype=np.float32).reshape(-1,1)

"""
q = np.zeros((3,2), dtype=np.float32)
xold = np.array([[0,0,0,0,0,0,0,0,0,np.pi,np.pi,np.pi,np.pi,np.pi,np.pi]], dtype=np.float32).reshape(-1,1)


q = np.array([
    [0, np.pi],
    [0, np.pi],
    [0, np.pi]],
    dtype=np.float32
)
xold = np.array([[0,0,0,np.pi,np.pi,np.pi,0,0,0,np.pi,np.pi,np.pi,0,0,0]], dtype=np.float32).reshape(-1,1)
"""


W = 1 * np.random.randn(5,3)
odot = 1 * np.random.randn(15,5)
co = 1 * np.random.randn(15,5)
ro = 1 * np.random.randn(15,5)

#beta = np.random.randn(5,1)

#q_data = np.empty((1,6), dtype=np.float32)
#e_data = np.empty((1,6), dtype=np.float32)
q3_data = []
qd3_data = []
e1_data = []
e2_data = []
e3_data = []
e4_data = []
e5_data = []
e6_data = []
e7_data = []
e8_data = []
e9_data = []
e10_data = []
e11_data = []
e12_data = []
e13_data = []
e14_data = []
e15_data = []
t_data = []

start = time.time()

while t < end:

    e = e_f(t,q)
    s = s_f(e)
    x = x_f(t,q,s)
    xji = xji_f(t,x,xold,odot,co,ro)
    A = A_f(t,xji,co,ro)
    Aold = A_f(t,xold, co,ro)
    B = B_f(x,Aold,odot,ro)
    mu = mu_f(A)
    muji = muji_f(A)
    omega = omega_f(odot,co,ro,W)
    tau = tau_f(s,A,beta,zeta,omega)
    bk = bk_f(mu,muji,A,Aold,B,co)
    ek = ek_f(mu,muji,A,Aold,B,odot,co,ro,xold)
    gk = gk_f(mu,muji,A,Aold,B,odot,co,ro)

    """
    taus(s,beta,zeta,omega)[]
    (100 * np.identity(3, dtype=np.float32)@s)[]
    y(A,W)[]
    """
    q3_data.append(x[2][0])
    qd3_data.append(0.5*np.sin(2*np.pi*t))
    e1_data.append(e[0][0])
    e2_data.append(e[1][0])
    e3_data.append(e[2][0])
    e4_data.append(tau[0])
    e5_data.append(tau[1])
    e6_data.append(tau[2])
    e7_data.append(taus(s,beta,zeta,omega)[0])
    e8_data.append(taus(s,beta,zeta,omega)[1])
    e9_data.append(taus(s,beta,zeta,omega)[2])
    e10_data.append((100 * np.identity(3, dtype=np.float32)@s)[0])
    e11_data.append((100 * np.identity(3, dtype=np.float32)@s)[1])
    e12_data.append((100 * np.identity(3, dtype=np.float32)@s)[2])
    e13_data.append(y(A,W)[0])
    e14_data.append(y(A,W)[1])
    e15_data.append(y(A,W)[2])
    t_data.append(t)

    #rungekutta_start
    k1 = system(t,q,p,l,g,tau)
    t_k2 = t + step/2
    q_k2 = q + (step/2) * k1
    e_k2 = e_f(t_k2,q_k2)
    s_k2 = s_f(e_k2)
    xold_k2 = (x + xold) / 2
    k2 = rungekutta(t_k2,q_k2,xold_k2,p,l,g,odot,co,ro,W,beta,zeta)
    t_k3 = t + step/2
    q_k3 = q + (step/2) * k2
    e_k3 = e_f(t_k3,q_k3)
    s_k3 = s_f(e_k3)
    xold_k3 = (x + xold) / 2
    k3 = rungekutta(t_k3,q_k3,xold_k3,p,l,g,odot,co,ro,W,beta,zeta)
    t_k4 = t + step
    q_k4 = q + step * k3
    e_k4 = e_f(t_k4,q_k4)
    s_k4 = s_f(e_k4)
    xold_k4 = x
    k4 = rungekutta(t_k4,q_k4,xold_k4,p,l,g,odot,co,ro,W,beta,zeta)

    xold = x
    qold = q

    q += (step / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    #rungekutta_end

    #q += step * system(t,q,p,l,g,tau)
    W += step * alpha_w @ (mu.reshape(5,1) - bk.T @ odot.T.reshape(-1,1) - ek.T @ co.T.reshape(-1,1) - gk.T @ ro.T.reshape(-1,1)) @ s.T
    odot += (step * alpha_odot @ bk @ W @ s).reshape(5,15).T
    co += (step * alpha_co @ ek @ W @ s).reshape(5,15).T
    ro += (step * alpha_ro @ gk @ W @ s).reshape(5,15).T
    beta += step * np.linalg.norm(s) * alpha_beta @ omega
    zeta += -step * alpha_zeta * zeta

    t += step
    i += 1
    if i%1000 == 0:
        print(round(100*t/end, 1),"%",i,round(time.time()-start, 1),"s")


print("W")
print(np.round(W,2))
print("odot")
print(np.round(odot,2))
print("co")
print(np.round(co,2))
print("ro")
print(np.round(ro,2))
print("beta")
print(beta)
print("zeta")
print(zeta)
print("beta")
print(np.linalg.norm(W.T @ bk.T))
print(np.linalg.norm(W.T @ ek.T))
print(np.linalg.norm(W.T @ gk.T))
print(np.linalg.norm(bk.T @ odot.T.reshape(-1,1) + ek.T @ co.T.reshape(-1,1) + gk.T @ ro.T.reshape(-1,1)))

fig = plt.figure()

ax1 = fig.add_subplot(3,2,1)
ax2 = fig.add_subplot(3,2,2)
ax3 = fig.add_subplot(3,2,3)
ax4 = fig.add_subplot(3,2,4)
ax5 = fig.add_subplot(3,2,5)
ax6 = fig.add_subplot(3,2,6)

ax1.plot(t_data, e1_data)
ax3.plot(t_data, e2_data)
ax5.plot(t_data, e3_data)
ax2.plot(t_data, e4_data)
ax4.plot(t_data, e5_data)
ax6.plot(t_data, e6_data)
ax2.plot(t_data, e7_data)
ax4.plot(t_data, e8_data)
ax6.plot(t_data, e9_data)
ax2.plot(t_data, e10_data)
ax4.plot(t_data, e11_data)
ax6.plot(t_data, e12_data)
ax2.plot(t_data, e13_data)
ax4.plot(t_data, e14_data)
ax6.plot(t_data, e15_data)

fig.tight_layout()

plt.title("rungekutta4_xi")
plt.show()