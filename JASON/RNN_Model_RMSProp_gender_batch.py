import theano
import theano.tensor as T
import numpy as np
import sys
from itertools import izip
import time
import cPickle
from  output48_39 import *
from random import randrange
import pdb
__author__= 'JasonWu'

# Number of units in the hidden (recurrent) layer
N_HIDDEN = 128
# input
N_INPUT = 49 # 48 + 1 (male = 1, female = 0)
# output
N_OUTPUT = 48
#mini batch
batch_num = 128
#sentence max length
len_max = 777

x_seq = T.ftensor3()
x_seq_1 = T.matrix()
y_hat = T.ftensor3()
mask = T.ftensor3()
start = T.scalar()
PARM = T.matrix()
'''
#################### LOAD PARAMETER #################
parm_data = file('parameter_RNN_1105.txt','rb')
parm = cPickle.load(parm_data)
Wi = parm[0] 
bh = parm[1] 
Wo = parm[2] 
bo = parm[3] 
Wh = parm[4] 
'''

Wi = theano.shared( np.random.randn(N_INPUT,N_HIDDEN) )
bh = np.zeros(N_HIDDEN)
bh = theano.shared( np.tile(bh,(batch_num, 1)) )
Wo = theano.shared( np.random.randn(N_HIDDEN,N_OUTPUT))
bo = np.zeros(N_OUTPUT)
bo = theano.shared( np.tile(bo,(batch_num, 1)) )
Wh = theano.shared( np.zeros( (N_HIDDEN,N_HIDDEN)  ) )

#sigma = theano.shared(np.random.randn(N_INPUT,N_HIDDEN) )
#Wi = theano.shared( np.random.normal(0, 0.1, (N_INPUT,N_HIDDEN)) )
#Wo = theano.shared( np.random.normal(0, 0.1, (N_HIDDEN,N_OUTPUT)) )
parameters = [Wi,bh,Wo,bo,Wh]

a_0 = np.zeros(N_HIDDEN)
a_0 = theano.shared( np.tile(a_0,(batch_num,1)) )
y_0 = np.zeros(N_OUTPUT)
y_0 = theano.shared( np.tile(y_0,(batch_num,1)) )

def sigmoid(z):
    return 1/(1+T.exp(-z))

def step(x_t,a_tm1,y_tm1):
        a_t = sigmoid( T.dot(x_t,Wi) + T.dot(a_tm1,Wh) + bh )
        y_t = T.dot(a_t,Wo) + bo
        return a_t, y_t

def step_1(x_t_1,a_tm1_1,y_tm1_1):
        a_t = sigmoid( T.dot(x_t_1[0],Wi) + T.dot(a_tm1_1[0],Wh) + bh[0] )
        y_t = T.dot(a_t,Wo) + bo[0]
        return a_t, y_t

[a_seq,y_seq],_ = theano.scan(
                        step,
                        sequences = x_seq,
                        outputs_info = [ a_0, y_0 ],
                        truncate_gradient=-1
                )

[a_seq_1,y_seq_1],_ = theano.scan(
                        step_1,
                        sequences = x_seq_1,
                        outputs_info = [ a_0, y_0 ],
                        truncate_gradient=-1
                )


y_seq_modify =  (y_seq*mask) 
cost = (( y_seq_modify - y_hat )**2 ).sum() / batch_num

#y_seq_modify_1 = (y_seq.T*mask).T 
#y_seq_modify = (T.exp(y_seq_modify_1).T/ T.sum( T.exp(y_seq_modify_1) , axis=1)).T
#cost = -1*((T.log(y_seq_modify)*y_hat).sum())
#y_seq_modify = (y_seq.T*mask).T 
#cost = T.sum( ( y_seq_modify - y_hat )**2 ) 

def RMSprop(cost, params, lr=0.001, rho=0.9, epsilon=1e-6):
    grads = T.grad(cost=cost, wrt=params)
    updates = []
    for p, g in zip(params, grads):
        acc = theano.shared(p.get_value() * 0.)
        #print acc.get_value()
        acc_new = rho * acc + (1 - rho) * g ** 2
        gradient_scaling = T.sqrt(acc_new + epsilon)
        g = g / gradient_scaling
        updates.append((acc, acc_new))
        updates.append((p, p - lr * g))
    return updates

rnn_test_cost = theano.function(
        inputs= [x_seq,y_hat,mask],
        outputs = cost
)

rnn_test_y_evaluate = theano.function(
        inputs= [x_seq_1],
        outputs = y_seq_1
)

rnn_test_parm = theano.function(
        inputs= [],
        outputs = [Wi,bh,Wo,bo,Wh]
)

rnn_train_test = theano.function(
        inputs=[x_seq,y_hat,mask],
        outputs=cost,
        updates=RMSprop(cost, parameters, lr=0.001, rho=0.9, epsilon=1e-6)
)

def float_convert(i):
    try: 
        return np.float32(i)
    except ValueError :
        return i

######################################################## testbench part ##########################################

f = open('DNN_softmax.txt','r')
ans_data = open('answer_map.txt','r')

f_DNNsoft = []
name = []
for line in f:
    input_x = line.split()
    input_x = [float_convert(i) for i in input_x]
    name_x = input_x[0].split('_')
    name.append(name_x)
    f_DNNsoft.append(input_x)
ans = []
for line in ans_data:
    ans_x = line.split(',')
    ans.append(ans_x[1])
wav_end=[]
for i in range( len(name) ):
    if i != len(name)-1:
        if int(name[i][2])+1 != int(name[i+1][2]):
            wav_end.append(i)
    else:
        wav_end.append(i)
wav_start = []
for i in range( len(name) ):
    if int(name[i][2]) == 1:
        wav_start.append(i)
sentence_number = len(wav_start)
run_time = sentence_number/batch_num

anstype = ["aa", "ae", "ah", "ao", "aw", "ax", "ay", "b", "ch", "cl", "d", "dh", "dx", "eh", "el"
               , "en", "epi", "er", "ey", "f", "g", "hh", "ih", "ix", "iy", "jh", "k", "l", "m", "ng"
               , "n", "ow", "oy", "p", "r", "sh", "sil", "s", "th", "t", "uh", "uw", "vcl", "v", "w"
               , "y", "zh", "z"]

train_number = 1091215 #1124823
validation_num = 1124823-1091215

len_max = 777

c = MAP()
ACC = 0.0
epoch=0
mask = []
i=0
epoch_counter = 0
start=1

try:
    while True:
        X = []
        Y= [] 
        count777 = 0
        
        if i>=run_time:#i>=1124823:
            i=0
            epoch = 1

        num = []
        count_len = []
        flag_wav_end = []
        wav_len = []
        for rand_num in range(batch_num):
            num.append ( randrange(0,sentence_number) )
            count_len.append( 0 ) 
            flag_wav_end.append(0)
            wav_len.append(0)

        while(count777<len_max):
            X_batch = []
            Y_batch = []
            for bi in range(batch_num):
                now_i = wav_start[num[bi]]
                if( (count_len[bi]+now_i) in wav_end):
                    if flag_wav_end[bi]==0:
                        flag_wav_end[bi] = 1
                        if(name[count_len[bi]+now_i][0][0] == 'f'):
                            X_batch.append(np.array([0]+f_DNNsoft[count_len[bi]+now_i][1:49]))
                        else:
                            X_batch.append(np.array([1]+f_DNNsoft[count_len[bi]+now_i][1:49]))
                        typeidx = anstype.index(str(ans[count_len[bi]+now_i].split('\n')[0]))                
                        y=[0]*48
                        y[typeidx]=1
                        Y_batch.append(y)
                        wav_len[bi] = count_len[bi]
                    else:
                        y=[0]*48
                        yy = [0]*49
                        Y_batch.append(y)
                        X_batch.append(yy)
                else:
                    if(name[count_len[bi]+now_i][0][0] == 'f'):
                        X_batch.append(np.array([0]+f_DNNsoft[count_len[bi]+now_i][1:49]))
                    else:
                        X_batch.append(np.array([1]+f_DNNsoft[count_len[bi]+now_i][1:49]))
                    typeidx = anstype.index(str(ans[count_len[bi]+now_i].split('\n')[0]))                
                    y=[0]*48
                    y[typeidx]=1
                    Y_batch.append(y)
                    count_len[bi] = count_len[bi]+1

            X.append(X_batch)
            Y.append(Y_batch)
            count777 = count777+1

        i=i+1
        #print i 
        mask_1 = []
        for mask_i in range(batch_num):
            mask_1.append( np.ones(wav_len[mask_i]).tolist()+np.zeros(len_max-wav_len[mask_i]).tolist() )
        mask_1 = np.array(mask_1).T

        mask=[]
        for ii in range(len_max):
            mask_2=np.tile(mask_1[ii],(N_OUTPUT,1))
            mask_2 = mask_2.T
            mask.append(mask_2)

        rnn_train_test(X,Y,mask)
        print 'cost = ',rnn_test_cost(X,Y,mask)

        ######################### check for one epoch #########################
        
        if epoch==1:
            epoch_counter = epoch_counter+1
            print 'epoch_counter',epoch_counter
            print "COST = ", rnn_test_cost(X,Y,mask)
            #print rnn_test_parm()
            err=0.0
            m=0
            test_index=0
            first = 1
            
            while(m<validation_num):
                X_test=[]
                Y_test=[]
                flag_data_end_test = 0
                flag_wav_end_test = 0
                count777_test = 0
                wave_lengh = 0
                while (count777_test<777) :
                    if(m==validation_num-1):
                        if(flag_data_end_test==0):
                            typeidx = anstype.index(str(ans[train_number+m].split('\n')[0]))
                            y=[0]*48
                            y[typeidx]=1
                            Y_test.append(y)
                            if(name[m][0][0] == 'f'):
                                X_test.append(np.array([0]+f_DNNsoft[train_number+m][1:49]))
                            else:
                                X_test.append(np.array([1]+f_DNNsoft[train_number+m][1:49]))
                            flag_data_end_test = 1
                            wave_lengh = int(name[train_number+m][2])
                        else:
                            y=[0]*48
                            yy= [0]*49
                            Y_test.append(y)
                            X_test.append(yy)
                    else:
                        if(name[train_number+m][0]==name[train_number+m+1][0] and name[train_number+m][1]==name[train_number+m+1][1]) :
                            typeidx = anstype.index(str(ans[train_number+m].split('\n')[0]))
                            y=[0]*48
                            y[typeidx]=1
                            Y_test.append(y)
                            if(name[m][0][0] == 'f'):
                                X_test.append(np.array([0]+f_DNNsoft[train_number+m][1:49]))
                            else:
                                X_test.append(np.array([1]+f_DNNsoft[train_number+m][1:49]))
                            m=m+1
                        else: 
                            if(flag_wav_end_test==0):
                                typeidx = anstype.index(str(ans[train_number+m].split('\n')[0]))
                                y=[0]*48
                                y[typeidx]=1
                                Y_test.append(y)
                                if(name[m][0][0] == 'f'):
                                    X_test.append(np.array([0]+f_DNNsoft[train_number+m][1:49]))
                                else:
                                    X_test.append(np.array([1]+f_DNNsoft[train_number+m][1:49]))
                                flag_wav_end_test = 1
                                wave_lengh = int(name[train_number+m][2])
                            else:
                                y=[0]*48
                                yy = [0]*49
                                Y_test.append(y)
                                X_test.append(yy)
                    count777_test = count777_test+1;
                if ((m+train_number) not in wav_end):
                    print "FUCKING TWO!!!!"
                    print 'm' ,m
                if (len(X_test)!=777 or len(Y_test)!=777):
                    print 'len wrong!!'

                m=m+1
                Ya = rnn_test_y_evaluate(X)
                for index in range(wave_lengh):
                    if( c.map(Ya[index]) !=  str(ans[train_number+test_index+index].split('\n')[0]) ):
                        err = err+1
                test_index = test_index+wave_lengh
            
            print 'err',err
            ACC = 1.0-err/validation_num
            print 'ACC = %f'%(ACC)
            epoch = 0
            counter = 0
            
        ######################### check for one epoch #########################

except KeyboardInterrupt:
    pass
    '''
err = 0.0
for index in range(474):
    #print 'Ya[index]',Ya[index]

    #print 'c.map(Ya[index])',c.map(Ya[index])
    #print Ya[index]
    #print 'ANS',str(ans[index].split('\n')[0])
    if( c.map(Ya[index]) !=  str(ans[index].split('\n')[0]) ):
        err = err+1.0
print 1-(err / 477.0)
'''
f.close()
ans_data.close()

f_P = file('parameter_RNN_1107.txt', 'wb')
cPickle.dump(parameters, f_P, protocol=cPickle.HIGHEST_PROTOCOL)
f_P.close()
'''
######################## test ############################
parm_data = file('parameter_W_RNN.txt','rb')
parm = cPickle.load(parm_data)
load_parm(parm)

test_ans = open('RNN_test_ans_1102.csv','w')


test_c = MAP()
Y=None
m=0
test_index=0
test_ans.write('Id,Prediction\n')
while(m<validation_num):
    X_test=[]
    Y_test=[]
    flag_data_end_test = 0
    flag_wav_end_test = 0
    count777_test = 0
    wave_lengh = 0;
    while (count777_test<777) :
        if(m==validation_num-1):
            if(flag_data_end_test==0):
                typeidx = anstype.index(str(ans[train_number+m].split('\n')[0]))
                y=[0]*48
                y[typeidx]=1
                Y_test.append(y)
                X_test.append(f_DNNsoft[train_number+m][1:49])
                flag_data_end_test = 1
                wave_lengh = int(name[train_number+m][2])
            else:
                y=[0]*48
                Y_test.append(y)
                X_test.append(y)
        else:
            if(name[train_number+m][0]==name[train_number+m+1][0] and name[train_number+m][1]==name[train_number+m+1][1]) :
                typeidx = anstype.index(str(ans[train_number+m].split('\n')[0]))
                y=[0]*48
                y[typeidx]=1
                Y_test.append(y)
                X_test.append(f_DNNsoft[train_number+m][1:49])
                m=m+1
            else: 
                if(flag_wav_end_test==0):
                    typeidx = anstype.index(str(ans[train_number+m].split('\n')[0]))
                    y=[0]*48
                    y[typeidx]=1
                    Y_test.append(y)
                    X_test.append(f_DNNsoft[train_number+m][1:49])
                    flag_wav_end_test = 1
                    wave_lengh = int(name[train_number+m][2])
                else:
                    y=[0]*48
                    Y_test.append(y)
                    X_test.append(y)
        count777_test = count777_test+1;
    m=m+1
    Ya = rnn_test_y_evaluate(X)
    for index in range(wave_lengh):
        test_ans.write(f_DNNsoft[train_number+test_index+index][0])
        test_ans.write(',')
        test_ans.write(test_c.map(Ya[index],1).split('\n')[0])
        if m!=validation_num-1-1:
            test_ans.write('\n')
    test_index = test_index+wave_lengh

'''