import matplotlib.pyplot as plt
import numpy as np


def sorted_barplot(P, W, ATP_top_players, title, color, empirical_worst_players=None, diff=False, P2=None):
    """
    Function for making a sorted bar plot based on values in P, and labelling the plot with the
    corresponding names
    :param P: An array of length num_players (107)
    :param W: Array containing names of each player
    :return: None
    """
    M = len(P)
    xx = np.linspace(0, M, M)
    plt.figure(figsize=(11, 30))
    sorted_indices = np.argsort(P)
    sorted_names = W[sorted_indices]
    plt.barh(xx, P[sorted_indices], color=color)
    
    if diff:
        sorted_indices2 = np.argsort(P2)
        sorted_names2 = W[sorted_indices2]
        bLabel = False
        for j in range(M):
            if sorted_names[j] != sorted_names2[j]:
                if not bLabel:
                    plt.barh(xx[j], P[sorted_indices][j], color='yellow', label = 'players ranked\ndifferently\nin Gibbs')
                    bLabel = True
                else:
                    plt.barh(xx[j], P[sorted_indices][j], color='yellow')
    
    colors = ['blue', 'orange', 'green', 'red']
    for i, p in enumerate(ATP_top_players):
        pos = np.where(sorted_names == W[p][0])[0]
        plt.barh(xx[pos], P[sorted_indices][pos], color=colors[i], label = W[p][0])
                

    if empirical_worst_players is not None:
        for i, name in enumerate(empirical_worst_players):
            pos = np.where(sorted_names == name)[0]
            if i == 0:
                plt.barh(xx[pos], P[sorted_indices][pos], color='purple', label = 'players who\nhave lost all\ntheir games')
            else:
                plt.barh(xx[pos], P[sorted_indices][pos], color='purple')
    
    
    
    plt.yticks(np.linspace(0, M, M), labels=sorted_names[:, 0])
    plt.ylim([-2, 109])
    plt.title(title, fontsize=30)
    plt.legend(loc='lower right', prop={'size': 30})
#     plt.show()
    

