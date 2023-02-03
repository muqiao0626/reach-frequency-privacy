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

T = 180
S_groups = [1,2,3,4,5,6,8,10,12,20,40,60,120]
Rss = []
reachess = []
for S in S_groups:
  Rs, reaches = macro_simulation(S_group = S, T = T)
  Rss.append(Rs)
  reachess.append(reaches)

reachess = np.array(reachess)

rvars = np.var(reachess, axis = 1)
reach_vars = []
for i,S in enumerate(S_groups):
  reach_vars.append(rvars[i,-1,-1])

plt.rc('font', size=16)
res = []
groups = []
for i in [0,1,3,8,10,12]:
  res.append(reach_vars[i])
  groups.append(S_groups[i])
  print (S_groups[i])
fig, ax = plt.subplots()
plt.plot(groups, res, '-o')
plt.ylabel("variance")
plt.xlabel("group size (k)")
plt.savefig('figure2c.svg')

