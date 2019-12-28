import scipy.linalg
import numpy as np
from tqdm import tqdm

# G is the 1801-by-2 matrix storing the results of all the games. Each entry is the index of a player in the player name array `W`.
# M is the number of players, = 107.

def gibbs_sample(G, M, num_iters):
        
    # number of games
    N = G.shape[0]    # 1801.
    
    # Array containing mean skills of each player, set to prior mean
    w = np.zeros((M, 1))
    
    # Array that will contain skill samples
    skill_samples = np.zeros((M, num_iters))
    
    # Array containing skill variance for each player, set to prior variance
    pv = 0.5 * np.ones(M)
    iS_0 = np.diag(1. / pv)
    
    
    # number of iterations of Gibbs
    for i in tqdm(range(num_iters)):
        
        # Step 2 in handout 3.
        
        # sample performance given differences in skills and outcomes
        
        t = np.zeros((N, 1))
        
        for g in range(N):

            s = w[G[g, 0]] - w[G[g, 1]]  # difference in skills
            t[g] = s + np.random.randn()  # Sample performance
            
            while t[g] < 0:  # rejection step
                t[g] = s + np.random.randn()  # resample if rejected

        # ------------------------------------------------------------------
        
        # Step 3 in handout 3.
        
        # Jointly sample skills given performance differences
        
        # initialise `iSS*mu`, where `mu` is to be obtained.
        m = np.zeros((M, 1))
        
        # After this for-loop, m should be [ inv(Sigma_0)*mu_0 + sum_g{ inv(Sigma_g)*mu_g } ].
        # But note that inv(Sigma_g)*mu_g is just [tg, -tg]'.
        # Calculate mu_squiggle first.
        for p in range(M):
            # TODO: COMPLETE THIS LINE
#             g_p_win = [g for g, players in enumerate(G) if players[0] == p]
#             g_p_lose = [g for g, players in enumerate(G) if players[1] == p]
#             m[p] = sum([t[g] for g in g_p_win]) - sum([t[g] for g in g_p_lose])

            games_won = np.where(G[:, 0] == p)[0]     # return 1D np array.
            games_lost = np.where(G[:, 1] == p)[0]
            m[p] = np.sum(t[games_won]) - np.sum(t[games_lost])
            
#             m[p] = sum([ t[g] if players[0] == p   else -t[g] if players[1] == p   else 0   for g, players in enumerate(G)])
        
#         m += np.dot(iS_0, w)
            
        # Below is just an initialisation of a precision matrix, not the prior.
        iS = np.zeros((M, M))  # Container for sum of precision matrices (likelihood terms)

        for g in range(N):
            # TODO: Build the iS matrix, which is inv(Sigma_squiggle) in note.
            
            # Increment on the diagonal.
            iS[G[g,0], G[g,0]] += 1     # top-left corner.
            iS[G[g,1], G[g,1]] += 1     # bottom-right corner.
            # Decrement on the counter-diagonal.
            iS[G[g,0], G[g,1]] += -1    # top-right corner.   
            iS[G[g,1], G[g,0]] += -1    # bottom-left corner.

        # Posterior precision matrix
#         iSS = iS + np.diag(1. / pv)
        iSS = iS + iS_0
#         iS_0 = iSS    # Not sure if iS_0 needs to be updated.

        # Use Cholesky decomposition to sample from a multivariate Gaussian
        iR = scipy.linalg.cho_factor(iSS)  # Cholesky decomposition of the posterior precision matrix.
                                           # cho_factor returns upper triangular matrix by default, same as MATLAB.
                                           # Hence (iR)'iR = iSS.
        mu = scipy.linalg.cho_solve(iR, m, check_finite=False)  # uses cholesky factor to compute inv(iSS)*m,
                                                                # i.e. solve iSS*mu = m.

        # sample from N(mu, inv(iSS))
        w = mu + scipy.linalg.solve_triangular(iR[0], np.random.randn(M, 1), check_finite=False)
        skill_samples[:, i] = w[:, 0]
        
    return skill_samples


