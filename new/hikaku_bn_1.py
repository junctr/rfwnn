import csv
import numpy as np
from matplotlib import pyplot as plt
"""
e_0.append(e[0][0])
e_3.append(tau[0])
e_6.append(taus(s,beta,zeta,omega)[0])
e_9.append((100 * np.identity(3, dtype=np.float64)@s)[0])
e_12.append(y(A,W)[0])
e_15.append(e[0][1])
e_18.append(s[0])
e_21.append(wn[0])
e_24.append(taus1[0])
e_27.append(beta.T @ omega)
"""
n_seed = 4
alpha_lambda = 0.3
alpha_wn0 = 100
alpha_wn1 = 100
alpha_s0 = 5.0
alpha_s1 = 5.0
alpha_s2 = 5.0
T = 1000
step = 0.0001
end = 100

end_plt = 100
start_plt = 0

n_e = 0

t_data = np.loadtxt(f"data/step{step}_t{end}.csv")
#e_data = np.loadtxt(f"p_s{s}_e_all.csv")
#e_all = np.load(f"p_s{s}_e_all.npy",allow_pickle=True)

e_all_p = np.loadtxt(f"data/pn_s{n_seed}_m{alpha_lambda}_wn{alpha_wn0}_{alpha_wn1}_s{alpha_s0}_{alpha_s1}_{alpha_s2}_T{T}_step{step}_t{end}_e_all.csv")
e_all_c = np.loadtxt(f"data/bn_s{n_seed}_wn{alpha_wn0}_{alpha_wn1}_T{T}_step{step}_t{end}_e_all.csv")

e1_p_data = e_all_p[n_e]
e1_c_data = e_all_c[n_e]

plt.plot(t_data, e1_c_data, color="tab:green", label = "Conventional")
plt.plot(t_data, e1_p_data, color="tab:red", label = "Proposed")

plt.xlabel("time (s)")
plt.ylabel(f"tracking error of link {n_e} (rad)")

plt.xlim(start_plt,end_plt)
#plt.ylim(-40,40)
plt.legend()
plt.grid()

# plt.savefig(f"data/s{n_seed}_m{alpha_lambda}_wn{alpha_wn0}_{alpha_wn1}_s{alpha_s0}_{alpha_s1}_{alpha_s2}_T{T}_step{step}_t{end}_1.png")

plt.show()
