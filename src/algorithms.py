# Import Module
import os
import time

# from stable_baselines3.common.vec_env import SubprocVecEnv

import matplotlib.pyplot as plt 
import secrets
import random

# from numpy.distutils.system_info import x11_so_dir
from numpy.random import choice
import numpy as np
import math

import functions as f
from ortools.linear_solver import pywraplp
#Folder Path
#import GreedyAlgo
from scipy.optimize import minimize, LinearConstraint
# import test_rl as RL

# from stable_baselines3 import PPO

KaistPath = r"C:\Users\Abder\OneDrive - UniversitÃ© Mohammed VI Polytechnique\Task allocation in crowdsourcing environments\Implementation\Dataset\KAIST"
NewYorkPath = r"C:\Users\Abder\OneDrive - UniversitÃ© Mohammed VI Polytechnique\Task allocation in crowdsourcing environments\Implementation\Dataset\NewYork"

tasksp = []
indexw = []
Mw = []
Mt = []
myMw = []
myMt = []
myMwp = []
L = []
xt = []
nt = []
zt = []
Ht = []
At = False



def OrToolSolver_reduction(workers,tasks,rewards,PoI,___,__,_):
    global myMt, myMw
    myInitialize(workers, tasks)
    cpw = f.C_Point_Worker(PoI)
    m = len(workers)
    n = len(tasks)
    k = len(PoI)
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Define decision variables
    x = {}
    y = {}
    for i in range(n):
        for j in range(m):
            x[i, j] = solver.IntVar(0, 1, 'x[%d,%d]' % (i, j))
        for t in range(k):
            y[i, t] = solver.IntVar(0, 1, 'y[%d,%d]' % (i, t))

    # Define constraints
    for i in range(n):
        solver.Add(solver.Sum([x[i, j] * rewards[j][i] for j in range(m)]) <= tasks[i][2])
        for t in range(k):
            # solver.Add(solver.Sum([cpw[t][j] * x[i, j] for j in range(m)]) <= m * y[i, t])
            solver.Add(solver.Sum([cpw[t][j] * x[i, j] for j in range(m)]) >= y[i, t])
    for j in range(m):
        solver.Add(solver.Sum([x[i, j] for i in range(n)]) <= 1)

    # print("starting the OrTool sovler")
    solver.Maximize(solver.Sum([solver.Sum([point[1] * y[i,point[0][0]] for point in tasks[i][1]]) for i in range(n)]))
    # solver.Maximize(solver.Sum([solver.Sum([point[1] * (solver.Sum([cpw[point[0][0]][j] * x[i, j] for j in range(m)])) for point in tasks[i][1]]) for i in range(n)]))


    # Solve the problem
    status = solver.Solve()
    # print("solved!")

    if status == pywraplp.Solver.OPTIMAL:
        # x_solution = [[] for i in range(n)]
        # for i in range(n):
        #     for j in range(m):
        #         x_solution[i].append(x[i, j].solution_value())
        # return solver.Objective().Value(), x_solution
        # print('solution: ')
        # print('objective value = ', solver.Objective().Value())
        for t in range(n):
            for w in range(m):
                if int(x[t, w].solution_value()) != 0:
                    myMt[t].append(workers[w])
                    myMw[w] = tasks[t]
        return myMt, myMw, solver.Objective().Value()
        #         print('x_%d_%d =' % (i, j), x[i, j].solution_value())
        # # print('sum(x) =', f.Value())
    else:
        print('No satisfying solution')
        return myMt, myMw, rewards

def OrToolSolver(workers,tasks,rewards,PoI,___,__,_):
    global myMt, myMw
    myInitialize(workers, tasks)
    cpw = f.C_Point_Worker(PoI)
    m = len(workers)
    n = len(tasks)

    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Define decision variables
    x = {}
    for i in range(n):
        for j in range(m):
            x[i, j] = solver.IntVar(0, 1, 'x[%d,%d]' % (i, j))

    # Define constraints
    for i in range(n):
        solver.Add(solver.Sum([x[i, j] * rewards[j][i] for j in range(m)]) <= tasks[i][2])
    for j in range(m):
        solver.Add(solver.Sum([x[i, j] for i in range(n)]) <= 1)

    # print("starting the OrTool sovler")
    solver.Maximize(solver.Sum([solver.Sum([point[1] * (solver.Sum([cpw[point[0][0]][j] * x[i, j] for j in range(m)])) for point in tasks[i][1]]) for i in range(n)]))


    # Solve the problem
    status = solver.Solve()
    # print("solved!")

    if status == pywraplp.Solver.OPTIMAL:
        # x_solution = [[] for i in range(n)]
        # for i in range(n):
        #     for j in range(m):
        #         x_solution[i].append(x[i, j].solution_value())
        # return solver.Objective().Value(), x_solution
        # print('solution: ')
        # print('objective value = ', solver.Objective().Value())
        for t in range(n):
            for w in range(m):
                if int(x[t, w].solution_value()) != 0:
                    myMt[t].append(workers[w])
                    myMw[w] = tasks[t]
        return myMt, myMw, solver.Objective().Value()
        #         print('x_%d_%d =' % (i, j), x[i, j].solution_value())
        # # print('sum(x) =', f.Value())
    else:
        print('No satisfying solution')
        return myMt, myMw, rewards

# def parallel_rl_PPO(workers,tasks,rewards,total_timesteps, episode_steps, n_procs, file_path):
#     global myMt, myMw
#     myInitialize(workers, tasks)
#     n = len(tasks)
#     m = len(workers)

#     envs = [f.make_custom_env(n, m, tasks, workers, f.Ut , f.Rt, rewards, episode_steps) for _ in range(n_procs)]
#     envs = SubprocVecEnv(envs)

#     model = PPO("MlpPolicy", envs, verbose=0)
#     model.learn(total_timesteps = total_timesteps, log_interval = 4)
#     model.save(file_path + f"_{n}_tasks")
#     # myMt = env.myMt

#     for t in range(len(myMt)):
#         for worker in myMt[t]:
#             w = worker[0]
#             myMw[w] = tasks[t]
#     return myMt, myMw, rewards


# def RLsolution(workers,tasks,rewards,PoI,___,__,_):
#     global myMt, myMw
#     myInitialize(workers, tasks)
#     episode_steps = 5000
#     n = len(tasks)
#     m = len(workers)
#     env = RL.CustomEnv(n, m, tasks, workers,  f.Ut , f.Rt,rewards, episode_steps)

#     model = PPO("MlpPolicy", env, verbose=0)
#     model.learn(total_timesteps=500000, log_interval=4)
#     model.save("dqn_cartpole")
#     myMt = env.myMt
#     # num_episode = 0
#     # while num_episode < 1000:
#     #     done = False
#     #     env.reset()
#     #     total_RL_reward = 0
#     #     while not done:
#     #         action = env.action_space.sample()
#     #         state, reward, done = env.step(action)
#     #         total_RL_reward += reward
#     #     num_episode +=1
#     # for task in tasks:
#     #     for worker in workers:
#     #         w = worker[0]
#     #         t = task[0]
#     #         if state[t][w] == 1:
#     #             myMw[w] = task
#     #             myMt[t].append(worker)
#     for t in range(len(myMt)):
#         for worker in myMt[t]:
#             w = worker[0]
#             myMw[w] = tasks[t]
#     return myMt, myMw, rewards

def get_names(compared_algorithms,reward_scheme):
    names = []
    for algo in compared_algorithms:
        names.append(algo.__name__)
    if reward_scheme !=0:
        compared_algorithms.append(CSTAg)
        names.append("CSTAg")
    return compared_algorithms, names

# Algo many-to-many with utility
def AlgoM2Me(workers, tasks, myRwd):
    global myMt, myMw, myMwp
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    for task in tasks:
        t = task[0]
        workers_list = [worker[0] for worker in workers]
        S, new_rewards = MCLB(workers, workers_list, task, rewards)
        rewards = f.copy_reward(new_rewards)
        myMt[t] = S.copy()
        for w in S: myMwp[w[0]].append(task)
    return myMt, myMw, rewards

# Algo many-to-many with utility
def AlgoM2Mu(workers, tasks, myRwd):
    global myMt, myMw, myMwp
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    for task in tasks:
        t = task[0]
        workers_list = [worker[0] for worker in workers]
        S, new_rewards = MCLButility(workers, workers_list, task, rewards)
        rewards = f.copy_reward(new_rewards)
        myMt[t] = S.copy()
        for w in S: myMwp[w[0]].append(task)
    return myMt, myMw, rewards

def myInitialize(workers, tasks):
    global myMt, myMw, myMwp

    myMw = [None for i in range(len(workers))]
    myMt = [[].copy() for i in range(len(tasks))]
    myMwp = [[].copy() for i in range(len(workers))]

def initialize(workers,tasks,rewards):
    global L, indexw, Mw, Mt, xt, nt, zt, Ht, At
    #copyCworkerTask()
    L = f.workerInterest(tasks,rewards)
    indexw = [0 for i in range(len(workers))]

    Mw = [None for i in range(len(workers))]
    Mt = [[].copy() for i in range(len(tasks))]

    xt = [[0 for i in  range(len(workers))].copy() for j in range(len(tasks))]
    nt = [[0 for i in  range(len(workers))].copy() for j in range(len(tasks))]
    zt = [[[[0,[].copy()].copy() for t in range(400)].copy() for i in  range(len(workers))] for j in range(len(tasks))]
    Ht = [[].copy() for i in range(len(tasks))]
    At = [False for i in range(len(tasks))]

def stableTaskAssignment(workers,tasks,myRwd,pois, rewardScheme,___,____):
    start_time = f.process_time()
    #global L,rewards,indexw,Mw,Mt,xt,nt,zt,Ht,At,cWorkerTask,logger, tasksp
    global Mw, Mt, tasksp, L, indexw
    #initialCWorkerTask = copyCWorkerTask(cWorkerTask)
    tasksp = f.copyTasks(tasks)
    rewards = f.copy_reward(myRwd)
    current_rewards = f.copy_reward(myRwd)
    initialize(workers,tasks,rewards)
    #R = []
    stack = workers.copy()
    while len(stack)>0:
        worker = stack.pop()
        w = worker[0]
        if indexw[w] < len(L[w]):
            task = tasksp[L[w][indexw[w]][0]]
            t = task[0]
            indexw[w] = indexw[w] + 1
            list_of_workers = [worker]

            # current_rewards = f.copy_reward(rewards)
            # rewards = f.reward_modification(tasksp[t],Mt[tasksp[t][0]],list_of_workers,current_rewards,rewards,workers)

            '''
            # changes done
            old_intersection_points = f.get_total_intersection(Mt[tasksp[t][0]], tasksp[t], f.cWorkerTaskp)
            remaining_points = f.retrieveFromC(f.cWorkerTaskp[w][t],old_intersection_points)
            rewards[w][t] = (rewards[w][t]*(f.getTotalWeightPoint(remaining_points)/f.Ut(task,[worker])))/task[2]
            '''
            Mw[w] = tasksp[t];
            Mt[t].append(worker)

            if rewardScheme == 0:
                R = workerSelection(tasksp[t], worker,rewards)
            else:
                R = workerSelectionProportional(tasksp[t], worker,rewards, workers)
            for r in R:
                index = None
                #rint("r == ", r)
                for i in range(len(Mt[t])):
                    #rint("Mt == " ,Mt[t][i])
                    #rint("m = r = ", Mt[t][i][0] == r[0] )
                    if Mt[t][i][0] == r[0]:
                        index = i
                        break
                Mt[t].pop(index)
                Mw[r[0]] = None
                stack.append(r)
            #rewards = f.rest_rewards(task, R, current_rewards,rewards)
    timex = f.process_time() -start_time
    return Mt,Mw, timex

def workerSelection(task, worker,rewards):
    global L, indexw, Mw, Mt, xt, nt, zt, Ht, At
    t = task[0]
    w = worker[0]
    xt[t][w] = 1
    intersectionPoints = f.cWorkerTaskp[w][t].copy()
    if rewards[w][t] == 0 :
        return [worker]
    for point in intersectionPoints:
        p = point[0][0]
        zm = 0
        '''
        count = 0
        for worker1 in Ht[t]:
            if len(worker1) == 0 :
                count = count + 1        
        for i in range(count):
            Ht.pop(Ht.index([]))
        '''
        for worker1 in Ht[t]:
            w1 = worker1[0]
            zm = zm + zt[t][w1][p][0]
        zt[t][w][p][0] = 1 - zm
        v = f.getWeightPoint(task,p)
        nt[t][w] = nt[t][w]+zt[t][w][p][0]*v
    nt[t][w] = nt[t][w] * (task[2]/rewards[w][t])

    value = 0
    for point in task[1]:
        for worker1 in Ht[t]:
            w1 = worker1[0]
            v = f.getWeightPoint(task, point[0][0])
            value = value + zt[t][w1][point[0][0]][0]*v
    # line 7 8 9

    # modification done according to the comment and not to the algorithm :
    '''
    if len(Ht[t]) > 0:
        HtRewards = 0
        for wor in Ht[t]:
            HtRewards += rewards[wor[0]][t]

        value = value * (task[2]/ HtRewards)
    '''
    # modification end

    if nt[t][w] <= 2*value:
        return [worker]
    else:
        # line 10
        bool = 0
        myRange = len(Ht[t])
        for i in range(myRange):
            if nt[t][w] >= nt[t][Ht[t][i][0]]:
                bool = 1
                Ht[t].insert(i, worker)
                break
        if bool == 0 or len(Ht[t]) == 0:
            Ht[t].append(worker)

        # line 11
        totalReward = 0
        k = -1
        myRange = len(Ht[t])
        for i in range(myRange):
            hworker = Ht[t][i]
            #rint(hworker)
            #rint(t)
            totalReward = totalReward + rewards[hworker[0]][t]
            if (totalReward >= task[2] or i == (len(Ht[t]))-1) and k == -1:
                k = i
                totalReward = totalReward - rewards[hworker[0]][t]
                break

        # line 12
        btM = task[2] - totalReward
        # line 13
        workerp = Ht[t][k]
        wp = workerp[0]
        # line 14
        beta = min([(btM / rewards[wp][t]), 1])
        # line 15 16 17
        intersectionPointsPrime = f.cWorkerTaskp[wp][t].copy()
        for point in intersectionPointsPrime:
            p = point[0][0]
            zt[t][wp][p][0] = (beta / xt[t][wp]) * zt[t][wp][p][0]
        # line 18
        R = []
        # line 19 20 21
        if xt[t][wp] == 1 and beta < 1:
            R = [workerp]
        # line 22
        xt[t][wp] = beta
        # back here if something is wrong
        # line 23 24 25 26 27 28 29
        for i in range(len(Ht[t])-1, k, -1):
            workert = Ht[t][i]
            wt = workert[0]
            Ht[t].pop(i)
            if (xt[t][wt] == 1):
                R.append(workert)
    return R

def workerSelectionProportional(task, worker,rewards,workers):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTaskp, tasksp
    global L, indexw, Mw, Mt, xt, nt, zt, Ht, tasksp,At
    t = task[0]
    w = worker[0]
    bt = task[2]
    if At[t] == False and rewards[w][t]>=0.2*bt and rewards[w][t]<=bt:
        # 2 3 4 5
        At[t] = True
        mu = Mt[t].copy()
        Mt[t] = [worker].copy()
        bt = bt - rewards[w][t]
        task[2] = bt
        tasksp[t][2] = bt
        # 6 7 8 9 10
        for workerp in workers:
            wp = workerp[0]
            if wp != w:
                L1 = f.cWorkerTaskp[wp][t].copy()
                L2 = f.cWorkerTaskp[w][t].copy()
                f.cWorkerTaskp[wp][t] = f.retrieveFromC(L1,L2).copy()
        Ht[t] = []
        R = []
        #11 12 13 14 15
        for workerp in mu:
            wp = workerp[0]
            # I guess there is an error in their algorithm otherwise a worker will be matched with more than one task
            if wp != w:
                Mt[t].append(workerp)
                nt[t][wp] = 0
                R = R + workerSelection(task, workerp, rewards)
        return R
    else:
        return workerSelection(task, worker,rewards)

def AlgoRR(few_workers, few_tasks, myRwd,PoIs,rewardScheme,___,____, by_part=0,workers=None,tasks=None):
    start_time = f.process_time()
    global myMt, myMw
    task_removed_from_system = []
    if tasks == None:
        tasks = few_tasks
    if workers == None:
        workers = few_workers
    if by_part == 0 :
        myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    current_rewards = f.copy_reward(myRwd)
    tasksIndex = random.sample([i[0] for i in few_tasks], len(few_tasks))
    # tasksIndex = [i for i in range(len(tasks))]
    workersIndex = [i[0] for i in few_workers]

    workerAdded = True
    while len(workersIndex) > 0 and workerAdded:

        tasksIndex = random.sample([i[0] for i in few_tasks], len(few_tasks))
        i = 0
        workerAdded = False
        while i < len(few_tasks) and len(workersIndex) > 0:
            t = tasksIndex[i]
            L = [w for w in workersIndex if rewards[w][t] != 0]

            task = tasks[t]
            list_of_workers = [w for w in few_workers if w[0] in L]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)

            # print(L)
            # L.sort(key= lambda w: rewards[w][t])
            wIndex = -1
            maxUtility = f.Ut(tasks[t], myMt[t])
            for w in L:
                setOfWorker = myMt[t] + [workers[w]]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    newMaxUtility = f.Ut(tasks[t], setOfWorker)
                    if maxUtility < newMaxUtility:
                        workerAdded = True
                        wIndex = w
                        maxUtility = newMaxUtility

            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workersIndex.remove(wIndex)
                list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]

            else:
                task_removed_from_system.append(t)
            rewards = f.rest_rewards(task, list_of_workers, current_rewards, rewards)
            i += 1
            while i < len(tasksIndex) and tasksIndex[i] in task_removed_from_system:
                i += 1

        # print("len = ", len(workersIndex))
        # print(i)
    timex = f.process_time() - start_time
    return myMt, myMw, timex

def AlgoRRbias(few_workers, few_tasks, myRwd,PoIs,rewardScheme, by_part=0,workers=None,tasks=None):
    global myMt, myMw
    if tasks == None:
        tasks = few_tasks
    if workers == None:
        workers = few_workers
    if by_part == 0 :
        myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    current_rewards = f.copy_reward(myRwd)
    tasksIndex = random.sample([i[0] for i in few_tasks], len(few_tasks))
    # tasksIndex = [i for i in range(len(tasks))]
    workersIndex = [i[0] for i in few_workers]

    workerAdded = True
    while len(workersIndex) > 0 and workerAdded:

        tasksIndex = random.sample([i[0] for i in few_tasks], len(few_tasks))
        i = 0
        workerAdded = False
        while i < len(few_tasks) and len(workersIndex) > 0:
            t = tasksIndex[i]
            L = [w for w in workersIndex if rewards[w][t] != 0]

            task = tasks[t]
            list_of_workers = [w for w in few_workers if w[0] in L]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)

            # print(L)
            # L.sort(key= lambda w: rewards[w][t])
            wIndex = -1
            maxUtility = f.Ut(tasks[t], myMt[t])
            for w in L:
                setOfWorker = myMt[t] + [workers[w]]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    newMaxUtility = f.Ut(tasks[t], setOfWorker)
                    if maxUtility < newMaxUtility:
                        workerAdded = True
                        wIndex = w
                        maxUtility = newMaxUtility

            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workersIndex.remove(wIndex)
                list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]
            rewards = f.rest_rewards(task,list_of_workers,current_rewards,rewards)
            i += 1

        # print("len = ", len(workersIndex))
        # print(i)

    return myMt, myMw, rewards

def AlgoRRbp(workers, tasks, myRwd, size):
    global myMt, myMw
    return myMt, myMw, myRwd


def AlgoWFIVpp(workers, tasks, myRwd, set_PoI):
    global myMt, myMw
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    c_worker_point = f.get_c_worker_point(set_PoI)
    workers_index = [i[0] for i in workers]
    workerAdded = True
    while len(workers_index) > 0 and workerAdded:
        list_of_importance = f.get_list_of_point_by_importance(c_worker_point)
        tasks_index = f.get_task_index_sorted_by_importance(list_of_importance,tasks,myMt)
        i = 0
        workerAdded = False
        while i < len(tasks) and workerAdded == False:
            t = tasks_index[i]
            L = [w for w in workers_index if rewards[w][t] != 0]
            task = tasks[t]
            wIndex = -1
            maxUtility = f.Ut(tasks[t], myMt[t])

            list_of_workers = [w for w in workers if w[0] in L]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)

            for w in L:
                setOfWorker = myMt[t] + [workers[w]]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    newMaxUtility = f.Ut(tasks[t], setOfWorker)
                    if maxUtility < newMaxUtility:
                        workerAdded = True
                        wIndex = w
                        maxUtility = newMaxUtility

            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workers_index.remove(wIndex)
                c_worker_point[wIndex] = [0 for p in set_PoI]
                list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]

            rewards = f.rest_rewards(task, list_of_workers, current_rewards, rewards)

            i += 1
    plop = 0
    return myMt, myMw, rewards


def AlgoWFIV(workers, tasks, myRwd, set_PoI,rewardScheme,list_of_importance,cpw):
    start_time = f.process_time()
    global myMt, myMw
    task_removed_from_system = []
    covered_point = [[] for __ in tasks]
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    workers_index = [i[0] for i in workers]
    workerAdded = True
    #cpw = np.sum(np.array(c_worker_point), axis=0)
    tasks_importance_value = f.get_task_importance_value_prim(list_of_importance,tasks,myMt)
    while len(workers_index) > 0 and workerAdded:
        i = 0
        workerAdded = False
        removed_task = []
        while i < len(tasks) and workerAdded == False:
            t = -1
            max_importance_value = 0
            for __ in range(len(tasks)):
                if tasks_importance_value[__] > max_importance_value and __ not in removed_task and __ not in task_removed_from_system:
                    max_importance_value = tasks_importance_value[__]
                    t = __
            removed_task.append(t)
            # if max_importance_value == 0:
            #     print(tasks_importance_value)
            #     break
            L = [w for w in workers_index if rewards[w][t] != 0]
            task = tasks[t]
            wIndex = -1
            maxUtility = f.Ut(tasks[t], myMt[t])

            list_of_workers = [w for w in workers if w[0] in L]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)

            for w in L:
                setOfWorker = myMt[t] + [workers[w]]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    newMaxUtility = f.Ut(tasks[t], setOfWorker)
                    if maxUtility < newMaxUtility:
                        workerAdded = True
                        wIndex = w
                        maxUtility = newMaxUtility

            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workers_index.remove(wIndex)
                # tasks_importance_value,list_of_importance ,covered_point= f.tasks_importance_value_modification_old(tasks_importance_value,list_of_importance,workers[wIndex],tasks[t],covered_point,myMt,tasks)
                tasks_importance_value, list_of_importance, covered_point= f.tasks_importance_value_modification(tasks_importance_value,list_of_importance,cpw,workers[wIndex],tasks[t],covered_point,myMt,tasks)
                #c_worker_point[wIndex] = [0 for p in set_PoI]
                #list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]
            else:
                task_removed_from_system.append(t)
            rewards = f.rest_rewards(task, list_of_workers, current_rewards, rewards)
            i += 1
            while i in task_removed_from_system:
                i += 1
    plop = 0
    timex = f.process_time() - start_time
    return myMt, myMw, timex

def AlgoWFIVbias(workers, tasks, myRwd, set_PoI,rewardScheme,list_of_importance,cpw):
    global myMt, myMw
    covered_point = [[] for __ in tasks]
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    workers_index = [i[0] for i in workers]
    workerAdded = True
    #cpw = np.sum(np.array(c_worker_point), axis=0)
    # c_worker_point,c_task_point = f.get_c_worker_point(set_PoI)
    # list_of_importance,[cpw ,cpt]= f.get_list_of_point_by_importance_bias(c_worker_point,c_task_point)
    tasks_importance_value = f.get_task_importance_value_prim(list_of_importance,tasks,myMt)
    while len(workers_index) > 0 and workerAdded:
        i = 0
        workerAdded = False
        removed_task = []
        while i < len(tasks) and workerAdded == False:
            t = -1
            max_importance_value = 0
            for __ in range(len(tasks)):
                if tasks_importance_value[__] > max_importance_value and __ not in removed_task:
                    max_importance_value = tasks_importance_value[__]
                    t = __
            removed_task.append(t)
            L = [w for w in workers_index if rewards[w][t] != 0]
            task = tasks[t]
            wIndex = -1
            maxUtility = f.Ut(tasks[t], myMt[t])

            list_of_workers = [w for w in workers if w[0] in L]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)

            for w in L:
                setOfWorker = myMt[t] + [workers[w]]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    newMaxUtility = f.Ut(tasks[t], setOfWorker)
                    if maxUtility < newMaxUtility:
                        workerAdded = True
                        wIndex = w
                        maxUtility = newMaxUtility

            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workers_index.remove(wIndex)
                tasks_importance_value,list_of_importance ,covered_point= f.tasks_importance_value_modification(tasks_importance_value,list_of_importance,cpw,workers[wIndex],tasks[t],covered_point,myMt,tasks)
                # tasks_importance_value,list_of_importance ,covered_point= f.tasks_importance_value_modification_bias(tasks_importance_value,list_of_importance,cpw,cpt,workers[wIndex],tasks[t],covered_point,myMt,tasks)
                #c_worker_point[wIndex] = [0 for p in set_PoI]
                #list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]
            i += 1
            rewards = f.rest_rewards(task, list_of_workers, current_rewards, rewards)
    plop = 0
    return myMt, myMw, rewards

def AlgoWFIVt(workers, tasks, myRwd, set_PoI):
    global myMt, myMw
    covered_point = [[] for __ in tasks]
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    c_worker_point, c_task_point = f.get_c_worker_point(set_PoI)
    workers_index = [i[0] for i in workers]
    workerAdded = True
    #cpw = np.sum(np.array(c_worker_point), axis=0)
    list_of_importance,cpw = f.get_list_of_point_by_importance(c_worker_point,c_task_point)
    tasks_importance_value = f.get_task_importance_value_prim(list_of_importance,tasks,myMt)
    while len(workers_index) > 0 and workerAdded:
        i = 0
        workerAdded = False
        removed_task = []
        while i < len(tasks) and workerAdded == False:
            t = -1
            max_importance_value = 0
            for __ in range(len(tasks)):
                if tasks_importance_value[__] > max_importance_value and __ not in removed_task:
                    max_importance_value = tasks_importance_value[__]
                    t = __
            removed_task.append(t)
            L = [w for w in workers_index if rewards[w][t] != 0]
            task = tasks[t]
            wIndex = -1
            maxUtility = f.Ut(tasks[t], myMt[t])

            list_of_workers = [w for w in workers if w[0] in L]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)

            for w in L:
                setOfWorker = myMt[t] + [workers[w]]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    newMaxUtility = f.Ut(tasks[t], setOfWorker)
                    if maxUtility < newMaxUtility:
                        workerAdded = True
                        wIndex = w
                        maxUtility = newMaxUtility

            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workers_index.remove(wIndex)
                tasks_importance_value,list_of_importance ,covered_point= f.tasks_importance_value_modification(tasks_importance_value,list_of_importance,cpw,workers[wIndex],tasks[t],covered_point,myMt,tasks)
                #c_worker_point[wIndex] = [0 for p in set_PoI]
                #list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]

            rewards = f.rest_rewards(task, list_of_workers, current_rewards, rewards)

            i += 1
    plop = 0
    return myMt, myMw, rewards

def AlgoWFIVb(workers, tasks, myRwd, set_PoI):
    global myMt, myMw
    covered_point = [[] for __ in tasks]
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    c_worker_point = f.get_c_worker_point(set_PoI)
    workers_index = [i[0] for i in workers]
    workerAdded = True
    list_of_importance = f.get_list_of_point_by_importance(c_worker_point)
    tasks_importance_value = f.get_task_importance_value_prim(list_of_importance,tasks,myMt)
    while len(workers_index) > 0 and workerAdded:
        i = 0
        workerAdded = False
        removed_task = []
        while i < len(tasks) and workerAdded == False:
            t = -1
            max_importance_value = 0
            for __ in range(len(tasks)):
                if tasks_importance_value[__] > max_importance_value and __ not in removed_task:
                    max_importance_value = tasks_importance_value[__]
                    t = __
            removed_task.append(t)
            L = [w for w in workers_index if rewards[w][t] != 0]
            task = tasks[t]
            wIndex = -1
            maxUtility = f.Ut(tasks[t], myMt[t])

            list_of_workers = [w for w in workers if w[0] in L]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)

            for w in L:
                setOfWorker = myMt[t] + [workers[w]]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    newMaxUtility = f.Ut(tasks[t], setOfWorker)
                    if maxUtility < newMaxUtility:
                        workerAdded = True
                        wIndex = w
                        maxUtility = newMaxUtility

            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workers_index.remove(wIndex)
                tasks_importance_value,list_of_importance ,covered_point= f.tasks_importance_value_modification(tasks_importance_value,list_of_importance,workers[wIndex],tasks[t],covered_point,myMt,tasks)
                #c_worker_point[wIndex] = [0 for p in set_PoI]
                #list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]

            rewards = f.rest_rewards(task, list_of_workers, current_rewards, rewards)

            i += 1
    plop = 0
    return myMt, myMw, rewards

def AlgoWFIVp(workers, tasks, myRwd, set_PoI):
    global myMt, myMw
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    c_worker_point = f.get_c_worker_point(set_PoI)
    workers_index = [i[0] for i in workers]
    workerAdded = True
    while len(workers_index) > 0 and workerAdded:
        list_of_importance = f.get_list_of_point_by_importance(c_worker_point)
        tasks_index,tasks_importance_value = f.get_task_index_sorted_by_importance_prim(list_of_importance,tasks,myMt)
        i = 0
        workerAdded = False
        while i < len(tasks) and workerAdded == False:
            t = tasks_index[i]
            L = [w for w in workers_index if rewards[w][t] != 0]
            task = tasks[t]
            wIndex = -1
            maxUtility = f.Ut(tasks[t], myMt[t])

            list_of_workers = [w for w in workers if w[0] in L]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)

            for w in L:
                setOfWorker = myMt[t] + [workers[w]]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    newMaxUtility = f.Ut(tasks[t], setOfWorker)
                    if maxUtility < newMaxUtility:
                        workerAdded = True
                        wIndex = w
                        maxUtility = newMaxUtility

            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workers_index.remove(wIndex)
                c_worker_point[wIndex] = [0 for p in set_PoI]
                list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]

            rewards = f.rest_rewards(task, list_of_workers, current_rewards, rewards)

            i += 1
    plop = 0
    return myMt, myMw, rewards

def AlgoWFIVppp(workers, tasks, myRwd, set_PoI):
    global myMt, myMw
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    c_worker_point = f.get_c_worker_point(set_PoI)
    workers_index = [i[0] for i in workers]
    workerAdded = True
    while len(workers_index) > 0 and workerAdded:
        list_of_importance = f.get_list_of_point_by_importance(c_worker_point)
        tasks_index = f.get_task_index_sorted_by_importance_prim(list_of_importance,tasks,myMt)
        i = 0
        workerAdded = False
        while i < len(tasks) and workerAdded == False:
            t = tasks_index[i]
            L = [w for w in workers_index if rewards[w][t] != 0]
            task = tasks[t]
            wIndex = -1

            list_of_workers = [w for w in workers if w[0] in L]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)

            maxUtility = f.Ut(tasks[t], myMt[t])
            #minImportance = f.compute_improtance_value_by_task(list_of_importance,task,myMt[t])
            for w in L:
                setOfWorker = myMt[t] + [workers[w]]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    #newMinImportance = f.compute_improtance_value_by_task(list_of_importance,task,setOfWorker)
                    #if minImportance > newMinImportance:
                    newMaxUtility = f.Ut(tasks[t], setOfWorker)
                    if maxUtility < newMaxUtility:
                        workerAdded = True
                        wIndex = w
                        #minImportance = newMinImportance
                        maxUtility = newMaxUtility

            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workers_index.remove(wIndex)
                c_worker_point[wIndex] = [0 for p in set_PoI]
                list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]

            rewards = f.rest_rewards(task, list_of_workers, current_rewards, rewards)

            i += 1
    plop = 0
    return myMt, myMw, rewards
    return 0

def AlgoRRp(workers, tasks, myRwd, set_PoI):
    global myMt, myMw
    myInitialize(workers, tasks)
    c_worker_point = f.get_c_worker_point(set_PoI)
    rewards = f.copy_reward(myRwd)
    workers_index = [i[0] for i in workers]
    tasks_index = [t[0] for t in tasks]
    list_of_indexs = [p[0] for p in set_PoI if sum([c_worker_point[w][p[0]] for w in workers_index]) >= 1]
    workerAdded = True
    list_of_importance = [1]
    while len(list_of_importance) != 0:
        workerAdded = False
        list_of_importance = f.get_list_of_point_by_importance(c_worker_point)
        list_of_importance = [list_of_importance[i] for i in list_of_indexs]
        list_of_points_index = [x for _, x in sorted(zip(list_of_importance, list_of_indexs)) if _!=0]
        list_of_importance = [x for x in list_of_importance if x != 0 ]
        list_of_importance.sort()
        if len(list_of_importance) == 0:
            break
        p = list_of_points_index[0]
        workers_list = [w for w in workers_index if c_worker_point[w][p] == 1]
        tasks_list = [t for t in tasks_index if set_PoI[p] in [point[0] for point in tasks[t][1]]]

        # applying the approximated one-to-one matching between 2 sets
        '''
        weight_point = [f.getWeightPoint(tasks[t],p) for t in tasks_listp]
        tasks_list = [x for _, x in sorted(zip(weight_point, tasks_listp),reverse = True)]
        weight_point.sort(reverse=True)
        for t in tasks_list:
            maxUtility = f.Ut(tasks[t], myMt[t])
            i = 0
            wIndex = -1
            for w in workers_list:
                setOfWorker = myMt[t] + [workers[w]]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    newMaxUtility = f.Ut(tasks[t], setOfWorker)
                    if maxUtility < newMaxUtility:
                        workerAdded = True
                        wIndex = w
                        maxUtility = newMaxUtility
            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workers_index.remove(wIndex)
                workers_list.remove(wIndex)
                c_worker_point[wIndex] = [0 for __ in set_PoI]
        '''
        # applying the brut one-to-one matching between 2 sets

        combination = f.one_to_one_matching(tasks_list,workers_list,tasks,workers,rewards,myMt)

        for c in combination:
            w = c[1]
            t = c[0]
            myMw[w] = tasks[t]
            myMt[t].append(workers[w])
            workers_index.remove(w)
            workers_list.remove(w)
            c_worker_point[w] = [0 for __ in set_PoI]

        for w in workers_list:
            c_worker_point[w][p] = 0

    return myMt, myMw, rewards

def AlgoPS(workers, tasks, myRwd, pois,scheme,___,____):
    start_time = f.process_time()
    global myMt, myMw
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    all_list_of_workers = []
    all_pairs=[]
    for task in tasks:
        t = task[0]
        list_of_workers = []
        for worker in workers:
            w = worker[0]
            if f.Ut(task,[worker]) != 0:
                list_of_workers.append(worker)
                all_pairs.append([t,w])
        all_list_of_workers.append(list_of_workers)

    found = True
    while found:
        found = False
        removed_pairs = []
        best_pair = []
        max_benefit = 0

        current_rewards = f.copy_reward(rewards)

        for task in tasks:
            t = task[0]
            rewards = f.reward_modification(task, myMt[t], all_list_of_workers[t], current_rewards, rewards, workers)

        for pair in all_pairs:
            t = pair[0]
            w = pair[1]
            if f.Rt(tasks[t],[workers[w]]+myMt[t],rewards) <= tasks[t][2]:
                benefit = f.Ut(tasks[t], [workers[w]]+myMt[t]) - f.Ut(tasks[t],myMt[t])
                if max_benefit < benefit :
                    best_pair = pair
                    max_benefit = benefit
            else:
                removed_pairs.append(pair)

        if len(best_pair) > 0:
            found = True
            t = best_pair[0]
            w = best_pair[1]
            myMt[t].append(workers[w])
            myMw[w] = tasks[t]
            all_list_of_workers[t] = [worker for worker in workers if worker in all_list_of_workers[t] and worker[0] != w]
            for ta in [__[0] for __ in tasks]:
                if [ta,w] in all_pairs and [ta,w] not in removed_pairs:
                    removed_pairs.append([ta,w])
        for task in tasks:
            t = task[0]
            rewards = f.rest_rewards(task, all_list_of_workers[t], current_rewards, rewards)
        for pair in removed_pairs:
            all_pairs.remove(pair)
    timex = f.process_time() - start_time
    return myMt, myMw, timex

def AlgowcPS(workers, tasks, myRwd):
    global myMt, myMw
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    all_list_of_workers = []
    all_pairs=[]
    for task in tasks:
        t = task[0]
        list_of_workers = []
        for worker in workers:
            w = worker[0]
            if f.Ut(task,[worker]) != 0:
                list_of_workers.append(worker)
                all_pairs.append([t,w])
        all_list_of_workers.append(list_of_workers)

    found = True
    neglect_pairs = []
    while found:
        found = False
        removed_pairs = []
        best_pair = []
        max_benefit = 0
        current_rewards = f.copy_reward(rewards)

        for task in tasks:
            t = task[0]
            rewards = f.reward_modification(task, myMt[t], all_list_of_workers[t], current_rewards, rewards, workers)

        for pair in all_pairs:
            t = pair[0]
            w = pair[1]
            if pair not in neglect_pairs:
                if f.Rt(tasks[t],[workers[w]]+myMt[t],rewards) <= tasks[t][2]:
                    benefit = f.Ut(tasks[t], [workers[w]]+myMt[t]) - f.Ut(tasks[t],myMt[t])
                    if max_benefit < benefit :
                        best_pair = pair
                        max_benefit = benefit
                else:
                    removed_pairs.append(pair)

        if len(best_pair) > 0:
            found = True
            t = best_pair[0]
            w = best_pair[1]
            myMt[t].append(workers[w])
            myMw[w] = tasks[t]
            all_list_of_workers[t] = [worker for worker in workers if worker in all_list_of_workers[t] and worker[0] != w]
            for ta in [__[0] for __ in tasks]:
                if [ta,w] in all_pairs and [ta,w] not in removed_pairs:
                    neglect_pairs.append([ta,w])
        for task in tasks:
            t = task[0]
            rewards = f.rest_rewards(task, all_list_of_workers[t], current_rewards, rewards)
        for pair in removed_pairs:
            all_pairs.remove(pair)

    return myMt, myMw, rewards

def AlgoPrS(workers, tasks, myRwd):
    global myMt, myMw
    Mti = [[] for _ in range(len(tasks))]
    Mwi = [[] for _ in range(len(workers))]
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)

    all_pairs=[]
    for task in tasks:
        t = task[0]
        for worker in workers:
            w = worker[0]
            if f.Ut(task, [worker]) != 0:
                all_pairs.append([t,w])
                Mti[t].append(w)
                Mwi[w].append(t)
    worker_index = [i[0] for i in workers]
    worker_index.sort(key=lambda worker: len(Mwi[worker]))
    for w in worker_index:
        if len(Mwi[w])>1:
            max_utility = 0

            initial_utility = sum([f.Ut(task,[worker for worker in workers if worker[0] in Mti[task[0]]]) for task in tasks])
            best_task = -1
            for t in Mwi[w]:
                set_of_workers = [worker for worker in workers if worker[0] in Mti[t]]
                utility = sum([f.Ut(task,[worker for worker in workers if (worker[0] in Mti[task[0]] and w != worker[0])]) for task in tasks if task[0] != t]) + f.Ut(tasks[t],set_of_workers)
                #utility = f.Ut(tasks[t], set_of_workers) + sum([initial_utilities[task[0]] for task in tasks if task[0] != t])
                if utility > max_utility:
                    max_utility = utility
                    best_task = t
            if max_utility == initial_utility:
                for worker_list in Mti:
                    if w in worker_list:
                        worker_list.remove(w)
                Mwi[w] = []
            elif best_task != -1 :
                for worker_list in Mti:
                    if w in worker_list:
                        worker_list.remove(w)
                Mti[best_task].append(w)
                Mwi[w] = [best_task]
    for task in tasks:
        t = task[0]
        S, new_rewards = MCLB(workers, Mti[t], task, rewards)
        rewards = f.copy_reward(new_rewards)
        myMt[t] = S.copy()
        for w in S: myMw[w[0]] = task


    return myMt, myMw, rewards

def AlgoRRsecond(workers, tasks, myRwd):
    global myMt, myMw
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    current_rewards = f.copy_reward(myRwd)
    tasksIndex = random.sample([i for i in range(len(tasks))], len(tasks))
    # tasksIndex = [i for i in range(len(tasks))]
    workersIndex = [i for i in range(len(workers))]

    workerAdded = True
    while len(workersIndex) > 0 and workerAdded:
        tasksIndex = random.sample([i for i in range(len(tasks))], len(tasks))
        i = 0
        workerAdded = False
        while i < len(tasks) and len(workersIndex) > 0:
            t = tasksIndex[i]
            L = [w for w in workersIndex if rewards[w][t] != 0]
            task = tasks[t]
            list_of_workers = [w for w in workers if w[0] in L]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)
            # print(L)
            # L.sort(key= lambda w: rewards[w][t])
            wIndex = -1
            maxUtility = f.Ut(tasks[t], myMt[t])
            many_workers = []
            for w in L:
                setOfWorker = myMt[t] + [workers[w]]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    newMaxUtility = f.Ut(tasks[t], setOfWorker)
                    if maxUtility < newMaxUtility:
                        workerAdded = True
                        wIndex = w
                        many_workers = [w]
                        maxUtility = newMaxUtility

                    elif maxUtility == newMaxUtility:
                        many_workers.append(w)
                if len(many_workers) > 1:
                    #Lw = f.workerInterest(tasks,rewards)
                    list_utility = f.workers_current_system_utility(tasks,workers,myMt)
                    size = 0
                    for worker in many_workers:
                        newsize = (list_utility[worker])
                        if newsize > size:
                            size = newsize
                            wIndex = worker

            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workersIndex.remove(wIndex)
                list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]
            rewards = f.rest_rewards(task,list_of_workers,current_rewards,rewards)
            i += 1

        # print("len = ", len(workersIndex))
        # print(i)

    return myMt, myMw, rewards

# improvement
def AlgoRRi(workers, tasks, myRwd):
    global myMt, myMw
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    current_rewards = f.copy_reward(myRwd)
    tasksIndex = random.sample([i for i in range(len(tasks))], len(tasks))
    workersIndex = [i for i in range(len(workers))]

    workerAdded = True
    while len(workersIndex) > 0 and workerAdded:
        i = 0
        workerAdded = False
        desbledWokerPerTask = [[] for __ in tasks]
        while i < len(tasks) and len(workersIndex) > 0:
            canBeAdded = True
            t = tasksIndex[i]
            L = [w for w in workersIndex if rewards[w][t] != 0 and w not in desbledWokerPerTask[t]]
            task = tasks[t]
            list_of_workers = [w for w in workers if w[0] in L]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)
            # print(L)
            # L.sort(key= lambda w: rewards[w][t])
            wIndex = -1
            maxUtility = f.Ut(tasks[t], myMt[t])
            for w in L:
                setOfWorker = myMt[t] + [workers[w]]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    newMaxUtility = f.Ut(tasks[t], setOfWorker)
                    if maxUtility < newMaxUtility:
                        wIndex = w
                        maxUtility = newMaxUtility
            w = wIndex

            if wIndex != -1:
                tasksList = f.tasksListByPreferences(w, t, rewards)
                if len(tasksList) > 0:
                    for my_task in tasksList:
                        if f.bestWorker(my_task, w, tasks, workers, myMt, rewards):
                            i -= 1
                            desbledWokerPerTask[t].append(w)
                            canBeAdded = False
                            rewards = f.rest_rewards(task,list_of_workers,current_rewards,rewards)
                            break
                if canBeAdded:
                    workerAdded = True
                    myMw[wIndex] = tasks[t]
                    myMt[t].append(workers[wIndex])
                    workersIndex.remove(wIndex)

                    list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]
                    rewards = f.rest_rewards(task,list_of_workers,current_rewards,rewards)

            i += 1

        # print("len = ", len(workersIndex))
        # print(i)

    return myMt, myMw, rewards

# contribution
def AlgoRRc(workers, tasks, myRwd):
    global myMt, myMw
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    current_rewards = f.copy_reward(myRwd)
    tasksIndex = random.sample([i for i in range(len(tasks))],len(tasks))
    #tasksIndex = [i for i in range(len(tasks))]
    # tasksIndex = sorted([i for i in range(len(tasks))],key= lambda i : len(tasks[i][1]))

    WightedProb = [1 - len(tasks[i][1]) / sum([len(tasks[t][1]) for t in range(len(tasks))]) for i in range(len(tasks))]

    WightedP = [x / sum(WightedProb) for x in WightedProb]
    workersIndex = [i for i in range(len(workers))]

    workerAdded = True
    while len(workersIndex) > 0 and workerAdded:
        i = 0
        workerAdded = False
        while i < len(tasks) and len(workersIndex) > 0:
            t = tasksIndex[i]
            t = choice(tasksIndex, 1, p=WightedP)[0]
            L = [w for w in workersIndex if rewards[w][t] != 0]
            task = tasks[t]
            list_of_workers = [w for w in workers if w[0] in L]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)
            # print(L)
            # L.sort(key= lambda w: rewards[w][t])
            wIndex = -1
            maxEfficiency = 0
            utility = f.Ut(tasks[t], myMt[t])
            for w in L:

                setOfWorker = myMt[t] + [workers[w]]
                newUtility = f.Ut(tasks[t], setOfWorker)
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2] and utility < newUtility:
                    newMaxEfficiency = (newUtility - utility) / f.Ut(tasks[t], [workers[w]])
                    # newMaxEfficiency = newUtility
                    if maxEfficiency < newMaxEfficiency:
                        workerAdded = True
                        wIndex = w
                        maxEfficiency = newMaxEfficiency

            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workersIndex.remove(wIndex)
                list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]
            rewards = f.rest_rewards(task,list_of_workers,current_rewards,rewards)
            i += 1

        # print("len = ", len(workersIndex))
        # print(i)

    return myMt, myMw, rewards

# efficiency
def AlgoRRe(workers, tasks, myRwd):
    global myMt, myMw
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    current_rewards = f.copy_reward(myRwd)
    tasksIndex = random.sample([i for i in range(len(tasks))], len(tasks))
    tasksIndex = [i for i in range(len(tasks))]
    # tasksIndex = sorted([i for i in range(len(tasks))],key= lambda i : len(tasks[i][1]))
    workersIndex = [i for i in range(len(workers))]

    workerAdded = True
    while len(workersIndex) > 0 and workerAdded:
        i = 0
        workerAdded = False
        while i < len(tasks) and len(workersIndex) > 0:
            t = tasksIndex[i]
            L = [w for w in workersIndex if rewards[w][t] != 0]
            task = tasks[t]
            list_of_workers = [w for w in workers if w[0] in L]
            current_rewards = f.copy_reward(myRwd)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)
            # print(L)
            # L.sort(key= lambda w: rewards[w][t])
            wIndex = -1
            maxEfficiency = 0
            utility = f.Ut(tasks[t], myMt[t])
            for w in L:
                setOfWorker = myMt[t] + [workers[w]]
                newUtility = f.Ut(tasks[t], setOfWorker)
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2] and utility < newUtility:
                    newMaxEfficiency = (newUtility - utility) / rewards[w][t]
                    #newMaxEfficiency = ((newUtility - utility)**2) / f.Ut(tasks[t], [workers[w]])
                    if maxEfficiency < newMaxEfficiency:
                        workerAdded = True
                        wIndex = w
                        maxEfficiency = newMaxEfficiency

            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workersIndex.remove(wIndex)
                list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]
            rewards = f.rest_rewards(task,list_of_workers,current_rewards,rewards)
            i += 1

        # print("len = ", len(workersIndex))
        # print(i)

    return myMt, myMw, rewards

# reverse selection
def AlgoRRr(workers, tasks, myRwd):
    global myMt, myMw
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    current_rewards = f.copy_reward(myRwd)
    tasksIndex = random.sample([i for i in range(len(tasks))], len(tasks))
    # tasksIndex = [i for i in range(len(tasks))]
    workersIndex = [i for i in range(len(workers))]

    workerAdded = True
    while len(workersIndex) > 0 and workerAdded:
        i = 0
        workerAdded = False
        while i < len(tasks) and len(workersIndex) > 0:
            t = tasksIndex[i]
            L = [w for w in workersIndex if rewards[w][t] != 0]
            task = tasks[t]
            list_of_workers = [w for w in workers if w[0] in L]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)
            # print(L)
            # L.sort(key= lambda w: rewards[w][t])
            wIndex = -1
            #maxUtility = f.Ut(tasks[t], myMt[t])
            initialUtility = f.Ut(tasks[t],myMt[t])
            minUtility = 1
            for w in L:
                setOfWorker = myMt[t] + [workers[w]]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    newMinUtility = f.Ut(tasks[t], setOfWorker)
                    if minUtility > newMinUtility and initialUtility != newMinUtility:
                        workerAdded = True
                        wIndex = w
                        minUtility = newMinUtility

            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workersIndex.remove(wIndex)
                list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]
            rewards = f.rest_rewards(task,list_of_workers,current_rewards,rewards)
            i += 1

        # print("len = ", len(workersIndex))
        # print(i)

    return myMt, myMw, rewards

# tasks selection
def AlgoRRw(workers, tasks, myRwd):
    global myMt, myMw
    myInitialize(workers, tasks)
    rewards = f.copy_reward(myRwd)
    current_rewards = f.copy_reward(myRwd)
    #tasksIndex = random.sample([i for i in range(len(tasks))], len(tasks))
    L = f.workerInterest(tasks,rewards)
    my_workers = f.sorting(workers,L)
    # tasksIndex = [i for i in range(len(tasks))]
    #workersIndex = [i for i in range(len(workers))]
    for worker in my_workers:
        w = worker[0]
        reward_constraint_failed = True
        i = -1
        while reward_constraint_failed:
            i+= 1
            if len(L[w]) == 0:
                reward_constraint_failed = False
            elif len(L[w]) > i:
                t = L[w][i][0]
                setOfWorker = myMt[t] + [worker]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    reward_constraint_failed = False
                    myMw[w] = tasks[t]
                    myMt[t].append(worker)
            else:
                reward_constraint_failed = False

    '''
    workerAdded = True
    while len(workersIndex) > 0 and workerAdded:
        i = 0
        workerAdded = False
        while i < len(tasks) and len(workersIndex) > 0:
            t = tasksIndex[i]
            L = [w for w in workersIndex if rewards[w][t] != 0]
            task = tasks[t]
            list_of_workers = [w for w in workers if w[0] in L]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task,myMt[t],list_of_workers,current_rewards,rewards,workers)
            # print(L)
            # L.sort(key= lambda w: rewards[w][t])
            wIndex = -1
            #maxUtility = f.Ut(tasks[t], myMt[t])
            minUtility = 1
            for w in L:
                setOfWorker = myMt[t] + [workers[w]]
                if f.Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
                    newMinUtility = f.Ut(tasks[t], setOfWorker)
                    if minUtility > newMinUtility:
                        workerAdded = True
                        wIndex = w
                        minUtility = newMinUtility

            if wIndex != -1:
                myMw[wIndex] = tasks[t]
                myMt[t].append(workers[wIndex])
                workersIndex.remove(wIndex)
                list_of_workers = [w for w in workers if w[0] in L and w[0] != wIndex]
            rewards = f.rest_rewards(task,list_of_workers,current_rewards,rewards)
            i += 1

        # print("len = ", len(workersIndex))
        # print(i)
    '''
    return myMt, myMw, rewards

# //////////////////////////////-----------------------------------------\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# ----------------------------------Maximum Coverage Quality Assignment--------------------------------
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\-----------------------------------------//////////////////////////////

def ApproximationAlgorithm(workers, workersList, task, myRwd):
    budget = task[2]    # allSubset = [x for x in StableMatching.subsets(workersList) if (len(x) < k and len(x) != 0 and StableMatching.rewardsByWorkers(task,x,rewards) <= budget) ]
    allSubset = [x for x in f.subsetsTwo(workersList) if
                 f.rewardsByWorkers(task, x, myRwd) <= budget]
    current_rewards = f.copy_reward(myRwd)
    rewards = f.copy_reward(myRwd)
    final_rewards = f.copy_reward(myRwd)
    # print("hi ",len(allSubset))
    Hp1 = max(allSubset, key=(lambda y: f.Ut(task, [x for x in workers if x[0] in y])))
    H1 = [x for x in workers if x[0] in Hp1]
    H2 = []
    # allSubset = [x for x in StableMatching.subsets(workersList) if (len(x) == k and StableMatching.rewardsByWorkers(task,x,rewards) <= budget)]
    allSubset = [x for x in f.subsetsThree(workersList) if
                 f.rewardsByWorkers(task, x, myRwd) <= budget]

    current_rewards = f.copy_reward(myRwd)
    for Gp in allSubset:
        G = [x for x in workers if x[0] in Gp]
        listM = [x for x in workers if (x[0] not in Gp and x[0] in workersList)]

        # I add this beause  i will change all rewards for each worker for the task for each iteration
        #rewards = f.copy_reward(myRwd)
        t = task[0]
        while len(listM) > 0:

            list_of_workers = [w for w in workers if w[0] in listM]
            current_rewards = f.copy_reward(rewards)
            rewards = f.reward_modification(task, G, list_of_workers, current_rewards, rewards, workers)

            indexI = 0
            while indexI < (len(listM)):
                y = listM[indexI]
                if rewards[y[0]][task[0]]==0:
                    listM.pop(indexI)
                    indexI = indexI -1
                indexI = indexI+1
            #print(M)
            if len(listM) == 0:
                continue
            v = max(listM, key=lambda y: (
                        (f.Ut(task, [y] + G) - f.Ut(task, G)) / rewards[y[0]][task[0]]))
            rwd = f.rewardsByWorkers(task, [v[0]] + Gp, rewards)
            if (f.Ut(task, [v] + G) - f.Ut(task, G)) == 0:
                break
            if rwd <= budget:
                Gp.append(v[0])
                G.append(v)
                list_of_workers = [w for w in workers if w[0] in listM and w[0] != v[0]]
                rewards = f.rest_rewards(task,list_of_workers,current_rewards,rewards)
            listM.remove(v)
        if f.Ut(task, G) > f.Ut(task, H2):
            final_rewards = f.copy_reward(rewards)
            H2 = G.copy()
    if f.Ut(task, H1) > f.Ut(task, H2):
        #print("len H1 = ",len(H1)," utility = ", f.Ut(task, H1))
        #print("len H2 = ",len(H2)," utility = ", f.Ut(task, H2))
        #print("yes")
        return H1, rewards
    return H2, rewards

def AlgoMC(workers, tasks, myRwd,scheme):
    global myMw, myMt
    rewards = f.copy_reward(myRwd)
    myInitialize(workers, tasks)
    L = f.setOfHappyWorkerPerTask(tasks, workers, rewards)
    # print("list on MCQA = ",L)
    for task in tasks:
        t = task[0]
        # print("len(L)= " , len(L[t]))
        # it can be that the task give bad rewards to all worker comparing to other tasks
        if len(L[t]) != 0:
            S, rewards = ApproximationAlgorithm(workers, L[t], task, rewards)
            myMt[t] = S.copy()
            for w in S: myMw[w[0]] = task
    #    return myMt, myMw
    myMt, myMw,rewards = f.addMoreWorkerToTasks(tasks, workers, rewards, myMw, myMt)

    #f.manyToOne(myMt, "underfunction")
    #f.budegetTest(myMt, tasks, rewards, "underfunction")
    return myMt, myMw, rewards

# //////////////////////////////-----------------------------------------\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# ----------------------------------Maximum Coverage Quality Assignment--------------------------------
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\-----------------------------------------//////////////////////////////

def MCLB(workers, list_workers, task, myRwd):
    S = []
    R = 0
    # I add this beause  i will change all rewards for each worker for the task for each iteration
    rewards = f.copy_reward(myRwd)
    workersList = list_workers.copy()
    t = task[0]
    while len(workersList) > 0:

        list_of_workers = [w for w in workers if w[0] in workersList]
        #
        # current_rewards = f.copy_reward(rewards)
        # rewards = f.reward_modification(task,S,list_of_workers,current_rewards,rewards,workers)

        indexI = 0
        while indexI < (len(workersList)):
            y = workersList[indexI]
            if rewards[y][task[0]] == 0:
                workersList.pop(indexI)
                indexI = indexI - 1
            indexI = indexI + 1
        # print(M)
        if len(workersList) == 0:
            continue
        w = max(workersList, key=(
            lambda x: (f.Ut(task, S + [workers[x]]) - f.Ut(task, S)) / rewards[x][task[0]]))
        if f.Ut(task, S + [workers[w]]) - f.Ut(task, S) == 0:
            break
        # if task[2] >= R + rewards[w][task[0]]:
        if task[2] >= f.Rt(task, S + [workers[w]], rewards):
            S.append(workers[w])
            R += rewards[w][task[0]]

            list_of_workers = [wor for wor in workers if wor[0] in workersList and wor[0] != w]
        # rewards = f.rest_rewards(task,list_of_workers,current_rewards,rewards)
        workersList.remove(w)
    return S, rewards

def MCLButility(workers, list_workers, task, myRwd):
    S = []
    R = 0
    # I add this beause  i will change all rewards for each worker for the task for each iteration
    rewards = f.copy_reward(myRwd)
    workersList = list_workers.copy()
    t = task[0]
    while len(workersList) > 0:

        list_of_workers = [w for w in workers if w[0] in workersList]
        #
        # current_rewards = f.copy_reward(rewards)
        # rewards = f.reward_modification(task,S,list_of_workers,current_rewards,rewards,workers)

        indexI = 0
        while indexI < (len(workersList)):
            y = workersList[indexI]
            if rewards[y][task[0]] == 0:
                workersList.pop(indexI)
                indexI = indexI - 1
            indexI = indexI + 1
        # print(M)
        if len(workersList) == 0:
            continue
        w = max(workersList, key=(
            lambda x: (f.Ut(task, S + [workers[x]]) - f.Ut(task, S))))
        if f.Ut(task, S + [workers[w]]) - f.Ut(task, S) == 0:
            break
        # if task[2] >= R + rewards[w][task[0]]:
        if task[2] >= f.Rt(task, S + [workers[w]], rewards):
            S.append(workers[w])
            R += rewards[w][task[0]]

            list_of_workers = [wor for wor in workers if wor[0] in workersList and wor[0] != w]
        # rewards = f.rest_rewards(task,list_of_workers,current_rewards,rewards)
        workersList.remove(w)
    return S, rewards

def Greedy(workers, tasks, myRwd,poi,scheme,___,____):
    start_time = f.process_time()
    global myMw, myMt
    rewards = f.copy_reward(myRwd)
    myInitialize(workers, tasks)
    L = f.setOfHappyWorkerPerTask(tasks, workers, rewards)
    # print("list on Greedy = ",L)
    for task in tasks:
        t = task[0]
        # print("len(L)= " , len(L[t]))
        # it can be that the task give bad rewards to all worker comparing to other tasks
        if len(L[t]) != 0:
            S, new_rewards = MCLB(workers, L[t], task, rewards)
            rewards = f.copy_reward(new_rewards)
            myMt[t] = S.copy()
            for w in S: myMw[w[0]] = task
    #    return myMt, myMw
    myMt, myMw ,rewards= f.addMoreWorkerToTasks(tasks, workers, rewards, myMw, myMt)
    time = (f.process_time() - start_time)  # ((time.time() - start_time) / nbrOfSimulations)

    #f.manyToOne(myMt, "underfunction")
    #f.budegetTest(myMt, tasks, rewards, "underfunction")
    return myMt, myMw, time

def AlgoGreedy(workers, tasks, myRwd,poi,scheme,___,____):
    global myMw, myMt
    rewards = f.copy_reward(myRwd)
    myInitialize(workers, tasks)
    list_worker = [w[0] for w in workers]
    list_of_tasks = [t[0] for t in tasks]
    worker_added = True
    task = 1
    while len(list_worker) > 0 and len(list_of_tasks) > 0 and task != -1:
        #worker_added = False
        maximum_utility = 0
        S = []
        task = -1
        for t in list_of_tasks:
            current_task = tasks[t]
            new_S, new_rewards = MCLB(workers, list_worker, current_task, rewards)
            # rewards = f.copy_reward(new_rewards)
            utility = f.Ut(current_task,new_S)
            if utility > maximum_utility:
                S = new_S.copy()
                task = current_task
        if len(S) > 0:
            myMt[t] = S.copy()
            for w in S: myMw[w[0]] = task
            list_of_tasks.remove(task[0])
            for worker in S:
                list_worker.remove(worker[0])

    return myMt, myMw, rewards






