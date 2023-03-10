import numpy as np
from matplotlib import pyplot as plt
import random
from collections import Counter
from collections import defaultdict
random.seed(10)

N = 2000
T = 2000
n = int(N/T)
B = 500
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

N_user = 144
user_id = np.random.choice(N_user, T)
cap = 3

S_group = 12
N_group = N_user//S_group
targeted_groups = [1,2,3,4,6,12]
targeted_members = []
for group in targeted_groups:
  targeted_member = []
  members_in_one_group = S_group//group
  for i in range(group):
    targeted_member.extend(range(S_group*i, S_group*i+members_in_one_group))
  targeted_members.append(targeted_member)

# simulation of dogd
def simulation (pctr = 1.0, step_size = 0.1, S_group = 12, plot = True, targeted_group = 6):
  bid = 4*B/T
  ps = [0]
  group_id = user_id//S_group
  wins = np.array([0]*(T+1))

  nn = np.array([0]*N_user)
  f = np.zeros((cap+1, T+1))
  for i in range(min(cap+1,T+1)):
    f[i,i] = (1.0/S_group)**i
  R = np.zeros((cap+1, T+1))

  projected_spend = np.array(range(0, T))*B/T+B/T
  actual_spend = [0]*T
  total_actual_spend = [0]*T
  num_of_clicks = [0]*T
  bs = [bid]
  ls = [1/bid]
  diffs = [0]
  for t in range(0, T):
    ti = t+1
    R[:,ti] = R[:,ti-1]

    p = 0
    if group_id[ti-1] < targeted_group:
      U = range(group_id[ti-1]*S_group, (group_id[ti-1]+1)*S_group)
      for i in U:
        for k in range(cap):
          p += 1.0/S_group*f[k,nn[i]]
    ps.append(p)

    if t == 0:
      b = bid
      l = 1/bid
    else:
      prev_l = l
      diff = 1 - actual_spend[t-1]*T/B
      l = 1/bid
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
      if group_id[ti-1] < targeted_group:
        for i in U:
          nn[i] += 1
          for li in range(cap+1):
            j = nn[i]
            if j > li:
              if f[li,j] == 0:
                f[li,j] = f[li,j-1]*j/(j-li)*(1-1.0/S_group)
            for m in range(li+1, cap+1):
              R[m,ti] += (m-li)*(f[li,j-1]-f[li,j])

  if plot:
    fig, ax = plt.subplots()
    plt.plot(range(0, T), bs, 'b-', label = 'bid price')
    plt.ylabel("bid price")
    plt.xlabel("maintenance cycle")
    plt.legend()
    plt.show()
  return total_actual_spend, bs, ls, ps, R, wins

total_actual_spend, bs, ls, ps, R, wins = simulation()

targeted_groups = [1,2,3,4,6,12]
spendss = []
bsss = []
psss = []
Rss = []
winsss = []
reach_arrayss = []
for i in range(50):
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
  for i, group in enumerate(targeted_groups):
    total_actual_spend, bs, ls, ps, R, wins = simulation (S_group = 12, plot = False, targeted_group = group)
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
      if np.isnan(user) or user not in targeted_members[i]:
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
for i in range(len(targeted_groups)):
  roi.append(reach_arrays[i][-1]/spends[i][-1])

plt.rc('font', size=16)
res = []
for group in targeted_groups:
  members_in_one_group = S_group//group
  res.append(members_in_one_group/S_group)

plt.plot(res, roi/roi[0]*100, '-o')
plt.ylabel("relative ROAS (%)")
plt.xlabel("coverage")
plt.savefig('figure4.svg')

