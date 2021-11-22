import csv
import numpy as np
from matplotlib import pyplot as plt

n_seed = 22
alpha_lambda = 0.4
T = 1000
end = 100

n_l = -1 + 3

t_data = np.loadtxt(f"time{end}.csv")
#e_data = np.loadtxt(f"p_s{s}_e_all.csv")
#e_all = np.load(f"p_s{s}_e_all.npy",allow_pickle=True)

e_all_p = np.loadtxt(f"k_s{n_seed}_m{alpha_lambda}_T{T}_t{end}_e_all.csv")
e_all_c = np.loadtxt(f"k_s{n_seed}_m0.0_T{T}_t{end}_e_all.csv")

e1_p_data = e_all_p[n_l+3]
e2_p_data = e_all_p[n_l+6]
e3_p_data = e_all_p[n_l+9]
e4_p_data = e_all_p[n_l+12]

e1_c_data = e_all_c[n_l+3]
e2_c_data = e_all_c[n_l+6]
e3_c_data = e_all_c[n_l+9]
e4_c_data = e_all_c[n_l+12]


fig = plt.figure()

ax1 = fig.add_subplot(2,2,1)
ax2 = fig.add_subplot(2,2,2)
ax3 = fig.add_subplot(2,2,3)
ax4 = fig.add_subplot(2,2,4)

ax1.plot(t_data, e1_c_data, label = "Conventional")
ax2.plot(t_data, e2_c_data, label = "Conventional")
ax3.plot(t_data, e3_c_data, label = "Conventional")
ax4.plot(t_data, e4_c_data, label = "Conventional")

ax1.plot(t_data, e1_p_data, label = f"Proposed_m{alpha_lambda}")
ax2.plot(t_data, e2_p_data, label = f"Proposed_m{alpha_lambda}")
ax3.plot(t_data, e3_p_data, label = f"Proposed_m{alpha_lambda}")
ax4.plot(t_data, e4_p_data, label = f"Proposed_m{alpha_lambda}")

#ax1.xlim(0,20)
ax1.legend()
ax1.grid()
#ax2.xlim(0,20)
ax2.legend()
ax2.grid()
#ax3.xlim(0,20)
ax3.legend()
ax3.grid()
#ax4.xlim(0,20)
ax4.legend()
ax4.grid()

plt.show()