import csv
import numpy as np
from matplotlib import pyplot as plt
"""
e_0.append(e[0][0])
e_1.append(e[1][0])
e_2.append(e[2][0])
e_3.append(tau[0])
e_4.append(tau[1])
e_5.append(tau[2])
e_6.append(taus(s,beta,zeta,omega)[0])
e_7.append(taus(s,beta,zeta,omega)[1])
e_8.append(taus(s,beta,zeta,omega)[2])
e_9.append((100 * np.identity(3, dtype=np.float64)@s)[0])
e_10.append((100 * np.identity(3, dtype=np.float64)@s)[1])
e_11.append((100 * np.identity(3, dtype=np.float64)@s)[2])
e_12.append(y(A,W)[0])
e_13.append(y(A,W)[1])
e_14.append(y(A,W)[2])
e_15.append(e[0][1])
e_16.append(e[1][1])
e_17.append(e[2][1])
e_18.append(s[0])
e_19.append(s[1])
e_20.append(s[2])
e_21.append(beta.T @ omega)
"""
n_seed = 4
alpha_lambda = 0.3

az1 = 0.4
az2 = 0.1

T = 1000
end = 25
end_plt = 25
start_plt = 0

n_e = 15

t_data = np.loadtxt(f"time{end}.csv")
#e_data = np.loadtxt(f"p_s{s}_e_all.csv")
#e_all = np.load(f"p_s{s}_e_all.npy",allow_pickle=True)

e_all_p = np.loadtxt(f"k_s{n_seed}_m{alpha_lambda}_T{T}_t{end}_az{az2}_e_all.csv")
e_all_c = np.loadtxt(f"k_s{n_seed}_m{alpha_lambda}_T{T}_t{end}_az{az1}_e_all.csv")

e1_p_data = e_all_p[n_e]
e1_c_data = e_all_c[n_e]

plt.plot(t_data, e1_c_data, color="tab:green", label = f"{az1}")
plt.plot(t_data, e1_p_data, color="tab:red", label = f"{az2}")

plt.xlabel("time (s)")
plt.ylabel(f"tracking error of link {n_e} (rad)")

plt.xlim(start_plt,end_plt)
#plt.ylim(-40,40)
plt.legend()
plt.grid()

plt.show()
