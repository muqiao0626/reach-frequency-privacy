import numpy as np
from matplotlib import pyplot as plt
import random
from collections import Counter
from collections import defaultdict
random.seed(10)

N = 2000
T = 2000
n = int(N/T)
B = 150
b_floor = 0.1
b_cap = 10
mu, sigma = 0.0, 0.5
second_price = np.random.lognormal(mu, sigma, N)
for i, price in enumerate(second_price):
  if price < 0.1:
    second_price[i] = 0.1
rand_num = np.random.rand(N)

parameter_string = "N = {N}, mu = {mu}, sigma = {sigma}".format(N = N, mu = mu, sigma = sigma)
plt.plot(range(0, N), second_price, 'b-')
plt.ylabel("second price")
plt.xlabel("auction index")
plt.title(parameter_string)
plt.show()

N_user = 120
user_id = np.random.choice(N_user, T)
cap = 3

# simulation of dogd
def simulation (pctr = 1.0, step_size = 0.1, S_group = 10, plot = True):
  ps = [0]
  N_group = N_user/S_group
  group_id = user_id//S_group
  wins = np.array([0]*(T+1))

  nn = np.array([0]*N_user)
  f = np.zeros((cap+1, T+1))
  for i in range(min(cap+1,T+1)):
    f[i,i] = (1.0/S_group)**i
  R = np.zeros((cap+1, T+1))

  projected_spend = np.array(range(0, T))*B/T+B/T
  actual_spend = np.array([0]*T)
  total_actual_spend = np.array([0]*T)
  num_of_clicks = np.array([0]*T)
  bs = [b_cap]
  ls = [1/b_cap]
  diffs = [0]
  for t in range(0, T):
    ti = t+1
    R[:,ti] = R[:,ti-1]

    p = 0
    U = range(group_id[ti-1]*S_group, (group_id[ti-1]+1)*S_group)
    for i in U:
      for k in range(cap):
        p += 1.0/S_group*f[k,nn[i]]
    ps.append(p)

    if t == 0:
      b = b_cap
      l = 1/b_cap
    else:
      prev_l = l
      diff = 1 - actual_spend[t-1]*T/B
      l = max(0.1, prev_l - step_size*diff)
      b = max(b_floor, min(b_cap, p/l))
      ls.append(l)
      diffs.append(diff)
      bs.append(b)
    for j in range(0, n):
      i = t*n+j
      if b >= second_price[i]: # win the impression
        if rand_num[i] < pctr: # win the click
          wins[ti] = 1
          actual_spend[t] += second_price[i]/pctr
          num_of_clicks[t] += 1
    total_actual_spend[t] = total_actual_spend[t-1] + actual_spend[t]
    if total_actual_spend[t] > B:
      break

    if wins[ti] == 1:
      for i in U:
        nn[i] += 1
        for li in range(cap+1):
          j = nn[i]
          if j > li:
            if f[li,j] == 0:
              f[li,j] = f[li,j-1]*j/(j-li)*(1-1.0/S_group)
          for m in range(li+1, cap+1):
            R[m,ti] += (m-li)*(f[li,j-1]-f[li,j])
          #print (t, R[t])

  if plot:
    fig, ax = plt.subplots()
    plt.plot(range(0, T), bs, 'b-', label = 'bid price')
    plt.ylabel("bid price")
    plt.xlabel("maintenance cycle")
    plt.legend()
    plt.show()
  return total_actual_spend, bs, ls, ps, R, wins

total_actual_spend, bs, ls, ps, R, wins = simulation()

S_groups = [1,2,3,4,5,6,8,10,12,20,40,60,120]
spendss = []
bsss = []
psss = []
Rss = []
winsss = []
reach_arrayss = []
for i in range(200):
  second_price = np.random.lognormal(mu, sigma, N)
  for i, price in enumerate(second_price):
    if price < 0.1:
      second_price[i] = 0.1
  rand_num = np.random.rand(N)

  spends = []
  bss = []
  pss = []
  Rs = []
  reach_arrays = []
  for S in S_groups:
    total_actual_spend, bs, ls, ps, R, wins = simulation(S_group = S, plot = False)
    spends.append(total_actual_spend)
    bss.append(bs)
    pss.append(ps)
    Rs.append(R[-1,1:])

    wins_labels = []
    wins_label = [1 if w else np.nan for w in wins]
    wins_labels.append(wins_label)
    win_mask = wins_label[1:]
    winned_users = user_id*win_mask
    c = cap
    counter = Counter()
    reach = 0
    reach_array = []
    for user in winned_users:
      if np.isnan(user):
        reach_array.append(reach)
      else:
        counter[user] += 1
        if counter[user] <= c:
          reach += 1
        reach_array.append(reach)
    reach_arrays.append(reach_array) 
    
  spendss.append(spends)
  bsss.append(bss)
  psss.append(pss)
  Rss.append(Rs)
  reach_arrayss.append(reach_arrays)

spends = np.array(spendss)
spends = np.mean(spends, axis = 0)
reach_arrays = np.array(reach_arrayss)
reach_arrays = np.mean(reach_arrays, axis = 0)

roi = []
for i in range(len(S_groups)):
  roi.append(reach_arrays[i][-1]/spends[i][-1])

plt.rc('font', size=16)
res = []
groups = []
for i in [0,1,3,8,10,12]:
  res.append(roi[i]/roi[0]%100)
  groups.append(S_groups[i])
  print (S_groups[i])
fig, ax = plt.subplots()
plt.plot(groups, res/res[0], '-o')
plt.ylabel("relative ROAS (%)")
plt.xlabel("group size (k)")
plt.savefig('figure3.svg')

