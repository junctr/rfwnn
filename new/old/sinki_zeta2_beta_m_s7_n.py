# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 17:14:10 2020

@author: satoj
"""
import numpy as np
import time
#import scipy.integrate as sp
from matplotlib import pyplot as plt
from tqdm import tqdm


def system(t, q, p, l, g, tau):
    
    dq = np.empty((3, 2), dtype=np.float64)

    #dq = [[q1,q1_dot],[q2,q2_dot],[q3,q3_dot]]

    dq[:,[0]] = q[:,[1]]
    dq[:,[1]] = np.linalg.inv(M(t,q,p,l)) @ (tau - tau0(t) - np.dot(C(t,q,p,l), q[:,[1]]) - G(t,q,l,p,g) - F(t,q))

    return dq

def M(t, q, p, l):

    M = np.zeros((3,3), dtype=np.float64)

    M[0][0] = l[0]**2 * (p[0] + p[1]) + p[1] * (l[1]**2 + 2 * l[0] * l[1] * np.cos(q[1][0]))
    #M[0][0] = l[0]**2 * (p[0] + p[1]) + p[1] * l[1]**2 + 2 * p[0] * p[1] * np.cos(q[1][0])
    M[0][1] = p[1] * l[1]**2 + p[1] * l[0] * l[1] * np.cos(q[1][0])
    M[1][0] = M[0][1]
    M[1][1] = p[1] * l[1]**2
    M[2][2] = p[2]

    return M

def C(t, q, p, l):

    C = np.zeros((3,3), dtype=np.float64)

    C[0][0] = -p[1] * l[0] * l[1] * (2 * q[0][1] * q[1][1] + q[1][1]**2) * np.sin(q[1][0])
    C[1][0] = p[1] * l[0] * l[1] * q[0][1]**2 * np.sin(q[1][0])

    return C

def G(t, q, p, l, g):
    
    G = np.array([
        [(p[0] + p[1]) * g * l[0] * np.cos(q[0][0]) + p[1] * g * l[1] * np.cos(q[0][0] + q[1][0])],
        [p[1] * g * l[1] * np.cos(q[0][0] + q[1][0])],
        [-p[2] * g]],
        dtype=np.float64
    )

    return G

def F(t, q):

    F = np.array([
        [5*q[0][1] + 0.2 * np.sign(q[0][1])],
        [5*q[1][1] + 0.2 * np.sign(q[1][1])],
        [5*q[2][1] + 0.2 * np.sign(q[2][1])]],
        dtype=np.float64
    )

    return F

def qd(t):

    qd = np.array([
        [0.5*np.sin(2*np.pi*t), np.pi*np.cos(2*np.pi*t)], 
        [0.5*np.sin(2*np.pi*t), np.pi*np.cos(2*np.pi*t)], 
        [0.5*np.sin(2*np.pi*t), np.pi*np.cos(2*np.pi*t)]],
        dtype=np.float64
    )

    return qd

def tau0(t):
    """
    tau0 = np.array([
        [2*np.sin(np.pi*t)],
        [2*np.sin(np.pi*t)],
        [2*np.sin(np.pi*t)]],
        dtype=np.float64
    )
    """
    tau0 = np.array([
        [2*np.sin(10 *2*np.pi*t)],
        [2*np.sin(10 *2*np.pi*t)],
        [2*np.sin(10 *2*np.pi*t)]],
        dtype=np.float64
    )
    
    return tau0

def e_f(t, q):

    e = np.empty((3,2), dtype=np.float64)

    e = qd(t) - q

    return e

def s_f(e):

    s = np.empty((3,1), dtype=np.float64)

    s = e[:,[1]] + ((5 * np.identity(3, dtype=np.float64)) @ e[:,[0]])

    return s

def x_f(t, q, s):

    x = np.empty((15,1), dtype=np.float64)

    x = np.concatenate([q.T.reshape(-1,1), qd(t).T.reshape(-1,1), s])

    return x

def xji_f(t, x, xold, odot, co, ro):

    xji = np.empty((15,5), dtype=np.float64)

    xji = x + odot * np.exp(A_f(t,xold,co,ro))

    return xji

def A_f(t, xji, co, ro):

    A = np.empty((15,5), dtype=np.float64)

    A = -(co**2) * ((xji - ro)**2)

    return A

def mu_f(A):

    mu = np.empty((1,5), dtype=np.float64)

    mu = np.prod((1 + A) * np.exp(A), axis=0)

    #muji = (1 + A) * np.exp(A)

    return mu

def muji_f(A):

    muji = (1 + A) * np.exp(A)

    return muji

def y(A, W):

    #y = np.empty((3,1), dtype=np.float64)

    y = W.T @ mu_f(A).reshape(5,1)

    return y

def omega_f(odot, co, ro, W):

    omega = np.array([
        [1],
        [np.linalg.norm(odot)],
        [np.linalg.norm(co)],
        [np.linalg.norm(ro)],
        [np.linalg.norm(W)]],
        dtype=np.float64
    )

    return omega

def taus(s, beta, zeta, omega):

    taus = ((beta.T @ omega)**2 / (np.linalg.norm(s) * beta.T @ omega + zeta + 0.1)) * s

    return taus

def tau_f(s, A, beta, zeta, omega):
    
    tau = np.empty((3,1), dtype=np.float64)

    K = 100 * np.identity(3, dtype=np.float64)

    tau = taus(s,beta,zeta,omega) + K @ s + y(A,W)
    #tau = y(A,W)
    #tau = taus(s,beta,zeta,omega) + K @ s

    return tau    

def B_f(x, Aold, odot, ro):

    B = x + odot * np.exp(Aold) - ro

    return B    

def bk_f(mu, muji, A, Aold, B, co):

    bk = np.empty((5,75), dtype=np.float64)

    dmuji =(2 + A) * np.exp(A) *(-2 * co**2 * np.exp(Aold) * B)

    #x = mu * dmuji / muji
    x = mu * np.divide(dmuji, muji, out=np.zeros_like(dmuji), where=muji!=0)

    zeros0 = np.zeros((15,5), dtype=np.float64) 
    zeros1 = np.zeros((15,5), dtype=np.float64) 
    zeros2 = np.zeros((15,5), dtype=np.float64) 
    zeros3 = np.zeros((15,5), dtype=np.float64) 
    zeros4 = np.zeros((15,5), dtype=np.float64) 

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

    ek = np.empty((5,75), dtype=np.float64)

    dmuji =(2 + A) * np.exp(A) *(-2 * co * B**2 -2 * co**2 * B *(-2 * odot * co * (xold - ro)**2 ) * np.exp(Aold))

    #x = mu * dmuji / muji
    x = mu * np.divide(dmuji, muji, out=np.zeros_like(dmuji), where=muji!=0)

    zeros0 = np.zeros((15,5), dtype=np.float64) 
    zeros1 = np.zeros((15,5), dtype=np.float64) 
    zeros2 = np.zeros((15,5), dtype=np.float64) 
    zeros3 = np.zeros((15,5), dtype=np.float64) 
    zeros4 = np.zeros((15,5), dtype=np.float64) 

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

    gk = np.empty((5,75), dtype=np.float64)

    dmuji =(2 + A) * np.exp(A) *(-2 * co**2 * B * (-1 -2 * odot * co**2 * ro * np.exp(Aold)))

    #x = mu * dmuji / muji
    x = mu * np.divide(dmuji, muji, out=np.zeros_like(dmuji), where=muji!=0)

    zeros0 = np.zeros((15,5), dtype=np.float64) 
    zeros1 = np.zeros((15,5), dtype=np.float64) 
    zeros2 = np.zeros((15,5), dtype=np.float64) 
    zeros3 = np.zeros((15,5), dtype=np.float64) 
    zeros4 = np.zeros((15,5), dtype=np.float64) 

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

np.random.seed(7)

alpha_w = 50 * np.identity(5, dtype=np.float64)
alpha_odot = 20 * np.identity(75, dtype=np.float64)
alpha_co = 20 * np.identity(75, dtype=np.float64)
alpha_ro = 20 * np.identity(75, dtype=np.float64)
alpha_beta = 0.001 * np.identity(5, dtype=np.float64)
alpha_zeta = 0.1
alpha_lambda = 0.5

zeta = 1
omega = np.ones((5,1), dtype=np.float64)

p = np.array([4, 3, 1.5])
l = np.array([0.4, 0.3, 0.2])
g = 10

beta = 0.1 * np.array([
    [1],
    [1],
    [1],
    [1],
    [1]],
    dtype=np.float64

)

t = 0.0
end = 100
step = 0.001
i = 0

m = -0.01
n = 1.01
q = np.array([
    [m * 0.5, n * np.pi],
    [m * 0.5, n * np.pi],
    [m * 0.5, n * np.pi]],
    dtype=np.float64
)
xold = [] 
xold.append(np.array([[m*0.5,m*0.5,m*0.5,n*np.pi,n*np.pi,n*np.pi,0,0,0,np.pi,np.pi,np.pi,(1-n)*np.pi-m*2.5,(1-n)*np.pi-m*2.5,(1-n)*np.pi-m*2.5]], dtype=np.float64).reshape(-1,1))

W = 50 * 2 * (np.random.rand(5,3) - 0.5)
j_q = 1.0 * 0.5
j_dq = 1.0 * np.pi
j_s = 0.1 * 1.0 * np.pi * np.sqrt(2)
j = np.array([[j_q,j_q,j_q,j_dq,j_dq,j_dq,j_q,j_q,j_q,j_dq,j_dq,j_dq,j_s,j_s,j_s]]).T
odot = j * 0.1 * 2 * (np.random.rand(15,5) - 0.5)
co = (1/j) * 0.5 * 2 * (np.random.rand(15,5) - 0.5)
ro = j * 1 * 2 * (np.random.rand(15,5) - 0.5)
"""
Wold = W
odotold = odot
coold = co
roold = ro
Wold2 = W
odotold2 = odot
coold2 = co
roold2 = ro
"""
Wold = []
odotold = []
coold = []
roold = []
Wold.append(W.copy())
odotold.append(odot.copy())
coold.append(co.copy())
roold.append(ro.copy())

print("W")
print(np.round(W,4))
print("odot")
print(np.round(odot/j,4))
print("co")
print(np.round(co*j,4))
print("ro")
print(np.round(ro/j,4))
print("beta")
print(beta)
print("zeta")
print(zeta)
"""
print("W")
print(W.dtype)
print("odot")
print(odot.dtype)
print("co")
print(co.dtype)
print("ro")
print(ro.dtype)
print("beta")
print(beta.dtype)
#print("zeta")
#print(zeta.dtype)
"""

#beta = np.random.randn(5,1)

#q_data = np.empty((1,6), dtype=np.float64)                         
#e_data = np.empty((1,6), dtype=np.float64)
#q1_data = []
#qd1_data = []
#v1_data = []
#vd1_data =[]
ev1_data = []
s1_data = []
#q2_data = []
#qd2_data = []
#v2_data = []
#vd2_data =[]
ev2_data = []
s2_data = []
#q3_data = []
#qd3_data = []
#v3_data = []
#vd3_data =[]
ev3_data = []
s3_data = []
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
e16_data = []
e17_data = []
e18_data = []
e19_data = []
t_data = []

start = time.time()

for i in tqdm(range(int(end/step))) :
    
    qdt = qd(t)
    e = e_f(t,q)
    s = s_f(e)
    x = x_f(t,q,s)
    xji = xji_f(t,x,xold[-1],odot,co,ro)
    A = A_f(t,xji,co,ro)
    Aold = A_f(t,xold[-1], co,ro)
    B = B_f(x,Aold,odot,ro)
    mu = mu_f(A)
    muji = muji_f(A)
    omega = omega_f(odot,co,ro,W)
    tau = tau_f(s,A,beta,zeta,omega)
    bk = bk_f(mu,muji,A,Aold,B,co)
    ek = ek_f(mu,muji,A,Aold,B,odot,co,ro,xold[-1])
    gk = gk_f(mu,muji,A,Aold,B,odot,co,ro)
    
    
    k1_q = system(t,q,p,l,g,tau)
    k2_q = system(t+step/2,q+(step/2)*k1_q,p,l,g,tau)
    k3_q = system(t+step/2,q+(step/2)*k2_q,p,l,g,tau)
    k4_q = system(t+step,q+step*k3_q,p,l,g,tau)

    xold.append(x.copy())

    Wold.append(W.copy())
    odotold.append(odot.copy())
    coold.append(co.copy())
    roold.append(ro.copy())

    #q1_data.append(q[0][0])
    #qd1_data.append(qdt[0][0])
    #v1_data.append(q[0][1])
    #vd1_data.append(qdt[0][1])
    ev1_data.append(e[0][1])
    s1_data.append(s[0])
    #q2_data.append(q[1][0])
    #qd2_data.append(qdt[1][0])
    #v2_data.append(q[1][1])
    #vd2_data.append(qdt[1][1])
    ev2_data.append(e[1][1])
    s2_data.append(s[1])
    #q3_data.append(q[2][0])
    #qd3_data.append(qdt[2][0])
    #v3_data.append(q[2][1])
    #vd3_data.append(qdt[2][1])
    ev3_data.append(e[2][1])
    s3_data.append(s[2])
    e1_data.append(e[0][0])
    e2_data.append(e[1][0])
    e3_data.append(e[2][0])
    e4_data.append(tau[0])
    e5_data.append(tau[1])
    e6_data.append(tau[2])
    e7_data.append(taus(s,beta,zeta,omega)[0])
    e8_data.append(taus(s,beta,zeta,omega)[1])
    e9_data.append(taus(s,beta,zeta,omega)[2])
    e10_data.append((100 * np.identity(3, dtype=np.float64)@s)[0])
    e11_data.append((100 * np.identity(3, dtype=np.float64)@s)[1])
    e12_data.append((100 * np.identity(3, dtype=np.float64)@s)[2])
    e13_data.append(y(A,W)[0])
    e14_data.append(y(A,W)[1])
    e15_data.append(y(A,W)[2])
    
    e16_data.append(np.mean(np.abs(Wold[-1]-Wold[-2]), dtype=np.float64))
    e17_data.append(np.mean(np.abs(odotold[-1]-odotold[-2]), dtype=np.float64))
    e18_data.append(np.mean(np.abs(coold[-1]-coold[-2]), dtype=np.float64))
    e19_data.append(np.mean(np.abs(roold[-1]-roold[-2]), dtype=np.float64))
    
    t_data.append(t)

    q += (step / 6) * (k1_q + 2 * k2_q + 2 * k3_q + k4_q)
    W += step * (alpha_w @ (mu.reshape(5,1) - bk.T @ odot.T.reshape(-1,1) - ek.T @ co.T.reshape(-1,1) - gk.T @ ro.T.reshape(-1,1)) @ s.T) + alpha_lambda * (Wold[-1] - Wold[-2])
    odot += step * ((alpha_odot @ bk @ W @ s).reshape(5,15).T) + alpha_lambda * (odotold[-1] - odotold[-2])
    co += step * ((alpha_co @ ek @ W @ s).reshape(5,15).T) + alpha_lambda * (coold[-1] - coold[-2])
    ro += step * ((alpha_ro @ gk @ W @ s).reshape(5,15).T) + alpha_lambda * (roold[-1] - roold[-2])
    
    if np.linalg.norm(beta) < 0.3:
        beta += step * (np.linalg.norm(s) * alpha_beta @ omega)
    
    zeta += step * (-alpha_zeta * zeta)

    t += step
    i += 1
    # if i%1000 == 0:
    #     print(round(100*t/end, 1),"%",i,round(time.time()-start, 1),"s")
        
        # print("x")
        # print(x)
        # print("xji")
        # print(xji)
        # print("A")
        # print(A)
        # print("mu")
        # print(mu)
        
        # print("muji")
        # print(muji)
        # print(x-xold[-2])
        # print(W)
        # print(Wold[-1])
        # print(Wold[-2])
        # print(W-Wold[-1])
        # print(Wold[-1]-Wold[-2])
        
        



print("W")
print(np.round(W,4))
print("odot")
print(np.round(odot/j,4))
print("co")
print(np.round(co*j,4))
print("ro")
print(np.round(ro/j,4))
print("beta")
print(beta)
print("zeta")
print(zeta)

"""
print("W")
print(W.dtype)
print("odot")
print(odot.dtype)
print("co")
print(co.dtype)
print("ro")
print(ro.dtype)
print("beta")
print(beta.dtype)
#print("zeta")
#print(zeta.dtype)
"""
"""
print("beta")
print(np.linalg.norm(W.T @ bk.T))
print(np.linalg.norm(W.T @ ek.T))
print(np.linalg.norm(W.T @ gk.T))
print(np.linalg.norm(bk.T @ odot.T.reshape(-1,1) + ek.T @ co.T.reshape(-1,1) + gk.T @ ro.T.reshape(-1,1)))
"""

fig = plt.figure()

ax1 = fig.add_subplot(4,3,1)
ax2 = fig.add_subplot(4,3,2)
ax3 = fig.add_subplot(4,3,3)
ax4 = fig.add_subplot(4,3,4)
ax5 = fig.add_subplot(4,3,5)
ax6 = fig.add_subplot(4,3,6)
ax7 = fig.add_subplot(4,3,7)
ax8 = fig.add_subplot(4,3,8)
ax9 = fig.add_subplot(4,3,9)
ax10 = fig.add_subplot(4,3,10)
ax11 = fig.add_subplot(4,3,11)
ax12 = fig.add_subplot(4,3,12)


#ax1.plot(t_data, q1_data)
#ax4.plot(t_data, q2_data)
#ax7.plot(t_data, q3_data)
#ax1.plot(t_data, qd1_data)
#ax4.plot(t_data, qd2_data)
#ax7.plot(t_data, qd3_data)
ax1.plot(t_data, e1_data)
ax4.plot(t_data, e2_data)
ax7.plot(t_data, e3_data)

#ax2.plot(t_data, v1_data)
#ax5.plot(t_data, v2_data)
#ax8.plot(t_data, v3_data)
#ax2.plot(t_data, vd1_data)
#ax5.plot(t_data, vd2_data)
#ax8.plot(t_data, vd3_data)
ax2.plot(t_data, ev1_data)
ax5.plot(t_data, ev2_data)
ax8.plot(t_data, ev3_data)
ax2.plot(t_data, s1_data)
ax5.plot(t_data, s2_data)
ax8.plot(t_data, s3_data)


ax3.plot(t_data, e4_data)
ax6.plot(t_data, e5_data)
ax9.plot(t_data, e6_data)
ax3.plot(t_data, e7_data)
ax6.plot(t_data, e8_data)
ax9.plot(t_data, e9_data)
ax3.plot(t_data, e10_data)
ax6.plot(t_data, e11_data)
ax9.plot(t_data, e12_data)
ax3.plot(t_data, e13_data)
ax6.plot(t_data, e14_data)
ax9.plot(t_data, e15_data)

ax10.plot(t_data, e16_data)
ax10.plot(t_data, e17_data)
ax11.plot(t_data, e18_data)
ax12.plot(t_data, e19_data)

ax1.grid()
ax2.grid()
ax3.grid()
ax4.grid()
ax5.grid()
ax6.grid()
ax7.grid()
ax8.grid()
ax9.grid()
ax10.grid()
ax11.grid()
ax12.grid()

fig.tight_layout()

plt.title("zeta2_beta_m_s7")
plt.savefig(f"data/new_s7_step{step}_end{end}.png")
plt.show()
