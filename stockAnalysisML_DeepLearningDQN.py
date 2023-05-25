import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import chainer
import chainer.functions as F
import chainer.links as L
import copy
import time
import datetime
from plotly.subplots import make_subplots
from plotly.graph_objs import *
from plotly.offline import init_notebook_mode, iplot, iplot_mpl

#init_notebook_mode()
# Define the ticker symbols of the stocks you want to analyze
ticker_symbols = ['NVDA']
#ticker_symbols = ['COST', 'MSFT', 'PYPL', 'PG', 'UNH', 'V', 'WMT', 'DIS', 'NFLX', 'NVDA' ]
#ticker_symbols  = ['AAPL', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMZN', 'BAC', 'BMY', 'CMCSA', 'COST', 'CSCO', 'CRM', 'CVX', 'DHR', 'DIS', 'GOOGL', 'HD', 'HON', 'INTC', 'JNJ', 'JPM', 'KO', 'LIN', 'LLY', 'MA', 'MCD', 'MMM', 'MRK', 'MSFT', 'NEE', 'NFLX', 'NVDA', 'NKE', 'ORCL', 'PFE', 'PEP', 'PG', 'PM', 'PYPL', 'T', 'TMO', 'TSLA', 'UNH', 'UNP', 'V', 'VZ', 'WMT', 'XOM']
#ticker_symbols = ['BTC-USD', 'ETH-USD', 'DOGE-USD', 'USDT-USD', 'ADA-USD', 'BNB-USD', 'XRP-USD']
train_data_start_date  = '2015-05-01'
test_data_start_date  = '2021-11-01'

class Environment1:
    
    def __init__(self, data, history_t=90):
        self.data = data
        self.history_t = history_t
        self.reset()
        
    def reset(self):
        self.t = 0
        self.done = False
        self.profits = 0
        self.positions = []
        self.position_value = 0
        self.history = [0 for _ in range(self.history_t)]
        return [self.position_value] + self.history # obs
    
    def step(self, act):
        reward = 0
        
        # act = 0: stay, 1: buy, 2: sell
        if act == 1:
            self.positions.append(self.data.iloc[self.t, :]['Close'])
        elif act == 2: # sell
            if len(self.positions) == 0:
                reward = -1
            else:
                profits = 0
                for p in self.positions:
                    profits += (self.data.iloc[self.t, :]['Close'] - p)
                reward += profits
                self.profits += profits
                self.positions = []
        
        # set next time
        self.t += 1
        self.position_value = 0
        for p in self.positions:
            self.position_value += (self.data.iloc[self.t, :]['Close'] - p)
        self.history.pop(0)
        self.history.append(self.data.iloc[self.t, :]['Close'] - self.data.iloc[(self.t-1), :]['Close'])
        
        # clipping reward
        if reward > 0:
            reward = 1
        elif reward < 0:
            reward = -1
        
        return [self.position_value] + self.history, reward, self.done # obs, reward, done

#This line of code calls the plot_loss_reward() function with total_losses and total_rewards as arguments. 
#These variables represent the losses and rewards obtained during the training process of the DQN agent.
#The plot_loss_reward() function creates a visual representation of the losses and rewards across training epochs using Plotly.
# By calling this function, a 1x2 subplot figure is displayed, 
# where the first subplot shows the losses and the second subplot shows the rewards as line plots over the epochs. 
# This visualization helps in assessing the performance of the DQN agent by observing how the losses and rewards change throughout the training process.
def plot_train_test_by_q(train_env, test_env, Q, algorithm_name, ticker):
    print("Ploting graph for Train / Test by Q - " + ticker + " at " +  str(datetime.datetime.now()) + " ...")
    # train
    pobs = train_env.reset()
    train_acts = []
    train_rewards = []

    for _ in range(len(train_env.data)-1):
        
        pact = Q(np.array(pobs, dtype=np.float32).reshape(1, -1))
        pact = np.argmax(pact.data)
        train_acts.append(pact)
            
        obs, reward, done = train_env.step(pact)
        train_rewards.append(reward)

        pobs = obs
        
    train_profits = train_env.profits
    
    # test
    pobs = test_env.reset()
    test_acts = []
    test_rewards = []
    optimal_action_printed = False

    print("Optimal solution by Q - " + ticker + " ...")
    for _ in range(len(test_env.data)-1):
    
        pact = Q(np.array(pobs, dtype=np.float32).reshape(1, -1))
        pact = np.argmax(pact.data)
        test_acts.append(pact)
            
        obs, reward, done = test_env.step(pact)
        test_rewards.append(reward)

        if not optimal_action_printed:
            print(f"Action: {'Stay' if pact == 0 else 'Buy' if pact == 1 else 'Sell'}, Price: {test_env.data.iloc[test_env.t, :]['Close']}, Date: {test_env.data.index[test_env.t]}")            
        pobs = obs
    optimal_action_printed = True
    print("Optimal solution by Q - " + ticker + " ... DONE")    
    test_profits = test_env.profits
    
    # plot
    train_copy = train_env.data.copy()
    test_copy = test_env.data.copy()
    train_copy['act'] = train_acts + [np.nan]
    train_copy['reward'] = train_rewards + [np.nan]
    test_copy['act'] = test_acts + [np.nan]
    test_copy['reward'] = test_rewards + [np.nan]
    train0 = train_copy[train_copy['act'] == 0]
    train1 = train_copy[train_copy['act'] == 1]
    train2 = train_copy[train_copy['act'] == 2]
    test0 = test_copy[test_copy['act'] == 0]
    test1 = test_copy[test_copy['act'] == 1]
    test2 = test_copy[test_copy['act'] == 2]
    act_color0, act_color1, act_color2 = 'gray', 'cyan', 'magenta'

    data = [
        Candlestick(x=train0.index, open=train0['Open'], high=train0['High'], low=train0['Low'], close=train0['Close'], increasing=dict(line=dict(color=act_color0)), decreasing=dict(line=dict(color=act_color0))),
        Candlestick(x=train1.index, open=train1['Open'], high=train1['High'], low=train1['Low'], close=train1['Close'], increasing=dict(line=dict(color=act_color1)), decreasing=dict(line=dict(color=act_color1))),
        Candlestick(x=train2.index, open=train2['Open'], high=train2['High'], low=train2['Low'], close=train2['Close'], increasing=dict(line=dict(color=act_color2)), decreasing=dict(line=dict(color=act_color2))),
        Candlestick(x=test0.index, open=test0['Open'], high=test0['High'], low=test0['Low'], close=test0['Close'], increasing=dict(line=dict(color=act_color0)), decreasing=dict(line=dict(color=act_color0))),
        Candlestick(x=test1.index, open=test1['Open'], high=test1['High'], low=test1['Low'], close=test1['Close'], increasing=dict(line=dict(color=act_color1)), decreasing=dict(line=dict(color=act_color1))),
        Candlestick(x=test2.index, open=test2['Open'], high=test2['High'], low=test2['Low'], close=test2['Close'], increasing=dict(line=dict(color=act_color2)), decreasing=dict(line=dict(color=act_color2)))
    ]
    title = '[{}] train s-reward: {}, profits: {}, test s-reward: {}, profits: {}, symbol: {}'.format(
        algorithm_name,
        int(sum(train_rewards)),
        int(train_profits),
        int(sum(test_rewards)),
        int(test_profits),
        ticker
    )
    layout = {
        'title': title,
        'showlegend': False,
         'shapes': [
             {'x0': test_data_start_date , 'x1': test_data_start_date , 'y0': 0, 'y1': 1, 'xref': 'x', 'yref': 'paper', 'line': {'color': 'rgb(0,0,0)', 'width': 1}}
         ],
        'annotations': [
            {'x': test_data_start_date , 'y': 1.0, 'xref': 'x', 'yref': 'paper', 'showarrow': False, 'xanchor': 'left', 'text': ' test data'},
            {'x': test_data_start_date , 'y': 1.0, 'xref': 'x', 'yref': 'paper', 'showarrow': False, 'xanchor': 'right', 'text': 'train data '}
        ]
    }
    figure = Figure(data=data, layout=layout)
    iplot(figure)
    print("Ploting graph for Train / Test by Q - " + ticker + " at " +  str(datetime.datetime.now()) +" ... DONE")

# Plot loss reward
# This code defines a function called plot_loss_reward, which takes two arguments: total_losses and total_rewards.
# These represent the losses and rewards obtained during the training process of a DQN agent, respectively.
# The purpose of this function is to create a visual representation of these losses and rewards across training epochs using subplots.make_subplots,
# a popular Python graphing library.
def plot_loss_reward(total_losses, total_rewards, ticker):
    print("Ploting graph for Loss reward - " + ticker + " at " +  str(datetime.datetime.now()) +  " ...")
    figure = make_subplots(rows=1, cols=2, subplot_titles=('loss', 'reward'), print_grid=False)
    figure.append_trace(Scatter(y=total_losses, mode='lines', line=dict(color='skyblue')), 1, 1)
    figure.append_trace(Scatter(y=total_rewards, mode='lines', line=dict(color='orange')), 1, 2)
    figure['layout']['xaxis1'].update(title='epoch')
    figure['layout']['xaxis2'].update(title='epoch')
    figure['layout'].update(height=400, width=900, showlegend=False)
    figure['layout'].update(title='Loss reward for ' + ticker)
    iplot(figure)
    print("Ploting graph for Loss reward - " + ticker + " at " +  str(datetime.datetime.now()) + " ...DONE")

# Deep Q-Network Training
def train_dqn(env):

    class Q_Network(chainer.Chain):

        def __init__(self, input_size, hidden_size, output_size):
            super(Q_Network, self).__init__(
                fc1 = L.Linear(input_size, hidden_size),
                fc2 = L.Linear(hidden_size, hidden_size),
                fc3 = L.Linear(hidden_size, output_size)
            )

        def __call__(self, x):
            h = F.relu(self.fc1(x))
            h = F.relu(self.fc2(h))
            y = self.fc3(h)
            return y

        def reset(self):
            self.zerograds()

    Q = Q_Network(input_size=env.history_t+1, hidden_size=100, output_size=3)
    Q_ast = copy.deepcopy(Q)
    optimizer = chainer.optimizers.Adam()
    optimizer.setup(Q)

    epoch_num = 50
    step_max = len(env.data)-1
    memory_size = 200
    batch_size = 20
    epsilon = 1.0
    epsilon_decrease = 1e-3
    epsilon_min = 0.1
    start_reduce_epsilon = 200
    train_freq = 10
    update_q_freq = 20
    gamma = 0.97
    show_log_freq = 5

    memory = []
    total_step = 0
    total_rewards = []
    total_losses = []

    start = time.time()
    print("Training DQN starts at ", datetime.datetime.now())
    print("Total number of iterations for training: ", epoch_num) 
    for epoch in range(epoch_num):

        pobs = env.reset()
        step = 0
        done = False
        total_reward = 0
        total_loss = 0

        while not done and step < step_max:

            # select act
            pact = np.random.randint(3)
            if np.random.rand() > epsilon:
                pact = Q(np.array(pobs, dtype=np.float32).reshape(1, -1))
                pact = np.argmax(pact.data)
            # act
            obs, reward, done = env.step(pact)

            # add memory
            memory.append((pobs, pact, reward, obs, done))
            if len(memory) > memory_size:
                memory.pop(0)

            # train or update q
            if len(memory) == memory_size:
                if total_step % train_freq == 0:
                    shuffled_memory = np.random.permutation(np.array(memory, dtype=object))
                    memory_idx = range(len(shuffled_memory))
                    for i in memory_idx[::batch_size]:
                        batch = shuffled_memory[i:i+batch_size]
                        b_pobs = np.array(batch[:, 0].tolist(), dtype=np.float32).reshape(batch_size, -1)
                        b_pact = np.array(batch[:, 1].tolist(), dtype=np.int32)
                        b_reward = np.array(batch[:, 2].tolist(), dtype=np.int32)
                        b_obs = np.array(batch[:, 3].tolist(), dtype=np.float32).reshape(batch_size, -1)
                        b_done = np.array(batch[:, 4].tolist(), dtype=bool)

                        q = Q(b_pobs)
                        maxq = np.max(Q_ast(b_obs).data, axis=1)
                        target = copy.deepcopy(q.data).reshape(batch_size, -1)
                        for j in range(batch_size):
                            target[j, b_pact[j]] = b_reward[j] + gamma * maxq[j] * (not b_done[j])
                        Q.reset()
                        loss = F.mean_squared_error(q, target)
                        total_loss += loss.data
                        loss.backward()
                        optimizer.update()

                if total_step % update_q_freq == 0:
                    Q_ast = copy.deepcopy(Q)

            # epsilon
            if epsilon > epsilon_min and total_step > start_reduce_epsilon:
                epsilon -= epsilon_decrease

            # next step
            total_reward += reward
            pobs = obs
            step += 1
            total_step += 1

        total_rewards.append(total_reward)
        total_losses.append(total_loss)

        if (epoch+1) % show_log_freq == 0:
            log_reward = sum(total_rewards[((epoch+1)-show_log_freq):]) / show_log_freq
            log_loss = sum(total_losses[((epoch+1)-show_log_freq):]) / show_log_freq
            elapsed_time = time.time() - start
            print('\t'.join(map(str, [epoch+1, epsilon, total_step, log_reward, log_loss, elapsed_time])))
            start = time.time()
    
    print("Training DQN finished at ", datetime.datetime.now())
    return Q, total_losses, total_rewards

def plot_train_test(train_data, test_data, test_data_start_date ):
    
    data = [
        Candlestick(x=train_data.index, open=train_data['Open'], high=train_data['High'], low=train_data['Low'], close=train_data['Close'], name='train_data'),
        Candlestick(x=test_data.index, open=test_data['Open'], high=test_data['High'], low=test_data['Low'], close=test_data['Close'], name='test_data')
    ]
    layout = {
         'shapes': [
             {'x0': test_data_start_date , 'x1': test_data_start_date , 'y0': 0, 'y1': 1, 'xref': 'x', 'yref': 'paper', 'line': {'color': 'rgb(0,0,0)', 'width': 1}}
         ],
        'annotations': [
            {'x': test_data_start_date , 'y': 1.0, 'xref': 'x', 'yref': 'paper', 'showarrow': False, 'xanchor': 'left', 'text': ' test data'},
            {'x': test_data_start_date , 'y': 1.0, 'xref': 'x', 'yref': 'paper', 'showarrow': False, 'xanchor': 'right', 'text': 'train data '}
        ]
    }
    figure = Figure(data=data, layout=layout)
    iplot(figure)



# Iterate through the ticker symbols and download historical data
for ticker in ticker_symbols:
    # Download historical data for the current ticker
    data = yf.download(ticker, start=train_data_start_date )
    #print(data.tail())
    # Data is split in an 80:20 ratio, with 80% used for training and 20% for testing
    #train_data, test_data = data[0:int(len(data)*0.8)], data[int(len(data)*0.8):]

    train_data = data[:test_data_start_date ]
    test_data = data[test_data_start_date :]
    #print("train data size:", len(train_data))
    #print("test data size:", len(test_data))
    #print(data.tail())
    #plot_train_test(train_data, test_data, test_data_start_date )

    
    env = Environment1(train_data)
    print(env.reset())
    for _ in range(3):
        pact = np.random.randint(3)
        print(env.step(pact))

    Q, total_losses, total_rewards = train_dqn(Environment1(train_data))
    plot_loss_reward(total_losses, total_rewards, ticker)

    plot_train_test_by_q(Environment1(train_data), Environment1(test_data), Q, 'DQN', ticker)
    print("Done.")