import numpy as np
from matplotlib import pyplot as plt
import random
from scipy.stats import binom
from collections import Counter
import seaborn as sns
random.seed(10)

def simulation(group_id, S_group, N_user, cap, T):
  user_id = []
  for id in group_id:
    U = range(id*S_group, (id+1)*S_group)
    user_id.append(np.random.choice(U))

  nn = np.array([0]*N_user)
  f = np.zeros((cap+1, T+1))
  for i in range(min(cap+1,T+1)):
    f[i,i] = (1.0/S_group)**i
  R = np.zeros((cap+1, T+1))

  for ti in range(1, T+1):
    R[:,ti] = R[:,ti-1]
    U = range(group_id[ti-1]*S_group, (group_id[ti-1]+1)*S_group)
    for i in U:
      nn[i] += 1
      for l in range(cap+1):
        j = nn[i]
        if j > l:
          if f[l,j] == 0:
            f[l,j] = f[l,j-1]*j/(j-l)*(1-1.0/S_group)
        for m in range(l+1, cap+1):
          R[m,ti] += (m-l)*(f[l,j-1]-f[l,j])
        #print (t, R[ti])
  
  reach_arrays = []
  for i in range(cap):
    c = i+1
    counter = Counter()
    reach = 0
    reach_array = []
    for user in user_id:
      counter[user] += 1
      if counter[user] <= c:
        reach += 1
      reach_array.append(reach)
    reach_arrays.append(reach_array)
  reach_arrays = np.array(reach_arrays)

  return R, reach_arrays

def macro_simulation(N_user = 120, S_group = 6, T = 500, cap = 3):
  N_group = N_user//S_group
  user_id = np.random.choice(N_user, T)
  group_id = user_id//S_group
  Rs = []
  reaches = []
  for i in range(2000):
    R, reach = simulation(group_id, S_group, N_user, cap, T)
    Rs.append(R[:,1:])
    reaches.append(reach)
  return Rs, reaches

T = 1000
S_group = 6
Rs, reaches = macro_simulation(S_group = S_group, T = T)

reports1 = []
reports2 = []
reports3 = []
reports4 = []
for reach in reaches:
  reports1.append(reach[-1][125-1])
  reports2.append(reach[-1][250-1])
  reports3.append(reach[-1][500-1])
  reports4.append(reach[-1][1000-1])

Rss = np.array(Rs)
R = Rss[0,-1,:][250-1]

plt.rc('font', size=16)
sns.distplot(reports2, hist=True, kde=True, 
             bins=30, color = 'darkblue', 
             hist_kws={'edgecolor':'black'},
             kde_kws={'linewidth': 4})
plt.axvline(R, color='r', linestyle='-', linewidth=2)
plt.axvline(np.mean(reports2), color='k', linestyle='dashed', linewidth=2)
plt.ylabel("density")
plt.xlabel("reach")
plt.savefig('figure2a.svg')

plt.figure()
sns.distplot(reports1, hist=False, kde=True, bins=30, color = 'blue', hist_kws={'edgecolor':'black'}, kde_kws={'linewidth': 1}, label = str(125)+' impressions')
sns.distplot(reports2, hist=False, kde=True, bins=30, color = 'orange', hist_kws={'edgecolor':'black'}, kde_kws={'linewidth': 1}, label = str(250)+' impressions')
sns.distplot(reports3, hist=False, kde=True, bins=30, color = 'green', hist_kws={'edgecolor':'black'}, kde_kws={'linewidth': 1}, label = str(500)+' impressions')
sns.distplot(reports4, hist=False, kde=True, bins=30, color = 'red', hist_kws={'edgecolor':'black'}, kde_kws={'linewidth': 1}, label = str(1000)+' impressions')
plt.legend()
plt.ylabel("density")
plt.xlabel("reach")
plt.savefig('figure2b.svg')

