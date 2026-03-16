import itertools
import os
import time
# import test_rl as RL
import matplotlib.pyplot as plt
import secrets
import random
import numpy as np
import math
import scipy.stats
from datetime import datetime
from time import process_time


cWorkerTask = []
cWorkerTaskp = []
#rewards = []


# //////////////////////////////-----------------------------------------\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# ----------------------------------------Problem Statement--------------------------------------------
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\-----------------------------------------//////////////////////////////

def extended_coverage_metric(Mt,tasks,all_PoIs,metric_value):

    extended_total_coverage = 0
    verify_metric = 0
    for t in range(len(Mt)):
        points_list = [0] * len(all_PoIs)
        for worker in Mt[t]:
                w = worker[0]
                for point in cWorkerTask[w][t]:
                    p = point[0][0]
                    points_list[p]+= 1
        for PoI in tasks[t][1]:
            extended_total_coverage += PoI[1] * max(points_list[PoI[0][0]],1)
            verify_metric += PoI[1] * points_list[PoI[0][0]]
    
    if verify_metric != metric_value:
        print("error, on the computed extended value: ",verify_metric," and the original value; ",metric_value )
    # return (verify_metric/extended_total_coverage) * (100/len(Mt))
    return (verify_metric) * (100/len(Mt))

def manyToOnetest(Mt,algo):
    testWorkers = []
    for setOfw in Mt:
        for element in setOfw:
            testWorkers.append(element[0])
    if len(testWorkers) ==0 :
        print("No matching in algo ",algo)
    elif testWorkers.count(max(testWorkers, key=testWorkers.count)) > 1:
        print("One worker in ",algo , " is matched with more than one task: ", testWorkers.count(max(testWorkers, key=testWorkers.count)))

def budegetTest(Mt,tasks,rewards,algo):
    for t in range(len(tasks)):
        task = tasks[t]
        budget = task[2]
        if budget < Rt(task,Mt[t],rewards):
            print("In ", algo, "the budget is exeeded for the task ", str(t) , " by :" , str( Rt(task,Mt[t],rewards) -budget))

def human_readable_format(num):
    for unit in ['','k','m','b','t']:
        if abs(num) < 1000.0:
            return "%3.1f%s" % (num, unit)
        num /= 1000.0
    return "%.1f%s" % (num, 'p')  # 'p' for quadrillion, as an example

# def make_custom_env(n, m, tasks, workers, Utility, Reward, budget_reward, episode_steps):
#     def _init():
#         return RL.CustomEnv(n, m, tasks, workers, Utility, Reward, budget_reward, episode_steps)
#     return _init

# def run_simulation(algorithms,algorithms_names, workers, tasks, PoIs, rewards, metrics, number_of_simulation,upper_bounded):
def run_simulation(algorithms,algorithms_names, workers, tasks, PoIs, rewards ,upper_bounded):
    coverage_results = []
    budget_results = []
    time_results = []
    for i in range(len(algorithms)):
        # if i==1:
            # print("I am ",rank,"and I started the RL")
        coverage, budget, time = run(algorithms[i], i, algorithms_names, workers, tasks, PoIs, rewards, upper_bounded)
        # coverage, budget, time = run(algorithms[i], i, algorithms_names, workers, tasks, PoIs, rewards, metrics, number_of_simulation)

        # if i==1:
            # print("I am ",rank,"and I finished the RL")

        coverage_results.append(coverage)
        budget_results.append(budget)
        time_results.append(time)

    return [coverage_results,budget_results,time_results]

def run(algorithm, index, algorithms_names, workers, tasks, PoIs, rewards,upper_bounded):
    scheme = 0
    if "CSTAp" == algorithms_names[index]:
        scheme = 1

    c_worker_point,c_task_point = get_c_worker_point(PoIs)
    list_of_importance,cpw = get_list_of_point_by_importance(c_worker_point)

    start_time = process_time()  # start_time = time.time()

    Mt, Mw, timex = algorithm(workers, tasks, rewards, PoIs,scheme,list_of_importance,cpw)

    time = (process_time() - start_time)  # ((time.time() - start_time) / nbrOfSimulations)
    manyToOnetest(Mt, algorithms_names[index])
    budegetTest(Mt, tasks, rewards, algorithms_names[index])
    # if upper_bounded and index == 0:
    #     coverage0 = extended_coverage_metric(Mt,tasks,PoIs,optimalresults)
    #     coverage1,_,_ = coverage_quality_parallel(tasks,Mt)
    #     coverage = (coverage0/(100 + coverage0 - coverage1))*100
        # coverage = extended_coverage_metric(Mt,tasks,PoIs,optimalresults)
        # coverage, _, _ = coverage_quality_parallel(tasks, Mt)
    if upper_bounded and index == 1:
        # coverage0 = extended_coverage_metric(Mt,tasks,PoIs,optimalresults)
        # coverage1,_,_ = coverage_quality_parallel(tasks,Mt)
        # coverage = coverage0/(1+coverage0 - coverage1)
        coverage = extended_coverage_metric(Mt,tasks,PoIs,optimalresults)
        # coverage, _, _ = coverage_quality_parallel(tasks, Mt)
    # elif upper_bounded and index == 2:
    #     # coverage0 = extended_coverage_metric(Mt,tasks,PoIs,optimalresults)
    #     # coverage1,_,_ = coverage_quality_parallel(tasks,Mt)
    #     # coverage = coverage0/(1+coverage0 - coverage1)
    #     # coverage = extended_coverage_metric(Mt,tasks,PoIs,optimalresults)
    #     coverage, _, _ = coverage_quality_parallel(tasks, Mt)
    else:
        coverage,_,_ = coverage_quality_parallel(tasks,Mt)
    budget = UsedBudget(tasks,Mt,rewards)
    return coverage, budget, timex

def readPoIandCworkers(folder):
    my_file = open(os.path.join(folder, "PoI.txt"), "r")
    PoIContent = my_file.readlines()
    PoI = []
    for i in range(len(PoIContent)):
        point = PoIContent[i].split(" ")
        PoI.append([float(point[0]),float(point[1])])
    #print(PoI)
    my_file = open(os.path.join(folder , "Cworkers.txt"), "r")
    CworkerContent = my_file.readlines()
    Cworker = [[] for i in range(len(CworkerContent))]
    i = 0
    for line in CworkerContent:
        points = line.split(" ")
        for element in points:
            point = element.split(",")
            if len(point) == 2:
                Cworker[i].append([float(point[0]),float(point[1])])
        i = i + 1
    return PoI, Cworker

def indexPoI(PoInoIndex):
    PoI = []
    for i in range(len(PoInoIndex)):
        PoI.append([i,PoInoIndex[i]])
    return PoI

def AddPoint(PoI,k):
    '''
    points = [p[1] for p in PoI]
    for i in range(len(PoI),k+len(PoI)):
        while True:
            x = random.sample(PoI,1)[0][1][0]
            y = random.sample(PoI,1)[0][1][1]
            #print([x,y] not in points)
            if [x,y] not in points:
                PoI.append([i,[x,y]])
                break
    return PoI
    '''

    points = [p[1] for p in PoI]
    for i in range(len(PoI), k + len(PoI)):
        while True:
            x = random.uniform(-15000,15000)
            y = random.uniform(-2500,15000)
            # print([x,y] not in points)
            if [x, y] not in points:
                PoI.append([i, [x, y]])
                break
    return PoI

def generatePoIandCwrokers(k,path,folder):

    workers = read_Data_Set(path)
    #PoI,Cworkers = GeneratePoI4(workers)
    # if k == 200:
    PoI = GeneratePoI4(workers,300)
    PoI = AddPoint(PoI,100)
    # else:
    #     PoI = GeneratePoI4(workers,3000)
    #     PoI = AddPoint(PoI,1000)
    Cworkers = ComputeCworkers(PoI,workers)

    textfile1 = open(folder+"PoI.txt", "w")
    for element1 in PoI:
        for element in element1[1]:
            textfile1.write(str(element) + " ")
        textfile1.write("\n")
    textfile1.close()
    textfile2 = open(folder+"Cworkers.txt", "w")
    for element1 in Cworkers:
        for element in element1:
            textfile2.write(str(element[0])+","+str(element[1]) + " ")
        textfile2.write("\n")
    textfile2.close()

def generate_testing_tasks(n, PoI):
    tasks = []

    for i in range(0,n):
        x = i+5
        s = abs((x % 1 + x % 3 + x % 8 - x % 10) + 3)
        budget = s*10
        task = []
        for j in range(s):
            index = (i+j+s +(s*i*j))%300
            p = PoI[index]
            w = 1
            task.append([p, w])
        totalweight = totalWeight([i, task, budget])
        task = [[t[0], t[1] / totalweight] for t in task]
        tasks.append([i, task, budget, totalWeight([i, task, budget])])
    return tasks

def generateTasks(n,PoI,generalProportional):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    tasks = []
    e = 5;a = 10;b = 100
    tasks_budgets = SEWAM(a,b,n,e)
    for i in range(0,n):
        #testPoI = []
        s = 1
        s = 0
        while s == 0:
            s = secrets.randbelow(10)
        '''
        #print("s = ",s)
        #budget = 0
        #if generalProportional == 0:
        #s = secrets.randbelow(12)
        # Select budget based on the number of point for the task using the normal distribution
        mean_budget = number_of_task_to_budget_mean(s,1,25,10,100)
        # using normal distribution
        #budget = np.random.normal(loc=0.0, scale=1.0, size=None)
        # using poisson distribution
        
        budget = np.random.poisson(lam = mean_budget,size=1)
        if budget > 100:
            budget = 100
        elif budget < 10:
            budget = 10
        else:
            budget = int(budget)
        '''
        #else:
        #budget = np.random.choice([i for i in  range(10,101)])

        budget = int(random.uniform(10, 100))
        budget = int(tasks_budgets[i])
        task = []
        list = [t for t in range(len(PoI))]
        for j in range(s):
            #list = [t for t in range(len(PoI))]
            index = np.random.choice(list)
            list.remove(index)
            p = PoI[index]
            #testPoI.append(p[1])
            w = 0
            while w == 0:
                w = random.uniform(0,1)
            #print("w = ", w)
            task.append([p,w])
        # we normelize the task's weight to 1 for each worker
        totalweight = totalWeight([i,task,budget])
        task = [[t[0],t[1]/totalweight] for t in task]
        #print("tasks generation = ", testPoI.count(max(testPoI, key=testPoI.count)))
        tasks.append([i,task,budget,totalWeight([i,task,budget])])

    return tasks

def selectRandomSampling(allWorkers,allCworkers, m):
    workers = random.sample(allWorkers, m)
    newWorkers = []
    newCworkers = []
    for i in range(len(workers)):
        newWorkers.append([i,workers[i][1]])
        newCworkers.append(allCworkers[workers[i][0]])

    return newWorkers, newCworkers

#        * ////////////----------------------------------------------------------------------\\\\\\\\\\\\ *
# --------------------------------------------------Metrics-------------------------------------------------
#        * \\\\\\\\\\\\----------------------------------------------------------------------//////////// *

def UsedBudgetp(resultPathUB, fileName, tasks, Mt, rewards):
    n = len(tasks)
    used_budget = 0
    for i in range(n):
        r = Rt(tasks[i],Mt[i],rewards)
        used_budget += r/tasks[i][2]
    used_budget = used_budget * (100/n)
    return used_budget


def UsedBudget(tasks, Mt, rewards):
    n = len(tasks)
    used_budget = 0
    for i in range(n):
        r = Rt(tasks[i],Mt[i],rewards)
        used_budget += r/tasks[i][2]
    used_budget = used_budget * (100/n)
    return used_budget


def coverage_quality_parallel(tasks, Mt):
    n = len(tasks)
    ratioCoverage = 0
    min = 1
    max = 0
    for i in range(n):
        if (Ut(tasks[i], Mt[i])) < min:
            min = (Ut(tasks[i], Mt[i]))
        elif (Ut(tasks[i], Mt[i])) > max:
            max = (Ut(tasks[i], Mt[i]))
        coverage = 0
        for point in tasks[i][1]:
            coverage = coverage + point[1]
        ratioCoverage = ratioCoverage + ((Ut(tasks[i], Mt[i])) / coverage)
    ratioCoverage = ratioCoverage * (100 / n)
    return ratioCoverage,min*100,max*100


def CoverageQuality(resultPathCQ, fileName, tasks, Mt):
    file = open(os.path.join(resultPathCQ, fileName), "a")
    n = len(tasks)
    ratioCoverage = 0
    min = 1
    max = 0
    for i in range(n):
        if (Ut(tasks[i], Mt[i])) < min:
            min = (Ut(tasks[i], Mt[i]))
        elif (Ut(tasks[i], Mt[i])) > max:
            max = (Ut(tasks[i], Mt[i]))
        coverage = 0
        for point in tasks[i][1]:
            coverage = coverage + point[1]
        ratioCoverage = ratioCoverage + ((Ut(tasks[i], Mt[i])) / coverage)
        if i == 0:
            file.write(str(i) + "," + str(Ut(tasks[i], Mt[i])) + "," + str(coverage))
        else:
            file.write(" " + str(i) + "," + str(Ut(tasks[i], Mt[i])) + "," + str(coverage))
    file.write("\n")
    file.close()
    ratioCoverage = ratioCoverage * (100 / n)
    return ratioCoverage,min*100,max*100

def AverageRewards(resultPathAR, fileName, Mw, rewards, tasks):
    file = open(os.path.join(resultPathAR, fileName), "a")
    m = len(Mw)
    x = 0
    ratioReward = 0
    for i in range(m):
        if Mw[i] != None:
            t = Mw[i][0]
            ratioReward = ratioReward + (rewards[i][Mw[i][0]]/tasks[t][2])
            x += 1
            if i == 0:
                file.write(str(i) + "," + str(rewards[i][Mw[i][0]]) + "," + str(tasks[t][2]))
            else:
                file.write(" " + str(i) + "," + str(rewards[i][Mw[i][0]]) + "," + str(tasks[t][2]))
    file.write("\n")
    file.close()
    ratioReward = (100* ratioReward) / x
    return ratioReward

def RewardsByMax(resultPathAR, fileName, Mw, rewards, maxReward):
    file = open(os.path.join(resultPathAR, fileName), "a")
    m = len(Mw)
    x = 0
    ratioReward = 0
    for i in range(m):
        if Mw[i] != None  and max(maxReward[i])!=0:
            ratioReward = ratioReward + rewards[i][Mw[i][0]] / max(maxReward[i])
            x += 1
            if i == 0:
                file.write(str(i) + "," + str(rewards[i][Mw[i][0]]) + "," + str(max(maxReward[i])))
            else:
                file.write(" " + str(i) + "," + str(rewards[i][Mw[i][0]]) + "," + str(max(maxReward[i])))
    file.write("\n")
    file.close()
    ratioReward = ratioReward * (100 / x)
    return ratioReward

def HappinessDegree(resultPathUS, fileName, Mw, rewards, maxReward):
    file = open(os.path.join(resultPathUS, fileName), "a")
    m = len(Mw)
    n = len(rewards[0])
    x = 0
    ratioSatisfaction = 0
    for i in range(m):
        if Mw[i] != None:
            t = Mw[i][0]
            w = i
            taskList = tasksListByPreferences(w, t, maxReward)
            ratioSatisfaction = ratioSatisfaction + (n - len(taskList)) / n
            x += 1
            if i == 0:
                file.write(str(i) + "," + str(n) + "," + str(n - len(taskList)))
            else:
                file.write(" " + str(i) + "," + str(n) + "," + str(n - len(taskList)))
    file.write("\n")
    file.close()
    ratioSatisfaction = ratioSatisfaction * (100 / x)
    return ratioSatisfaction

def NormalizedHappiness(resultPathUS, fileName, Mw, rewards, maxRewards):
    file = open(os.path.join(resultPathUS, fileName), "a")
    m = len(Mw)
    n = len(rewards[0])
    x = 0
    ratioSatisfaction = 0
    for i in range(m):
        if Mw[i] != None  and  max(maxRewards[i])!=0:
            t = Mw[i][0]
            w = i
            maxi = max(maxRewards[w])
            if [__ for __ in rewards[i] if __ != 0 ] == []:
                mini = 0
            else:
                mini = min([__ for __ in rewards[w] if __ != 0 ])
            if maxi == mini:
                ratioSatisfaction = ratioSatisfaction + 1
            else:
                ratioSatisfaction = ratioSatisfaction + normalize(maxi,mini,rewards[w][t])
            #ratioSatisfaction = ratioSatisfaction + (n-len(taskList))/n
            x += 1
            if i == 0:
                file.write(str(w) + "," + str(rewards[w][t]) + "," + str(maxi) + "," + str(mini))
            else:
                file.write(" " + str(w) + "," + str(rewards[w][t]) + "," + str(maxi) + "," + str(mini))
    file.write("\n")
    file.close()
    ratioSatisfaction = ratioSatisfaction * (100 / x)
    return ratioSatisfaction

def average_number_of_worker(resultPathAW,fileName,Mw,m):
    file = open(os.path.join(resultPathAW, fileName), "a")
    x = len([1 for __ in Mw if __ != None])
    file.write(str(x) + "," + str(m) + "\n")
    file.close()
    return x * (100/m)

def number_of_worker_per_task(resultPathWpT,fileName,Mt):
    file = open(os.path.join(resultPathWpT, fileName), "a")
    n = len(Mt)
    x = sum([len(__) for __ in Mt])
    #print([len(__) for __ in Mt])
    file.write(str(x) + "," + str(n) + "\n")
    file.close()
    return x / n

def ExtraPointCovered(tasks, Mt, PoI, rewards):
    n = len(tasks)
    extraRewards = [0 for __ in range(n)]
    nmbOfPoints = [[0 for __ in range(len(PoI))] for _ in tasks]
    extraWeight = [[0 for __ in range(len(PoI))] for _ in tasks]
    cwt = cWorkerTask.copy()
    # go over tasks
    for t in range(len(tasks)):
        task = tasks[t]
        # go over workers
        for worker in Mt[t]:
            w = worker[0]
            # go over the point that are covered by the worker for the task t
            for point in cwt[w][t]:
                p = point[0][0]
                # increment the number of point of the point p
                nmbOfPoints[t][p] += 1
                # if the point is covered more than 2 time we compute the reward the worker got for covering this point
                if nmbOfPoints[t][p] > 1:
                    # this is working for proportional and general setting
                    extraRewards[t] += (rewards[w][t]*(point[1]/Ut(task,[worker])))/task[2]
        # go over the point of the task
        xxxx = 2
        for point in task[1]:
            p = point[0][0]
            # if the point p is covered more than 1 time we reduce the count (if he is cover one time we do not count the extra value otherwise we consider only the information after getting covered more than 2 times)
            if nmbOfPoints[t][p] >= 1:
                nmbOfPoints[t][p] = nmbOfPoints[t][p] - 1
            # we compute the extra weight the system is getting without any utility
            extraWeight[t][p] = (point[1])*(nmbOfPoints[t][p])

    extRewards = sum(extraRewards)/n
    extWeight = sum([sum(extraWeight[t]) for t in range(n)])/n
    extPoint = sum([sum(nmbOfPoints[t]) for t in range(n)])/n
    return extPoint, extWeight, extRewards

def UserHappiness(resultPathUH, fileName, workers, tasks, Mt, Mw, rewards):
    nmbOfCoalition, nmbOfMatching = nmbOfCoalitionAndMatching(workers, tasks, Mt, Mw, rewards)
    userHappiness = 100 * (1 - (nmbOfCoalition / nmbOfMatching))
    file = open(os.path.join(resultPathUH, fileName), "a")
    # f.write(str(userHappiness) + "\n")
    file.write(str(nmbOfCoalition) + "," + str(nmbOfMatching) + "\n")
    file.close()
    return userHappiness


# //////////////////////////////-----------------------------------------\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# ---------------------------------------Metrics functions-------------------------------------------
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\-----------------------------------------//////////////////////////////
# calculate the Welch t-statistic
def t_statistic_Welch(means1,means2,stds1,stds2,number_of_simulations):
    t_statistic = []
    freedom_degrees = []
    p_values = []
    for i in range(0,len(means1)):
        mean1 = means1[i]
        mean2 = means2[i]
        std1 = stds1[i]
        std2 = stds2[i]
        t = (mean1-mean2)/ (math.sqrt(((std1**2)/number_of_simulations)+((std2**2)/number_of_simulations) ))
        #t = (mean1-mean2)/ (math.sqrt(((std1**2))+((std2**2) )))
        df = ((((std1**2)/number_of_simulations)+((std2**2)/number_of_simulations))**2) / ( ((std1**4)/((number_of_simulations**3)-number_of_simulations)+((std2**4)/((number_of_simulations**3)-number_of_simulations)) ) )
        t_statistic.append(t)
        freedom_degrees.append(df)
        p_values.append(scipy.stats.t.sf(abs(t), df=df))
    return t_statistic,freedom_degrees,p_values

# calculate the students t-statistic, degree of freesom, p-values
def student_test_shibani(means1,means2,stds1,stds2,number_of_simulations):
    t_statistic = []
    freedom_degrees = []
    p_values = []
    for i in range(0,len(means1)):
        mean1 = means1[i]
        mean2 = means2[i]
        std1 = stds1[i]
        std2 = stds2[i]
        # t = (mean1-mean2)/ (math.sqrt(((std1**2)/number_of_simulations)+((std2**2)/number_of_simulations) ))
        t = (mean1-mean2)/ (math.sqrt(((std1**2)+(std2**2))/2))
        # df = ((((std1**2)/number_of_simulations)+((std2**2)/number_of_simulations))**2) / ( ((std1**4)/((number_of_simulations**3)-number_of_simulations)+((std2**4)/((number_of_simulations**3)-number_of_simulations)) ) )
        df = 2*number_of_simulations - 2 #1.645
        t_statistic.append(t)
        freedom_degrees.append(df)
        p_values.append(scipy.stats.t.sf(abs(t), df=df)*2)
    print("shibani p-values using student t-test= ",p_values)
    return t_statistic,freedom_degrees,p_values

# calculate the students t-statistic, degree of freesom, p-values
def student_test_wiki(means1,means2,stds1,stds2,number_of_simulations):
    t_statistic = []
    freedom_degrees = []
    p_values = []
    for i in range(0,len(means1)):
        mean1 = means1[i]
        mean2 = means2[i]
        std1 = stds1[i]
        std2 = stds2[i]
        # t = (mean1-mean2)/ (math.sqrt(((std1**2)/number_of_simulations)+((std2**2)/number_of_simulations) ))
        t = (mean1-mean2)/ (math.sqrt(((std1**2)+(std2**2))/number_of_simulations))
        # df = ((((std1**2)/number_of_simulations)+((std2**2)/number_of_simulations))**2) / ( ((std1**4)/((number_of_simulations**3)-number_of_simulations)+((std2**4)/((number_of_simulations**3)-number_of_simulations)) ) )
        df = 2*number_of_simulations-2
        t_statistic.append(t)
        freedom_degrees.append(df)
        p_values.append(scipy.stats.t.sf(abs(t), df=df)*2)
    print("wiki p-values using student t-test= ",p_values)
    return t_statistic,freedom_degrees,p_values

def Welch(means1,means2,stds1,stds2,number_of_simulations):
    t_statistic = []
    freedom_degrees = []
    p_values = []
    x = scipy.stats.ttest_ind_from_stats(means1,[std1 for std1 in stds1],number_of_simulations,means2,[std2 for std2 in stds2],number_of_simulations,equal_var=True)
    #print(x)
    #t_statistic.append(t)
    #freedom_degrees.append(df)
    p_values = list(x.pvalue)
    t_statistic = list(x.statistic)
    print("python p_values using student t-test = ", list(p_values))
    return t_statistic,freedom_degrees,p_values

def standard_deviation(names,metric,index_of_simulation):
    i = 0
    for __ in names:
        metric[i][1][index_of_simulation] = np.std(metric[i][2][index_of_simulation])
        i = i+1
    return metric

def coverage_metric(path,results,names,tasks,workers,metric,number_of_simulation,index_of_simulation):
    i = 0
    for element in results:
        ratio,min,max = CoverageQuality(path, str(names[i])+".txt", tasks, element[0])
        metric[i][0][index_of_simulation] += (ratio/number_of_simulation)
        metric[i][2][index_of_simulation].append(ratio)
        #metric[i][1][0][index_of_simulation] += (min/number_of_simulation)
        #metric[i][1][1][index_of_simulation] += (max/number_of_simulation)
        i+=1
    return metric

def used_budget_metric(path, results,names, tasks, workers, metric, number_of_simulation, index_of_simulation):
    i = 0
    for element in results:
        ratio = UsedBudget(path, str(names[i]) + ".txt", tasks, element[0],element[2])
        metric[i][index_of_simulation] += (ratio / number_of_simulation)
        i += 1
    return metric

def average_reward_metric(path,results,names,tasks,workers,metric,number_of_simulation,index_of_simulation):
    i = 0
    for element in results:
        ratio = AverageRewards(path, str(names[i]) + ".txt", element[1], element[2],tasks)
        metric[i][index_of_simulation] += (ratio / number_of_simulation)
        i+=1
    return metric

def reward_by_max_metric(path,results,names,tasks,workers,metric,number_of_simulation,rewards,index_of_simulation):
    i = 0
    for element in results:
        ratio = RewardsByMax(path, str(names[i]) + ".txt", element[1], element[2],rewards)
        metric[i][index_of_simulation] += (ratio / number_of_simulation)
        i+=1
    return metric

def happiness_degree_metric(path,results,names,tasks,workers,metric,number_of_simulation,rewards,index_of_simulation):
    i = 0
    for element in results:
        ratio = HappinessDegree(path, str(names[i]) + ".txt", element[1], element[2],rewards)
        metric[i][index_of_simulation] += (ratio / number_of_simulation)
        i+=1
    return metric

def normalized_happiness_metric(path,results,names,tasks,workers,metric,number_of_simulation,rewards,index_of_simulation):
    i = 0
    for element in results:
        ratio = NormalizedHappiness(path, str(names[i]) + ".txt", element[1], element[2],rewards)
        metric[i][index_of_simulation] += (ratio / number_of_simulation)
        i+=1
    return metric

def average_number_of_workers_metric(path,results,names,tasks,workers,metric,number_of_simulation,index_of_simulation):
    i = 0
    m = len(workers)
    for element in results:
        ratio = average_number_of_worker(path,str(names[i]) + ".txt",element[1],m)
        metric[i][index_of_simulation] += (ratio / number_of_simulation)
        i+=1
    return metric

def number_of_workers_metric(path,results,names,tasks,workers,metric,number_of_simulation,index_of_simulation):
    i = 0
    n = len(tasks)
    for element in results:
        ratio = number_of_worker_per_task(path,str(names[i]) + ".txt",element[0])
        metric[i][index_of_simulation] += (ratio / number_of_simulation)
        i+=1
    return metric


# //////////////////////////////-----------------------------------------\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# ---------------------------------------Helpfully functions-------------------------------------------
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\-----------------------------------------//////////////////////////////

def one_to_one_matching(tasks_list, workers_list, tasks, workers, rewards, Mt):
    if len(tasks_list)>= len(workers_list):
        all_combinations = [list(zip(each_permutation, workers_list)) for each_permutation in itertools.permutations(tasks_list, len(workers_list))]
    else:
        all_combinations = [list(zip(tasks_list, each_permutation)) for each_permutation in itertools.permutations(workers_list, len(tasks_list))]

    max_utility = 0
    final_combination = None
    for combination in all_combinations:
        utility = sum([Ut(tasks[c[0]],[workers[c[1]]] + Mt[c[0]]) if Rt(tasks[c[0]],[workers[c[1]]] + Mt[c[0]],rewards)<=tasks[c[0]][2] else Ut(tasks[c[0]],Mt[c[0]]) for c in combination])
        combination = [c for c in combination if Rt(tasks[c[0]],[workers[c[1]]] + Mt[c[0]],rewards)<=tasks[c[0]][2]]
        if utility > max_utility:
            max_utility = utility
            final_combination = combination

    return final_combination

def worker_many_to_many(Mt):
    testWorkers = []
    for setOfw in Mt:
        for element in setOfw:
            testWorkers.append(element[0])
    if testWorkers.count(max(testWorkers, key=testWorkers.count)) > 1:
        return max(testWorkers, key=testWorkers.count)
    return None

def normalize(max,min,x):
    return (x-min)/(max-min)

def CheckPair(worker,task,Mt,Mw,CheckIf,rewards,workers):
    w = worker[0]
    t = task[0]
    r = 0
    if Mw[w] != None : r = rewards[w][Mw[w][0]]
    if Mw[w] == task or r >rewards[w][t]:
        return False
    S = [work[0] for work in Mt[t]]
    if CheckIf == 0 :
        for workerp in workers:
            wp = workerp[0]
            rp = 0
            if Mw[wp] != None: rp = rewards[w][Mw[wp][0]]
            if rewards[wp][t] !=0 and rp <= rewards[wp][t]:
                S.append(wp)
        S.remove(w)
    Rt = [int(rewards[i][t]) + 1 for i in S]
    Rt.sort()
    L = sortLbyRewards(t, S, rewards)
    Smax = KnapSackp(int(task[2] - rewards[w][t]), Rt, workers, L, task)
    listOfWorkers = [workers[i] for i in Smax[1]+[w]]
    if Ut(task,listOfWorkers) > Ut(task,Mt[t]):
        return True
    return False

def nmbOfCoalitionAndMatching(workers,tasks,Mt,Mw,rewards):
    nmbOfCoalition = 0
    nmbOfMatching = 0
    for w in range(len(workers)):
        for t in range(len(tasks)):
            if rewards[w][t] != 0:
                nmbOfMatching += 1
                if CheckPair(workers[w],tasks[t],Mt,Mw,0,rewards,workers):
                    nmbOfCoalition += 1
    return nmbOfCoalition,nmbOfMatching

def get_total_intersection(set_of_worker,task,cWorkerTask):
    t = task[0]
    points = []
    for worker in set_of_worker:
        w = worker[0]
        newListOfPoints = [pt for pt in cWorkerTask[w][t] if pt not in points]
        testPoI = [pt[0][0] for pt in cWorkerTask[w][t] if pt not in points]
        if len(testPoI) > 1 and 1 < (testPoI.count(max(testPoI, key=testPoI.count))):
            print("found!! = ", testPoI.count(max(testPoI, key=testPoI.count)))
        points = points + newListOfPoints
    return points

def get_number_of_workers(p,Mw):
    number_of_workers = 0
    w = 0
    for __ in cWorkerTask:
        for _ in __:
            for point in _:
                if p[0] == point[0][0]:
                    # if the worker is already matched we will not count it
                    if Mw[w] == None:
                        number_of_workers =+ 1
        w += 1
    return number_of_workers

def get_c_worker_point(set_PoI):
    c_worker_point = []
    c_task_point = [[0 for __ in set_PoI] for _ in (cWorkerTask[0])]
    for i in range(len(cWorkerTask)):
        point_list_w = [0 for _ in set_PoI]
        point_list_t = [0 for _ in set_PoI]
        t = 0
        for points in cWorkerTask[i]:
            for point in points:
                p = point[0][0]
                point_list_w[p] = 1
                point_list_t[p] = 1
            c_task_point[t] = (np.add(np.array(c_task_point[t]),np.array(point_list_t))).tolist()
            t+= 1
        c_worker_point.append(point_list_w)

    return c_worker_point,c_task_point

def get_list_of_point_by_importance_bias(c_worker_point,c_task_point):

    cwp = np.array(c_worker_point)
    ctp = np.array(c_task_point)
    sum_cwp = np.sum(cwp, axis=0)
    sum_stp = np.sum(ctp, axis=0)
    list_of_importance = []
    for i in range(len(sum_cwp)):
        if sum_cwp[i] != 0:
            list_of_importance.append(sum_stp[i]/sum_cwp[i])
            # list_of_importance.append(1/sum_cwp[i])
        else :
            list_of_importance.append(0)
    return list_of_importance, [sum_cwp,sum_stp]

def get_list_of_point_by_importance(c_worker_point):

    cwp = np.array(c_worker_point)
    # ctp = np.array(c_task_point)
    sum_cwp = np.sum(cwp, axis=0)
    # sum_stp = np.sum(ctp, axis=0)
    list_of_importance = []
    for i in range(len(sum_cwp)):
        if sum_cwp[i] != 0:
            # list_of_importance.append(sum_stp[i]/sum_cwp[i])
            list_of_importance.append(1/sum_cwp[i])
        else :
            list_of_importance.append(0)
    return list_of_importance, sum_cwp

def get_task_index_sorted_by_importance(list_of_importance,tasks,Mt):

    tasksIndex = [i[0] for i in tasks]
    tasks_importance_value = tasks_importance_by_PoIs(tasks, list_of_importance,Mt)
    #print(tasks_importance_value)
    new_tasks_index = [x for _, x in sorted(zip(tasks_importance_value, tasksIndex),reverse=True)]
    return new_tasks_index

def get_task_index_sorted_by_importance_prim(list_of_importance,tasks,Mt):

    tasksIndex = [i[0] for i in tasks]
    tasks_importance_value = tasks_importance_by_PoIs_prim(tasks, list_of_importance,Mt)
    #print(tasks_importance_value)
    new_tasks_index = [x for _, x in sorted(zip(tasks_importance_value, tasksIndex),reverse=True)]
    return new_tasks_index,tasks_importance_value

def tasks_importance_value_modification_old(tasks_importance_value,list_of_importance,worker,task,covered_point,Mt,tasks):
    w = worker[0]
    point_considered = []
    for t in range(len(cWorkerTask[w])):
        for point in cWorkerTask[w][t]:
            p = point[0][0]
            if p not in covered_point[t]:
                if p not in point_considered:
                    point_considered.append(p)
                    list_of_importance[p] -= 1

                if t == task[0]:
                    tasks_importance_value[t] += - point[1]/(list_of_importance[p]+1)
                    covered_point[t].append(p)
                else:
                    # if list_of_importance[p] <0:
                    #     print(list_of_importance[p])
                    if list_of_importance[p] == 0:
                        tasks_importance_value[t] += - point[1]
                    else:
                        tasks_importance_value[t] += point[1]/(list_of_importance[p]) - point[1]/(list_of_importance[p]+1)

        # new_task_importance_value = 0
        # for point in tasks[t][1]:
        #     p = point[0][0]
        #
        #     # if t == task[0] and p in point_considered:
        #     if t != task[0] or p not in point_considered:
        #         points = []
        #         for wor in Mt[t]:
        #             points += [pts[0][0] for pts in cWorkerTask[wor[0]][t]]
        #         if p not in points:
        #             if list_of_importance[p] != 0:
        #                 new_task_importance_value += point[1]/(list_of_importance[p])
        #
        # tasks_importance_value[t] = new_task_importance_value
        # print(new_task_importance_value, "", tasks_importance_value[t])

    return tasks_importance_value,list_of_importance,covered_point


def tasks_importance_value_modification(tasks_importance_value,list_of_importance,cpw,worker,task,covered_point,Mt,tasks):
    w = worker[0]
    point_considered = []
    old_list_of_importance = list_of_importance.copy()
    for t in range(len(cWorkerTask[w])):
        for point in cWorkerTask[w][t]:
            p = point[0][0]
            if p not in covered_point[t]:
                if p not in point_considered:
                    point_considered.append(p)
                    cpw[p] -= 1
                    if cpw[p]<0 : print("cpw is negative")
                    if cpw[p]==0:   list_of_importance[p] = 0
                    # changed 4/24/2023 else:           list_of_importance[p] -= (1/cpw[p])*(old_list_of_importance[p])
                    else:           list_of_importance[p] = (1/cpw[p])

                if t == task[0]:
                    tasks_importance_value[t] += - point[1] * (old_list_of_importance[p])
                    covered_point[t].append(p)
                else:
                    if list_of_importance[p] <0:
                        # print(list_of_importance[p])
                        print("importance is negative")
                    if list_of_importance[p] == 0:
                        tasks_importance_value[t] += - point[1]
                    else:
                        tasks_importance_value[t] += point[1]*(list_of_importance[p]) - point[1]*(old_list_of_importance[p])
    return tasks_importance_value,list_of_importance,covered_point

def tasks_importance_value_modification_bias(tasks_importance_value,list_of_importance,cpw,cpt,worker,task,covered_point,Mt,tasks):
    w = worker[0]
    point_considered = []
    old_list_of_importance = list_of_importance.copy()
    for t in range(len(cWorkerTask[w])):
        for point in cWorkerTask[w][t]:
            p = point[0][0]
            if p not in covered_point[t]:
                if p not in point_considered:
                    point_considered.append(p)
                    cpw[p] -= 1
                    if cpw[p]<0 : print("cpw is negative")
                    if cpw[p]==0:   list_of_importance[p] = 0
                    # changed 4/24/2023 else:           list_of_importance[p] -= (1/cpw[p])*(old_list_of_importance[p])
                    else:           list_of_importance[p] = (cpt[p]/cpw[p])

                if t == task[0]:
                    cpt[p] -= 1
                    if cpt[p]<0 : print("cpt is negative")
                    if cpt[p]==0:   list_of_importance[p] = 0
                    else:  list_of_importance[p] = (cpt[p] / cpw[p])
                    tasks_importance_value[t] += - point[1] * (old_list_of_importance[p])
                    covered_point[t].append(p)
                else:
                    if list_of_importance[p] <0:
                        # print(list_of_importance[p])
                        print("importance is negative")
                    if list_of_importance[p] == 0:
                        tasks_importance_value[t] += - point[1]
                    else:
                        tasks_importance_value[t] += point[1]*(list_of_importance[p]) - point[1]*(old_list_of_importance[p])
    return tasks_importance_value,list_of_importance,covered_point

def get_task_importance_value_prim(list_of_importance,tasks,Mt):

    # tasksIndex = [i[0] for i in tasks]
    tasks_importance_value = tasks_importance_by_PoIs_prim(tasks, list_of_importance,Mt)
    #print(tasks_importance_value)
    #new_tasks_index = [x for _, x in sorted(zip(tasks_importance_value, tasksIndex),reverse=True)]
    return tasks_importance_value

def sort_list_based_list_by_count(L1,L2):
    L1.sort(key=lambda worker: len(L2[worker]))
    L2.sort(key=len())
    return L1,L2

def compute_improtance_value_by_task(list_of_importance,task,worker_list):
    t = task[0]
    importance_value = 0
    for point in task[1]:
        p = point[0][0]

        # need to consider a penalty if the point is already covered by a worker for this task to not get high rank.
        # if the point is already coverd by the workers matched with task t then we do not concider the worker
        can_be_concider = True
        for worker in worker_list:
            w = worker[0]
            if point in cWorkerTask[w][t]:
                can_be_concider = False
        if can_be_concider and list_of_importance[p] != 0:
            # last update at 6/23/2022 where i cange importance_value += list_of_importance[p]/point[1] to
            importance_value += list_of_importance[p]/point[1]
    return importance_value

def tasks_importance_by_PoIs(tasks,list_of_importance,Mt):
    task_importance_value = [0 for _ in tasks]
    for task in tasks:
        t = task[0]
        importance_value = 0
        for point in task[1]:
            p = point[0][0]

            # need to consider a penalty if the point is already covered by a worker for this task to not get high rank.
            # if the point is already coverd by the workers matched with task t then we do not concider the worker
            can_be_concider = True
            for worker in Mt[t]:
                w = worker[0]
                if point in cWorkerTask[w][t]:
                    # print("not considered")
                    can_be_concider = False
            if can_be_concider and list_of_importance[p] != 0:
                # last update at 6/23/2022 where i cange importance_value += list_of_importance[p]/point[1] to
                importance_value += list_of_importance[p]/point[1]

        if importance_value != 0: task_importance_value[t] = 1 / importance_value
    return task_importance_value

def tasks_importance_by_PoIs_prim(tasks,list_of_importance,Mt):
    task_importance_value = [0 for _ in tasks]
    for task in tasks:
        t = task[0]
        importance_value = 0
        for point in task[1]:
            p = point[0][0]

            # need to consider a penalty if the point is already covered by a worker for this task to not get high rank.
            # if the point is already coverd by the workers matched with task t then we do not concider the worker
            can_be_concider = True
            for worker in Mt[t]:
                w = worker[0]
                if point in cWorkerTask[w][t]:
                    # print("not considered")
                    can_be_concider = False
            if can_be_concider: # and list_of_importance[p] != 0:
                # last update at 6/23/2022 where i cange importance_value += list_of_importance[p]/point[1] to
                # last update at 4/24/2023 where i cange importance_value += point[1] * list_of_importance[p]
                importance_value += point[1] * list_of_importance[p]

        if importance_value != 0: task_importance_value[t] = importance_value
    return task_importance_value


def copy_reward(reward):
    
    return reward


def copy_reward_prim(reward):
    new_reward = []
    for i in range(len(reward)):
        new_reward.append([])
        for element in reward[i]:
            new_reward[i].append(element)
    return new_reward

def number_of_task_to_budget_mean(x,min1,max1,min2,max2):
    return min2 + (x-min1)*((max2-min2)/(max1-min1))

def changeWorkersOrganisation(workers):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    newWorkers = []
    for w in workers:
        worker = w[1]
        x = []
        y = []
        for i in range(len(worker)):
            x.append(worker[i][0])
            y.append(worker[i][1])
        newWorkers.append([x,y])
    return newWorkers

def changePoIOrganisation(PoI):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    x = []
    y = []
    for i in range(len(PoI)):
        x.append(PoI[i][1][0])
        y.append(PoI[i][1][1])
    return [x,y]

def changePoIOrganisation1(PoI):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    x = []
    y = []
    for i in range(len(PoI)):
        x.append(PoI[i][0])
        y.append(PoI[i][1])
    return [x,y]

def workerContainThePoint(worker,myx,myy):
    i = -1
    k = 0
    l = 1
    while (i < len(worker[k])-2):
        i = i + 1
        if ((worker[k][i] <= myx and worker[k][i + 1] > myx) or (
                worker[k][i] > myx and worker[k][i + 1] <= myx)):
            x,m = getYfromX(worker, i, myx, 0, 1)
            # go to https://www.alloprof.qc.ca/fr/eleves/bv/mathematiques/la-distance-d-un-point-a-une-droite-dans-un-plan-m1315
            value =(abs(m*myx-myy+(worker[l][i]-m*worker[k][i]))/(math.sqrt((m*m)+1)))
            if (value <= 50):
                return True
    return False

def getYfromX(worker,i,myx,k,l):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    m = 0
    if ((worker[k][i + 1] != worker[k][i])):
        m = (worker[l][i + 1] - worker[l][i]) / (
                worker[k][i + 1] - worker[k][i])
    myy = m * (myx - worker[k][i]) + worker[l][i]
    return [myy,m]

# read one file by path
def read_text_file(file_path):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    with open(file_path, 'r') as f:
        moves = []
        file = f.read()
        lines = file.split("\n")
        for line in lines:
            lineElements = line.split()
            if len(lineElements) > 0:
                moves.append([float(lineElements[1]),float(lineElements[2])])
        return moves

# iterate through all file
def read_Data_Set(path):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    # Change the directory
    os.chdir(path)
    workers = []
    i = 0
    for file in os.listdir():
        # Check whether file is in text format or not
        if file.endswith(".txt"):
            #file_path = f"{path}\{file}"
            file_path = os.path.join(path,file)
            # call read text file function
            moves = read_text_file(file_path)
            workers.append([i,moves])
            i = i + 1
    return workers

def ComputeCworkers(PoI,workers1):
    workers = changeWorkersOrganisation(workers1)
    Cworkers = [[].copy() for i in range(len(workers))]
    count = 0
    distinctCount = 0
    totalDistinctCount = 0
    listOfDone = []
    totalListOfDone = []
    #print("len PoI : ",len(PoI))
    for point in PoI:
        myx = point[1][0]
        myy = point[1][1]
        for t in range(len(workers)):
            if workerContainThePoint(workers[t],myx,myy):
                Cworkers[t].append([myx, myy])
                count = count + 1
                if point[0] not in listOfDone:
                    distinctCount +=1
                    listOfDone.append(point[0])
            if point[1] not in totalListOfDone:
                totalDistinctCount +=1
                totalListOfDone.append(point[1])
    for t in range(len(workers)):
        if len(Cworkers[t]) > 1:
            if Cworkers[t].count(max(Cworkers[t], key=Cworkers[t].count))  > 1:
                print("Cworker generation  = ", Cworkers[t].count(max(Cworkers[t], key=Cworkers[t].count)))
    # print("number of couples (w,p) where the worker w cover the point p = ", count)
    # print("number of point covered by at least one worker = ", distinctCount)
    # print("number of point = ", totalDistinctCount)
    return Cworkers

def GeneratePoI4(workers1,number_of_PoIs):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    # Cworkers = [[].copy() for i in range(len(workers1))]
    numberOfPoint = [0 for i in range(len(workers1))]
    workers = changeWorkersOrganisation(workers1)
    points = []
    count = 0
    for j in range(number_of_PoIs):
        # select randomnly a worker
        workersRand = secrets.randbelow(len(workers))
        maxRangX = max(workers[workersRand][0])
        minRangX = min(workers[workersRand][0])
        maxRangY = max(workers[workersRand][1])
        minRangY = min(workers[workersRand][1])
        k = 0;
        l = 1
        # chose the axis that has the most movement range for the worker and use it to select the random value
        if (maxRangY - minRangY) > (maxRangX - minRangX):
            k = 1;
            l = 0;
            maxRangX = maxRangY
            minRangX = minRangY
        myx = random.uniform(minRangX, maxRangX)
        i = -1;
        notFound = True
        # find where the worker pass through the point
        listOfY = []
        listOfWorker = []
        while (i < len(workers[workersRand][k]) - 2):
            i = i + 1
            if ((workers[workersRand][k][i] <= myx and workers[workersRand][k][i + 1] > myx) or (
                    workers[workersRand][k][i] > myx and workers[workersRand][k][i + 1] <= myx)):
                notFound = False
                myElement = getYfromX(workers[workersRand], i, myx, k, l)
                myy1 = myElement[0]
                m = myElement[1]
                listOfY.append(myy1)

        if notFound: print(notFound)

        myy = np.random.choice(listOfY)

        '''
        # I remove it because at the end some of the point are not covered by any worker (7 points - 12 points)
        print([myx,myy] , end='')

        nMyx = random.uniform(myx-49, myx+49)
        rangeX = abs(nMyx - myx)
        rangeY = math.sqrt(49*49 - rangeX*rangeX)
        myy = random.uniform(myy-rangeY, myy+rangeY)
        myx = nMyx

        print(" ", [myx,myy])
        '''

        '''listOfWorker.append(workersRand)
        for t in range(len(workers)):
            if workerContainThePoint(workers[t],myx,myy,k,l) and t != workersRand:
                listOfWorker.append(t)
        '''

        if k == 0:
            '''for t in listOfWorker:
                Cworkers[t].append([myx, myy])
                count = count + 1'''
            # Cworkers[workersRand].append([myx,myy])
            points.append([j, [myx, myy]])
        else:
            '''for t in listOfWorker:
                Cworkers[t].append([myy,myx])
                count = count + 1'''
            # Cworkers[workersRand].append([myy,myx])
            points.append([j, [myy, myx]])

    # plt.plot(range(len(workers)),numberOfPoint)
    # plt.show()
    # indexPoint = random.sample(points, 300)
    # indexPoint = np.random.choice((l, 3))
    # return points,Cworkers
    return points

# show worker pattern
def workerPattern(workers1, PoI1,folderPath,HPC):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    # workers1 = read_Data_Set(path)
    # PoI1, Cworkers = GeneratePoI4(workers1)
    PoI = changePoIOrganisation1(PoI1)
    workers = changeWorkersOrganisation(workers1)
    for element in workers:
        plt.plot(element[0], element[1])
    plt.plot(PoI[0], PoI[1], 'r.')
    name = os.path.join(folderPath, "DataSet.png")
    if HPC == 0:
        plt.show()
    else:
        plt.savefig(name)
    # plt.show()
    plt.close()

# show worker pattern
def workerPattern1(workers1, PoI1, folderPath):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    # workers1 = read_Data_Set(path)
    # PoI1, Cworkers = GeneratePoI4(workers1)
    PoI = changePoIOrganisation1(PoI1)
    workers = changeWorkersOrganisation(workers1)
    for element in workers:
        plt.plot(element[0], element[1])
    plt.plot(PoI[0], PoI[1], 'r.')
    name = os.path.join(folderPath, "DataSet.png")
    plt.savefig(name)
    # plt.show()
    plt.close()

#get the intersection between the point that the set if workers pass through and the set of the tasks interset
def getIntersectionPoints(Cworker,Ctask):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    points = []
    for workerPoint in Cworker:
        for taskPoint in Ctask:
            #if (len(workerPoint) != 0):
                if workerPoint[0] == taskPoint[0][1][0] and workerPoint[1] == taskPoint[0][1][1]:
                    points.append(taskPoint)
    return points

#list of all intersection point between task and worker
def CworkerTask(tasks,workers,Cworkers):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask, cWorkerTaskp
    global cWorkerTask, cWorkerTaskp
    cWorkerTaskp = [[].copy() for i in range(len(workers))]
    cWorkerTask = [[].copy() for i in range(len(workers))]


    for worker in workers:
        for task in tasks:
            w = worker[0]
            t = task[0]

            intersectionPoints = getIntersectionPoints(Cworkers[w],task[1])
            testPoI = []
            for element in intersectionPoints:
                testPoI.append(element)
            if testPoI != [] and testPoI.count(max(testPoI, key=testPoI.count))>1: print(testPoI.count(max(testPoI, key=testPoI.count)))
            cWorkerTask[w].append(intersectionPoints.copy())
            cWorkerTaskp[w].append(intersectionPoints.copy())
    
    return cWorkerTask,cWorkerTaskp

def getWeightPoint(task,p):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    for point in task[1]:
        if point[0][0] == p:
            return point[1]

#
def getTotalWeightPoint(pointTask):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    w = 0;
    for point in pointTask:
        w = w + point[1]
    return w

def generateNormalizedProportionalFairRewards_with_overall_reward_average_regardless_covering_the_point_or_not(workers,tasks,PoI):
    global cWorkerTask
    n = len(tasks)
    m = len(workers)
    workerTaskRewards = [[0 for _ in tasks].copy() for __ in workers]
    avg_budget = sum([task[2] for task in tasks])/n
    avg_points_reward = []
    for i in range(len(PoI)):
        number_of_tasks_interested_on_that_point = 0
        avg_point_reward = 0
        for task in tasks:
            for point in task[1]:
                point_index = point[0][0]       
                if i == point_index:
                    number_of_tasks_interested_on_that_point +=1
                    avg_point_reward += point[1]
        if number_of_tasks_interested_on_that_point :
            avg_points_reward.append(avg_budget * avg_point_reward/number_of_tasks_interested_on_that_point)
        else: avg_points_reward.append(0) 

    for task in tasks:
        for worker in workers:
            t = task[0]
            w = worker[0]
            intersectionPoints = cWorkerTask[worker[0]][task[0]]
            n_p = len(intersectionPoints)
            reward = 0
            if n_p != 0:  
                for k in range(len(PoI)):          
                    # print("PoI[k][0] =", PoI[k][0])
                    # print("[point[0][0] for point in cWorkerTask[w][t]]", [point[0][0] for point in cWorkerTask[w][t]])
                    # print("PoI[k][0] in [point[0][0] for point in cWorkerTask[w][t]]",PoI[k][0] in [point[0][0] for point in cWorkerTask[w][t]])
                    # exit()       
                    if PoI[k][0] in [point[0][0] for point in cWorkerTask[w][t]]:
                        reward += avg_points_reward[k]
            workerTaskRewards[w][t] = reward

    return workerTaskRewards

def generateNormalizedProportionalFairRewards(workers,tasks,PoI):
    global cWorkerTask
    n = len(tasks)
    m = len(workers)
    workerTaskRewards = [[0 for _ in tasks].copy() for __ in workers]
    # avg_budget = sum([task[2] for task in tasks])/n
    avg_points_reward = []
    for i in range(len(PoI)):
        avg_budget = 0
        number_of_tasks_interested_on_that_point = 0
        total_point_weights = 0
        for task in tasks:
            for point in task[1]:
                point_index = point[0][0]       
                if i == point_index:
                    avg_budget += task[2]
                    number_of_tasks_interested_on_that_point +=1
                    total_point_weights += point[1]
        if number_of_tasks_interested_on_that_point :
            avg_points_reward.append(avg_budget * total_point_weights/number_of_tasks_interested_on_that_point**2)
        else: avg_points_reward.append(0) 

    for task in tasks:
        for worker in workers:
            t = task[0]
            w = worker[0]
            intersectionPoints = cWorkerTask[worker[0]][task[0]]
            n_p = len(intersectionPoints)
            reward = 0
            if n_p != 0:  
                for k in range(len(PoI)):
                    if PoI[k][0] in [point[0][0] for point in cWorkerTask[w][t]]:
                        reward += avg_points_reward[k]
            workerTaskRewards[w][t] = reward

    return workerTaskRewards

def generateNormalizedProportionalFairRewards_trying_to_correct(workers,tasks,PoI):
    global cWorkerTask
    n = len(tasks)
    m = len(workers)
    workerTaskRewards = [[0 for _ in tasks].copy() for __ in workers]
    # avg_budget = sum([task[2] for task in tasks])/n
    avg_points_reward = []
    for i in range(len(PoI)):
        avg_budget = 0
        number_of_tasks_interested_on_that_point = 0
        total_point_weights = 0
        for task in tasks:
            found = False
            for point in task[1]:
                point_index = point[0][0]       
                if i == point_index:
                    found = True
                    avg_budget += task[2]
                    number_of_tasks_interested_on_that_point +=1
                    total_point_weights += point[1]
            if found:
                avg_budget += task[2]
        if number_of_tasks_interested_on_that_point:
            avg_points_reward.append(avg_budget * avg_point_reward/number_of_tasks_interested_on_that_point**2)
        else: avg_points_reward.append(0)
    
        if number_of_tasks_interested_on_that_point :
            avg_points_reward.append(avg_budget * total_point_weights/number_of_tasks_interested_on_that_point**2)
        else: avg_points_reward.append(0) 

    for task in tasks:
        for worker in workers:
            t = task[0]
            w = worker[0]
            intersectionPoints = cWorkerTask[worker[0]][task[0]]
            n_p = len(intersectionPoints)
            reward = 0
            if n_p != 0:  
                for k in range(len(PoI)):
                    if PoI[k][0] in [point[0][0] for point in cWorkerTask[w][t]]:
                        reward += avg_points_reward[k]
            workerTaskRewards[w][t] = reward

    return workerTaskRewards

def generateGeneralandFairRewards_with_overall_reward_average_regardless_covering_the_point_or_not(workers, tasks, PoI):
    global cWorkerTask
    n = len(tasks)
    m = len(workers)
    workerTaskRewards = [[0 for _ in tasks].copy() for __ in workers]
    avg_budget = sum([task[2] for task in tasks])/n
    avg_points_reward = []
    for i in range(len(PoI)):
        number_of_tasks_interested_on_that_point = 0
        avg_point_reward = 0
        for task in tasks:
            for point in task[1]:
                point_index = point[0][0]       
                if i == point_index:
                    number_of_tasks_interested_on_that_point +=1
                    avg_point_reward += point[1]
        if number_of_tasks_interested_on_that_point:
            avg_points_reward.append(avg_budget * avg_point_reward/number_of_tasks_interested_on_that_point)
        else: avg_points_reward.append(0)
    min_p = float('inf')
    max_p = 0
    total_reward_of_the_system = 0
    for task in tasks:
        for worker in workers:
            t = task[0]
            w = worker[0]
            intersectionPoints = cWorkerTask[worker[0]][task[0]]
            n_p = len(intersectionPoints)
            if n_p != 0:
                if min_p > n_p: min_p = n_p
                if max_p < n_p: max_p = n_p   
                for k in range(len(PoI)):
                    # print("PoI[k][0] =", PoI[k][0])
                    # print("[point[0][0] for point in cWorkerTask[w][t]]", [point[0][0] for point in cWorkerTask[w][t]])
                    # print("PoI[k][0] in [point[0][0] for point in cWorkerTask[w][t]]",PoI[k][0] in [point[0][0] for point in cWorkerTask[w][t]])
                    # exit()
                    if PoI[k][0] in [point[0][0] for point in cWorkerTask[w][t]]:
                        
                        total_reward_of_the_system += avg_points_reward[k]


    avg_reward_task_worker = total_reward_of_the_system/(n*m)
    alpha = 2/(min_p + max_p)
    for task in tasks:
        for worker in workers:
            t = task[0]
            w = worker[0]
            workerTaskRewards[w][t] = avg_reward_task_worker * random.uniform(alpha *min_p , alpha * max_p)
    
    return workerTaskRewards

def generateGeneralandFairRewards_maybe_wrong(workers, tasks, PoI):
    global cWorkerTask
    n = len(tasks)
    m = len(workers)
    workerTaskRewards = [[0 for _ in tasks].copy() for __ in workers]
    avg_budget = sum([task[2] for task in tasks])/n
    avg_points_reward = []
    for i in range(len(PoI)):
        number_of_tasks_interested_on_that_point = 0
        avg_point_reward = 0
        for task in tasks:
            for point in task[1]:
                point_index = point[0][0]       
                if i == point_index:
                    number_of_tasks_interested_on_that_point +=1
                    avg_point_reward += point[1]
        if number_of_tasks_interested_on_that_point:
            avg_points_reward.append(avg_budget * avg_point_reward/number_of_tasks_interested_on_that_point**2)
        else: avg_points_reward.append(0)
    min_p = float('inf')
    max_p = 0
    total_reward_of_the_system = 0
    for task in tasks:
        for worker in workers:
            t = task[0]
            w = worker[0]
            intersectionPoints = cWorkerTask[worker[0]][task[0]]
            n_p = len(intersectionPoints)
            if n_p != 0:
                if min_p > n_p: min_p = n_p
                if max_p < n_p: max_p = n_p   
                for k in range(len(PoI)):
                    if PoI[k][0] in [point[0][0] for point in cWorkerTask[w][t]]:
                        
                        total_reward_of_the_system += avg_points_reward[k]


    avg_reward_task_worker = total_reward_of_the_system/(n*m)
    alpha = 2/(min_p + max_p)
    for task in tasks:
        for worker in workers:
            t = task[0]
            w = worker[0]
            workerTaskRewards[w][t] = avg_reward_task_worker * random.uniform(alpha *min_p , alpha * max_p)
    
    return workerTaskRewards

def generateGeneralandFairRewards_old(workers, tasks, PoI):
    global cWorkerTask
    n = len(tasks)
    m = len(workers)
    workerTaskRewards = [[0 for _ in tasks].copy() for __ in workers]
    # avg_budget = sum([task[2] for task in tasks])/n
    avg_points_reward = []
    for i in range(len(PoI)):
        avg_budget = 0
        number_of_tasks_interested_on_that_point = 0
        avg_point_reward = 0
        for task in tasks:
            for point in task[1]:
                point_index = point[0][0]       
                if i == point_index:
                    avg_budget += task[2]
                    number_of_tasks_interested_on_that_point +=1
                    avg_point_reward += point[1]
        if number_of_tasks_interested_on_that_point:
            avg_points_reward.append(avg_budget * avg_point_reward/number_of_tasks_interested_on_that_point**2)
        else: avg_points_reward.append(0)
    
    # avg_points_reward = [for i in range(len(PoI))]

    # avg_budget = sum(avg_points_reward)
    
    min_p = float('inf')
    max_p = 0
    total_reward_of_the_system = 0
    for task in tasks:
        for worker in workers:
            t = task[0]
            w = worker[0]
            intersectionPoints = cWorkerTask[worker[0]][task[0]]
            n_p = len(intersectionPoints)
            if n_p != 0:
                if min_p > n_p: min_p = n_p
                if max_p < n_p: max_p = n_p   
                for k in range(len(PoI)):
                    if PoI[k][0] in [point[0][0] for point in cWorkerTask[w][t]]:
                        
                        total_reward_of_the_system += avg_points_reward[k]


    avg_reward_task_worker = total_reward_of_the_system/(n*m)
    alpha = 2/(min_p + max_p)
    for task in tasks:
        for worker in workers:
            t = task[0]
            w = worker[0]
            workerTaskRewards[w][t] = avg_reward_task_worker * random.uniform(alpha *min_p , alpha * max_p)
    

    # test
    # values = [workerTaskRewards[w][t] for t in range(n) for w in range(m)]
    # bin_size = 0.005
    # folder_path = r"/home/abderrafi.abdeddine/PycharmProjects/EfficientTaskAllocation/old Implementations/test.png"
    # plt.figure(figsize=(8, 6))
    # plt.hist(values, bins=np.arange(min(values), max(values) + bin_size, bin_size), edgecolor='black', alpha=0.7)
    # plt.title('Binned Histogram of Elements')
    # plt.xlabel('Value Range')
    # plt.ylabel('Frequency')
    # plt.grid(True)
    # plt.savefig(folder_path)
    # exit()

    return workerTaskRewards


def generateGeneralandFairRewards(workers, tasks, PoI):
    global cWorkerTask
    n = len(tasks)
    m = len(workers)
    workerTaskRewards = [[0 for _ in tasks].copy() for __ in workers]
    # avg_budget = sum([task[2] for task in tasks])/n
    avg_points_reward = []
    for i in range(len(PoI)):
        avg_budget = 0
        number_of_tasks_interested_on_that_point = 0
        avg_point_reward = 0
        for task in tasks:
            for point in task[1]:
                point_index = point[0][0]       
                if i == point_index:
                    avg_budget += task[2]
                    number_of_tasks_interested_on_that_point +=1
                    avg_point_reward += point[1]
        if number_of_tasks_interested_on_that_point:
            avg_points_reward.append(avg_budget * avg_point_reward/number_of_tasks_interested_on_that_point**2)
        else: avg_points_reward.append(0)
    
    # avg_points_reward = [for i in range(len(PoI))]

    # avg_budget = sum(avg_points_reward)
    
    min_p = float('inf')
    max_p = 0
    total_reward_of_the_system = 0
    number_of_elements_cumulated = 0
    for task in tasks:
        for worker in workers:
            t = task[0]
            w = worker[0]
            intersectionPoints = cWorkerTask[worker[0]][task[0]]
            n_p = len(intersectionPoints)
            if n_p != 0:
                number_of_elements_cumulated += 1
                if min_p > n_p: min_p = n_p
                if max_p < n_p: max_p = n_p   
                for k in range(len(PoI)):
                    if PoI[k][0] in [point[0][0] for point in cWorkerTask[w][t]]:
                        
                        total_reward_of_the_system += avg_points_reward[k]/n_p


    avg_reward_task_worker = total_reward_of_the_system/number_of_elements_cumulated
    # alpha = 2/(min_p + max_p)
    for task in tasks:
        for worker in workers:
            t = task[0]
            w = worker[0]
            workerTaskRewards[w][t] = avg_reward_task_worker * random.uniform(min_p , max_p)
    

    # test
    # values = [workerTaskRewards[w][t] for t in range(n) for w in range(m)]
    # bin_size = 0.005
    # folder_path = r"/home/abderrafi.abdeddine/PycharmProjects/EfficientTaskAllocation/old Implementations/test.png"
    # plt.figure(figsize=(8, 6))
    # plt.hist(values, bins=np.arange(min(values), max(values) + bin_size, bin_size), edgecolor='black', alpha=0.7)
    # plt.title('Binned Histogram of Elements')
    # plt.xlabel('Value Range')
    # plt.ylabel('Frequency')
    # plt.grid(True)
    # plt.savefig(folder_path)
    # exit()

    return workerTaskRewards


def generateGeneralandFairRewards_trying_to_correct(workers, tasks, PoI):
    global cWorkerTask
    n = len(tasks)
    m = len(workers)
    workerTaskRewards = [[0 for _ in tasks].copy() for __ in workers]
    # avg_budget = sum([task[2] for task in tasks])/n
    avg_points_reward = []
    for i in range(len(PoI)):
        avg_budget = 0
        number_of_tasks_interested_on_that_point = 0
        avg_point_reward = 0
        for task in tasks:
            found = False
            for point in task[1]:
                point_index = point[0][0]       
                if i == point_index:
                    found = True
                    number_of_tasks_interested_on_that_point +=1
                    avg_point_reward += point[1]
            if found:
                avg_budget += task[2]
        if number_of_tasks_interested_on_that_point:
            avg_points_reward.append(avg_budget * avg_point_reward/number_of_tasks_interested_on_that_point**2)
        else: avg_points_reward.append(0)
    
    # avg_points_reward = [for i in range(len(PoI))]

    # avg_budget = sum(avg_points_reward)
    
    min_p = float('inf')
    max_p = 0
    total_reward_of_the_system = 0
    for task in tasks:
        for worker in workers:
            t = task[0]
            w = worker[0]
            intersectionPoints = cWorkerTask[worker[0]][task[0]]
            n_p = len(intersectionPoints)
            if n_p != 0:
                if min_p > n_p: min_p = n_p
                if max_p < n_p: max_p = n_p   
                for k in range(len(PoI)):
                    if PoI[k][0] in [point[0][0] for point in cWorkerTask[w][t]]:
                        
                        total_reward_of_the_system += avg_points_reward[k]


    avg_reward_task_worker = total_reward_of_the_system/(n*m)
    alpha = 2/(min_p + max_p)
    for task in tasks:
        for worker in workers:
            t = task[0]
            w = worker[0]
            workerTaskRewards[w][t] = avg_reward_task_worker * random.uniform(alpha *min_p , alpha * max_p)
    
    return workerTaskRewards

#generate rewards the lines are the workers and the column are the taskss
def generateGeneralRewards(workers,tasks):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    global cWorkerTask
    workerTaskRewards = [[].copy() for i in range(len(workers))]
    i = 0
    for worker in workers:
        for task in tasks:
            intersectionPoints = cWorkerTask[worker[0]][task[0]]
            if len(intersectionPoints) != 0:
                budget = task[2]
                #budget = budgetp/1000
                reward = random.uniform(0.05*budget, 0.95*budget)
                workerTaskRewards[i].append(reward)
            else:
                workerTaskRewards[i].append(0)
        i = i+1
    return workerTaskRewards

def generateProportionalRewards(workers,tasks):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    global cWorkerTask
    workerTaskRewards = [[].copy() for i in  range(len(workers))]
    i = 0
    for worker in workers:
        for task in tasks:

            intersectionPoints = cWorkerTask[worker[0]][task[0]]
            totalWeightPointOfTask = getTotalWeightPoint(task[1])
            totalWeightPointOfintersection = getTotalWeightPoint(intersectionPoints)
            if len(intersectionPoints) != 0:
                budget = task[2]
                #budget = budgetp / 1000
                reward = budget*(totalWeightPointOfintersection/totalWeightPointOfTask)
                if reward > budget :
                    reward = budget
                workerTaskRewards[i].append(reward)
            else:
                workerTaskRewards[i].append(0)
        i = i + 1
    return workerTaskRewards

def generateNormalizedProportionalRewards(workers,tasks):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    global cWorkerTask
    workerTaskRewards = [[].copy() for i in  range(len(workers))]
    i = 0
    for worker in workers:
        for task in tasks:

            intersectionPoints = cWorkerTask[worker[0]][task[0]]
            totalWeightPointOfTask = getTotalWeightPoint(task[1])
            totalWeightPointOfintersection = getTotalWeightPoint(intersectionPoints)
            if len(intersectionPoints) != 0:
                budget = 55
                #budget = budgetp / 1000
                reward = budget*(totalWeightPointOfintersection/totalWeightPointOfTask)
                if reward > budget :
                    reward = budget
                workerTaskRewards[i].append(reward)
            else:
                workerTaskRewards[i].append(0)
        i = i + 1
    return workerTaskRewards

def retrieveFromC(L1,L2):
    L3 = []

    for p1 in L1:
        add = True
        for p2 in L2:
            if p1[0][0] == p2[0][0]:
                add = False
                break
        if add:
            L3.append(p1)
    return L3

#Initialize (W, T ,M)
def workers_current_system_utility(tasks,workers,Mt):
    list = [0 for _ in workers]
    for worker in workers:
        w = worker[0]
        for task in tasks:
            t = task[0]
            if Ut(task,Mt[t]) < Ut(task,Mt[t]+[worker]):
                list[w]+=1
    return list

def unused_workers(workers,Mw):
    new_workers = []
    i = 0
    for worker in workers:
        w = worker[0]
        if Mw[w] == None:
            new_workers.append(worker)
    return new_workers

def select_random_task(tasks,size,task_index):
    new_tasks=[]
    indexs = random.sample(task_index,size)
    i = 0
    for element in indexs:
        task = tasks[element]
        #new_tasks.append([i,task[1],task[2],task[3]])
        new_tasks.append(task)
        task_index.remove(element)
        i += 1
    return new_tasks,task_index

# Order tasks of interset of a worker by non increasing value of there rewards
def workerInterest(tasks,rewards):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    L = [[].copy() for w in range(len(rewards))]
    i = 0
    for reward in rewards:
        myreward = reward.copy()
        while (len(myreward)>0):
            '''
            #bad way of doing that if 2 rewards are similare the functino will get the same value of the task twice
            if max(myreward) != 0:
                realIndex = reward.index(max(myreward))
                L[i].append(tasks[realIndex])
                index = myreward.index(max(myreward))
                myreward.pop(index)
            '''
            if max(myreward) != 0:
                index = myreward.index(max(myreward))
                myreward[index] = 0
                L[i].append(tasks[index])
            else: myreward = []
        i = i + 1
    return L

def sorting(workers,L):
    my_workers = [worker for worker in workers]
    my_workers.sort(key=lambda worker: len(L[worker[0]]))
    return my_workers

def copyTasks(tasks):
    newTasks = []
    for t in tasks:
        task = [t[0],t[1].copy(),t[2]]
        newTasks.append(task)
    return newTasks

# convert c_worker_task to c_point_worker
def C_Point_Worker(PoIs):
    c_point_worker = [[0 for w in cWorkerTask] for p in PoIs]
    for w in range(len(cWorkerTask)):
        for t in range(len(cWorkerTask[w])):
            for point in cWorkerTask[w][t]:
                p = point[0][0]
                c_point_worker[p][w] = 1

    return c_point_worker


# utilit only with indexs
def utility(t,set_of_workers_indexs):
    #global cWorkerTask
    points = []
    
    for w in set_of_workers_indexs:
        newListOfPoints = [pt for pt in cWorkerTask[w][t] if pt not in points]


        testPoI = [pt[0][0] for pt in cWorkerTask[w][t] if pt not in points]
        if len(testPoI) > 1 and 1 < (testPoI.count(max(testPoI, key=testPoI.count))):
            print("found!! = ",testPoI.count(max(testPoI, key=testPoI.count)))

        points = points + newListOfPoints
    '''
    testPoI1 = [pt[0][0] for pt in points]
    if len(testPoI1) > 1 and 1 < (testPoI1.count(max(testPoI1, key=testPoI.count))):
        print("found!!xD = ", testPoI1.count(max(testPoI1, key=testPoI1.count)))'''
    utility = 0
    for point in points:

        utility = utility + point[1]
    #if utility > 20 :print("u = ", utility)
    return utility


# utility
def Ut(task,setOfWorkers):
    #global cWorkerTask
    t = task[0]
    points = []
    
    for worker in setOfWorkers:
        w = worker[0]
        newListOfPoints = [pt for pt in cWorkerTask[w][t] if pt not in points]


        testPoI = [pt[0][0] for pt in cWorkerTask[w][t] if pt not in points]
        if len(testPoI) > 1 and 1 < (testPoI.count(max(testPoI, key=testPoI.count))):
            print("found!! = ",testPoI.count(max(testPoI, key=testPoI.count)))

        points = points + newListOfPoints
    '''
    testPoI1 = [pt[0][0] for pt in points]
    if len(testPoI1) > 1 and 1 < (testPoI1.count(max(testPoI1, key=testPoI.count))):
        print("found!!xD = ", testPoI1.count(max(testPoI1, key=testPoI1.count)))'''
    utility = 0
    for point in points:

        utility = utility + point[1]
    #if utility > 20 :print("u = ", utility)
    return utility

# get all set of worker that can do the task t for each task
def UsefulWorker(tasks,workers):
    #global L, indexw, Mw, Mt, xt, nt, zt, Ht, At, cWorkerTask
    S = [[].copy() for i in range(len(tasks))]
    for task in tasks:
        for i in range(len(workers)):
            if len(cWorkerTask[i][task[0]]) != 0:
                # updated : we append the index instead of all worker
                S[task[0]].append(workers[i][0])
    return S


# L1-L2 update : the set of workers are only indexes
def removeSetFromSetWorker(L1,L2):
    L3 = []
    for worker in L1:
        if worker not in L2:
            L3.append(worker)
    return L3

#get all subsets of given size of a set
def subsets(workersSet):
    if workersSet == []:
        return [[]]
    x = subsets(workersSet[1:])
    return x + [[workersSet[0]] + y for y in x]

#get all subsets of given size of a set
def subsetsTwo(workersSet):
    result = []
    for i in range(len(workersSet)):
        result.append([workersSet[i]])
        for j in range(i+1,len(workersSet)):
            result.append([workersSet[i],workersSet[j]])
    return result

#get all subsets of given size of a set
def subsetsThree(workersSet):
    result = []
    for i in range(len(workersSet)):
        #result.append([i])
        for j in range(i+1,len(workersSet)):
            #result.append([i,j])
            for t in range(j + 1, len(workersSet)):
                result.append([workersSet[i], workersSet[j], workersSet[t]])
    return result


#get reward of all workers in the set according to a task
def Rt(task, setOfWoker, rewards):
    rt = 0
    for worker in setOfWoker:
        rt = rt + rewards[worker[0]][task[0]]
    return rt

#get reward of all workers in the set according to a task
def rewardsByWorkers(task, setOfWoker, rewards):
    rt = 0
    for w in setOfWoker:
        rt = rt + rewards[w][task[0]]
    return rt

#compute the remaining budegt in the matching M
def RemainBudget(task, Mt, rewards):
    bt = task[2]
    for worker in Mt[task[0]]:
        bt = bt - rewards[worker[0]][task[0]]
    return bt

def happyWorkerPerTaskOfDegree(i, tasks, workersp, desableWorkers, rewards):
    workers = [w for w in workersp if w[0] not in desableWorkers]
    L = [[] for t in range(len(tasks))]
    workerList = [[] for t in range(len(tasks))]
    workerIndex = [x[0] for x in workers]
    rewardsPrim = [rewards[x[0]].copy() for x in workers]
    xxxxxx = 0
    for w in range(len(rewardsPrim)):

        t = (rewardsPrim[w]).index(max(rewardsPrim[w]))
        for degree in range(i):
            if rewardsPrim[w][t] != 0:
                rewardsPrim[w][t] = 0
                t = (rewardsPrim[w]).index(max(rewardsPrim[w]))
            else:
                break
        if max(rewardsPrim[w]) != 0:
            # L[t].append(w)
            workerList[t].append(workerIndex[w])
    testWorkers = []
    '''
    for setOfw in L:
        for element in setOfw:
            testWorkers.append(element)
    if testWorkers.count(max(testWorkers, key=testWorkers.count)) > 1: print("L = ", testWorkers.count(
        max(testWorkers, key=testWorkers.count)))
    '''
    return workerList

def workerListSatisfactionPerTask(tasks, workers, desableWorkers, rewards):
    L = []

    workersp = [w for w in workers if w[0] not in desableWorkers]
    for i in range(len(tasks)):
        L.append(happyWorkerPerTaskOfDegree(i, tasks, workersp, rewards))
    return L

def tasksListByPreferences(w, t, rewards):
    taskList = []
    rewardsPrime = rewards[w].copy()
    task = rewardsPrime.index(max(rewardsPrime))
    while rewards[w][task] != rewards[w][t] and rewardsPrime[task] != 0:
        taskList.append(task)
        rewardsPrime[task] = 0
        task = rewardsPrime.index(max(rewardsPrime))
    return taskList

def bestWorkerc(t, w, tasks, workers, myMt, rewards):
    L = [worker for worker in workers if rewards[worker[0]][t] != 0]
    wIndex = -1
    maxUtility = Ut(tasks[t], myMt[t]) / totalWeight(tasks[t])
    for worker in L:
        setOfWorker = myMt[t] + [worker]
        if Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
            newMaxUtility = Ut(tasks[t], setOfWorker) / totalWeight(tasks[t])
            if maxUtility < newMaxUtility:
                wIndex = worker[0]
                maxUtility = newMaxUtility
    # can be improved too, because it may be the wIndex and w give the same utility if we add it to myMt and the wIndex was the first add so w will not be taken into account
    # also if both workers give the same utility we will prefer to add the worker that have the maximum reward
    return wIndex == w

def bestWorker(t, w, tasks, workers, myMt, rewards):
    L = [worker for worker in workers if rewards[worker[0]][t] != 0]
    wIndex = -1
    maxUtility = Ut(tasks[t], myMt[t])
    for worker in L:
        setOfWorker = myMt[t] + [worker]
        if Rt(tasks[t], setOfWorker, rewards) <= tasks[t][2]:
            newMaxUtility = Ut(tasks[t], setOfWorker)
            if maxUtility < newMaxUtility:
                wIndex = worker[0]
                maxUtility = newMaxUtility
    # can be improved too, because it may be the wIndex and w give the same utility if we add it to myMt and the wIndex was the first add so w will not be taken into account
    # also if both workers give the same utility we will prefer to add the worker that have the maximum reward
    return wIndex == w

def totalWeight(task):
    coverage = 0
    for point in task[1]:
        coverage = coverage + point[1]
    return coverage

def addMoreWorkerToTasks(tasks, workers, myRwd, myMw, myMt):
    rewards = copy_reward(myRwd)
    Lw = workerInterest(tasks, rewards)
    for w in range(len(Lw)):
        if myMw[w] == None:
            interestList = Lw[w]
            for task in interestList:
                t = task[0]
                benefit = Ut(task, [workers[w]] + myMt[t]) - Ut(task, myMt[t])

                '''    
                old_intersection_points = get_total_intersection(myMt[t], task, cWorkerTask)
                remaining_points = retrieveFromC(cWorkerTask[w][t], old_intersection_points)
                rewards[w][t] = (rewards[w][t] * (getTotalWeightPoint(remaining_points) / Ut(task, [workers[w]]))) / \
                                task[2]
                '''
                # remainBudget = StableMatching.RemainBudget(task,myMt,rewards)
                # if  remainBudget >= rewards[w][task[0]] and benefit > 0:
                current_rewards = copy_reward(rewards)
                rewards = reward_modification(task,myMt[t],[workers[w]],current_rewards,rewards,workers)
                if Rt(task, [workers[w]] + myMt[t], rewards) <= task[2] and benefit > 0:
                    myMt[t].append(workers[w])
                    myMw[w] = task
                    # print("one couple matched : ", (t,w))
                    break

                rewards = rest_rewards(task, [workers[w]], current_rewards, rewards)

        #manyToOne(myMt, "underunderfunction")
        #budegetTest(myMt, tasks, rewards, "underunderfunction")

    return myMt, myMw,rewards

def setOfHappyWorkerPerTask(tasks, workers, rewards):
    L = [[] for t in range(len(tasks))]
    for worker in workers:
        w = worker[0]
        t = (rewards[w]).index(max(rewards[w]))
        if max(rewards[w]) != 0: L[t].append(w)
    # testWorkers = []
    # for setOfw in L:
    #     for element in setOfw:
    #         testWorkers.append(element)

    # if len(testWorkers) == 0 :
    #     print("No matching in algo Greedy")
    # elif testWorkers.count(max(testWorkers, key=testWorkers.count)) > 1: print("L = ", testWorkers.count(
    #     max(testWorkers, key=testWorkers.count)))
    return L

def rwd(i):
    return myRewards[i][taskIndex]

def sortLbyRewards(taskInde, L, rewards):
    global taskIndex, myRewards
    myRewards = rewards
    taskIndex = taskInde
    L.sort(key=rwd)
    return L

def KnapSackp(W, wt, workers, L, task):
    '''
    :param W: capacity of knapsack
    :param wt: list containing weights
    :param workers : all list of workers
    :param L: list of index of the worker taked into account
    :param task : the task taked into account
    :return: Integer
    '''
    dp_table = [[[0, []] for j in range(W + 1)] for i in range(len(wt) + 1)]
    for i in range(1, len(dp_table)):
        for j in range(1, len(dp_table[0])):
            if wt[i - 1] <= j:

                setOfWorkers = []
                setOfWorkers.append(workers[L[i - 1]])
                utility = Ut(task, setOfWorkers)
                # print("set of workers = ", dp_table[i - 1][j - wt[i - 1]][1])
                for element in dp_table[i - 1][j - wt[i - 1]][1]:
                    if element != L[i - 1]:
                        if Ut(task, setOfWorkers + [workers[element]]) != utility:
                            setOfWorkers.append(workers[element])
                            utility = Ut(task, setOfWorkers)
                        # else:
                        # print(element)
                        # print("utlity = ",utility)
                dp_table[i][j][0] = max(Ut(task, setOfWorkers), dp_table[i - 1][j][0])

                if dp_table[i][j][0] != dp_table[i - 1][j][0]:
                    dp_table[i][j][1] = (dp_table[i - 1][j - wt[i - 1]][1] + [L[i - 1]]).copy()
                else:
                    dp_table[i][j][1] = dp_table[i - 1][j][1].copy()
            elif wt[i - 1] > j:
                dp_table[i][j][0] = dp_table[i - 1][j][0]
                dp_table[i][j][1] = dp_table[i - 1][j][1].copy()

    return dp_table[-1][-1]

def reward_modification(task, set_of_worker, set_of_worker_of_interest, rewards, new_rewards,workers):
    return rewards

    t = task[0]
    for worker in set_of_worker_of_interest:
        w = worker[0]
        old_intersection_points = get_total_intersection(set_of_worker, task, cWorkerTask)
        remaining_points = retrieveFromC(cWorkerTask[w][t], old_intersection_points)
        new_rewards[w][t] = (rewards[w][t] * (getTotalWeightPoint(remaining_points) / Ut(task, [workers[w]])))

        #new_rewards[w][t] = (rewards[w][t] * (getTotalWeightPoint(remaining_points) / Ut(task, [workers[w]]))) / task[2]

    return copy_reward(new_rewards)

    return rewards

def rest_rewards(task, set_of_worker, rewards, new_rewards):
    return rewards

    t = task[0]
    for worker in set_of_worker:
        w = worker[0]
        new_rewards[w][t] = rewards[w][t]

    return copy_reward(new_rewards)

    return rewards

def info(Mt,Mw,rewards,tasks,workers):
    remainingcwt = [[] for _ in workers]
    remainingPoIs = []
    remainingbudget = []
    for t in range(len(Mt)):
        task = tasks[t]
        old_intersection_points = get_total_intersection(Mt[t], task, cWorkerTask)
        for worker in workers:
            w = worker[0]
            remainingcwt[w].append(retrieveFromC(cWorkerTask[w][t], old_intersection_points))

        remainingPoIs.append(retrieveFromC(task[1], old_intersection_points))
        remainingbudget.append(task[2]-Rt(tasks[t], Mt[t], rewards))
    return remainingcwt,remainingPoIs,remainingbudget,Mw,rewards

def compute_averge_worker_per_point(tasks_list,path,data_path):

    workers = read_Data_Set(path)
    AllPoI, AllCworkersp = readPoIandCworkers(data_path)
    PoI = indexPoI(AllPoI)
    Cworkers = ComputeCworkers(PoI, workers)
    average_worker_points = []
    ecart_type = []
    for n in tasks_list:
        tasks = generateTasks(n, PoI, 0)
        cwt, cwtp = CworkerTask(tasks, workers, Cworkers)

        c_worker_point = get_c_worker_point(PoI)
        list_of_importance = get_list_of_point_by_importance(c_worker_point)
        # print(list_of_importance)
        average_worker_points.append(sum(list_of_importance)/len(list_of_importance))
        ecart_type.append(np.std(list_of_importance))

    plt.errorbar(tasks_list, average_worker_points, yerr=ecart_type, xerr=None, fmt='o-')
    plt.xlabel('# of task (n)')
    plt.ylabel('Average number of worker covering per point')
    plt.title('Average number of worker covering per point')
    plt.ylim(-1.25, 7)
    #plt.xlim(0, 50)
    plt.show()

def mean(L):
    return(sum(L)/len(L))
def SEWAM(a,b,n,e):
    L = []
    mean_a_b = (a+b)/2
    L.append(np.random.uniform(10,100,1)[0])
    for i in range(1,n):
        diff = mean_a_b - mean(L)
        if abs(diff) > e or i == n-1:
            mu = mean_a_b + diff
            std = diff
            x = np.random.normal(mu,abs(std),1)[0]
            while x > 100 or x < 10:
                x = np.random.normal(mu,abs(std),1)[0]
            L.append(x)
        else:
            x = np.random.uniform(10, 100, 1)[0]
            while x > 100 or x < 10:
                x = np.random.uniform(10, 100, 1)[0]
            L.append(x)
        # dist = stats.truncnorm(a,b,mu,abs(std))
        # L.append(dist.rvs())
    return L