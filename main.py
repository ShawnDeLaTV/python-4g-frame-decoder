import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib import ticker, cm
import pytest
import sk_dsp_comm.fec_conv as fec

my_data = np.genfromtxt(r"reseauxsansfils/tfMatrix.csv", delimiter=';')
mat_complex = my_data[:,0::2] +1j*my_data[:,1::2] #Complex Matrice

print(len(mat_complex[0]))
print(len(mat_complex))

N_Re = 624 # Nombre de sous_porteuses utiles
N = len(mat_complex[0])
print("N = ", N)
truncated_mat1 = mat_complex[:,0:N_Re//2]
truncated_mat2 = mat_complex[:,N-N_Re//2:N]
print("taille matrice complexe", mat_complex.shape)


print("taille demi_matrice 1 = ", truncated_mat1.shape)
print(len(truncated_mat1[0]))
print(len(truncated_mat1))

print(len(truncated_mat2[0]))
print(len(truncated_mat2))

tfMatrix_short = np.hstack((truncated_mat1,truncated_mat2)) #la nouvelle matrix est la concaténation horizontale des deux matrices tronqués

print("taille tf_matrix_short = ", tfMatrix_short.shape)

#print(tfMatrix_short)

qamMatrix = tfMatrix_short[2:]

print("QAM MATRIX SHAPE = ", qamMatrix.shape)



a = [
    [1,1,1,1,1],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [1,1,1,1,1],
    [0,0,0,0,0]
]

def powerDistributionGraph(Z):
    """
    Draw the power distribution graph
    """
    fig, ax = plt.subplots()
    cs = ax.contourf(np.linspace(0, len(Z[0]), len(Z[0])), np.linspace(0,len(Z), len(Z)), np.abs(Z)**2)
    cbar = fig.colorbar(cs)
    ax.set_title('_') # je ne sais pas à quoi ça correspond 
    ax.set_xlabel('_') #je ne sais pas à quoi ça correspond mais c'est les lignes de la matrice
    ax.set_ylabel('_') #je ne sais pas à quoi ça correspond mais c'est les colonnes de la matrice
    plt.show()



powerDistributionGraph(tfMatrix_short)
powerDistributionGraph(qamMatrix)