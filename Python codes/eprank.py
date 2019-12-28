from scipy.stats import norm
import numpy as np


def eprank(G, M, num_iters):
    """

    :param G: Game outcomes
    :param M: number of players
    :param num_iters: number of iterations of message passing
    :return: mean and precisions for each players skills based on message passing
    """
    
    Ms_series = np.zeros((M, num_iters))
    Ps_series = np.zeros((M, num_iters))
    
    
    # number of games
    N = G.shape[0]

    # prior skill variance (prior mean is always 0)
    pv = 0.5

    # Helper functions - these will be used to approximate the marginal dist of tg via moment matching.
    psi = lambda x: norm.pdf(x)/norm.cdf(x)     # psi() will be used to compute mu_g_squiggle.
    lam = lambda x: psi(x) * (psi(x) + x)       # lam() will be used to compute nu_g_squiggle.

    # intialize marginal means and precisions
    Ms = np.zeros(M)
    Ps = np.zeros(M)

    # initialize matrices of game-to-skill messages, means and precisions
    Mgs = np.zeros((N, 2))
    Pgs = np.zeros((N, 2))

    # initialize matrices of skill-to-game messages, means and precisions
    Msg = np.zeros((N, 2))
    Psg = np.zeros((N, 2))

    for i in range(num_iters):
        for p in range(M):  # compute marginal player skills: Ps[p] being precision r_p, Ms[p] being precision-adjusted mean lambda_p.
            games_won = np.where(G[:, 0] == p)[0]     # return 1D np array.
            games_lost = np.where(G[:, 1] == p)[0]
            
            Ps[p] = 1./pv + np.sum(Pgs[games_won, 0]) + np.sum(Pgs[games_lost, 1])  # r_0 = 1./pv; each element in Pgs gives r_hg->wp.
            
            Ms[p] = np.sum(Pgs[games_won, 0] * Mgs[games_won, 0]) / Ps[p] \
                + np.sum(Pgs[games_lost, 1] * Mgs[games_lost, 1]) / Ps[p]           # Pgs[] * Mgs[] here is elementwise multiplication,
                                                                                    # giving precision-adjusted mean lambda_hg->wp.
                                                                                    # i.e. elements in Mgs are skill mean mu.
                                                                    # Dividing everything by Ps[p] so that Ms[p] = lambda / precision = mu.
        
        Ms_series[:,i] = Ms
        Ps_series[:,i] = Ps
        
        # (2) compute skill to game messages
#         print('G =', G)
#         print('Ps =', Ps)
#         print('Ps[G] =', Ps[G])
        Psg = Ps[G] - Pgs
        Msg = (Ps[G] * Ms[G] - Pgs * Mgs) / Psg

        # (3) compute game to performance messages
        vgt = 1 + np.sum(1. / Psg, axis=1)
        mgt = Msg[:, 0] - Msg[:, 1]
#         print('vgt =', vgt)
#         print('mgt =', mgt)

        # (4) approximate the marginal on performance differences
        Mt = mgt + np.sqrt(vgt) * psi(mgt / np.sqrt(vgt))
        Pt = 1. / (vgt * (1 - lam(mgt / np.sqrt(vgt))))

        # (5) compute performance to game messages
        ptg = Pt - 1. / vgt
        mtg = (Mt * Pt - mgt / vgt) / ptg

        # (6) compute game to skills messages
        Pgs = 1. / (1 + 1. / ptg[:, None] + 1. / np.flip(Psg, axis=1))
        Mgs = np.stack([mtg, -mtg], axis=1) + np.flip(Msg, axis=1)

#     return Ms, Ps
    return Ms_series, Ps_series
