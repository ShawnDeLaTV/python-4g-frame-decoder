import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib import ticker, cm
import pytest

import sk_dsp_comm.fec_conv as fec

my_data = np.genfromtxt(r"tfMatrix.csv", delimiter=';')
mat_complex = my_data[:,0::2] +1j*my_data[:,1::2] #Complex Matrice

#print(len(mat_complex[0]))
#print(len(mat_complex))

N_Re = 624 # Nombre de sous_porteuses utiles
N = len(mat_complex[0])
#print("N = ", N)
truncated_mat1 = mat_complex[:,0:N_Re//2]
truncated_mat2 = mat_complex[:,N-N_Re//2:N]
#print("taille matrice complexe", mat_complex.shape)


#print("taille demi_matrice 1 = ", truncated_mat1.shape)
#print(len(truncated_mat1[0]))
#print(len(truncated_mat1))

#print(len(truncated_mat2[0]))
#print(len(truncated_mat2))

tfMatrix_short = np.hstack((truncated_mat1,truncated_mat2)) #la nouvelle matrix est la concaténation horizontale des deux matrices tronqués

#print("taille tf_matrix_short = ", tfMatrix_short.shape)

##print(tfMatrix_short)



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
    #plt.show()



powerDistributionGraph(tfMatrix_short)

qamMatrix = tfMatrix_short[2:]

#print("QAM MATRIX SHAPE = ", qamMatrix.shape)

powerDistributionGraph(qamMatrix)


# Preuve que le premier symbole est bien BPSK (partie imaginaire nulle, varie entre +1 et -1 en réel)
#for j in range (2):
    #print(f"Symbole {j+1}")
    #for k in range (len(qamMatrix)):
        #print(qamMatrix[j][k])

def matrix_to_seq(qam_matrix):
    seq = []
    for j in range (2):
        for k in range (len(qam_matrix)):
            seq.append(qam_matrix[j][k])
    return seq

def bpsk_demod(qamSeq): # dans la matrice le premier caractere de la 1ère et deuxieme ligne (PBCH) est un 0j, ici on l'ignore
    seq_final = []
    for car in qamSeq:
        if np.real(car) < 0.5 and (np.imag(car) < 0.5 or np.imag(car) > 0.5): # variation bruit
            seq_final.append(0)
        elif np.real(car) > 0.5 and (np.imag(car) < 0.5 or np.imag(car) > 0.5): # variation bruit
            seq_final.append(1)
    return seq_final
        
seq_decode = bpsk_demod(matrix_to_seq(qamMatrix))

#print(seq_decode)


pbch_matrix_seq = qamMatrix[0, :48] # 48 premier bits

#print (len(pbch_matrix_seq))

# --- Calling Hamming decoding function
#for k in range (6):
#        seq_8_bits = seq[8*k:8*(k+1)]

def hamming748_decode(seq):
    final_list = []
    for k in range(len(seq) // 8):
        seq_8_bits = seq[8*k:8*(k+1)]
        H = np.array([
        [0, 0, 0, 1, 1, 1, 1],
        [0, 1, 1, 0, 0, 1, 1],
        [1, 0, 1, 0, 1, 0, 1]],dtype=int)
        y74 = np.array(seq_8_bits[:7],dtype=int)
        syndrome = np.dot(H,y74) % 2
        indice_syndrome = 0
        for i in range(len(syndrome)):
            indice_syndrome = indice_syndrome + syndrome[-1 - i] * (2 ** i)
        # cas
        #print(indice_syndrome)
        if indice_syndrome != 0:
            y74[indice_syndrome-1] = (y74[indice_syndrome-1]+1) %2 #bitflip
        parity = 0
        for i in range (len(y74)):
            parity = parity + y74[i]
        if parity % 2 == seq[7]:
            final_list += (y74[:4].tolist()) # d'apres la doc c'est les 4 premiers bits les "data bits"
        else :
            return "Deux erreurs ont été détéctées" # le mieux c'est de remplacer par un raise
    return final_list




#bool = hamming748_decode([0, 0, 1, 1, 0, 0, 1, 0]) celui la ne passe pas, alors qu'il est censé n'avoir qu'une erreur (corrigeable)
# à corriger
#print(bool)


# j'ai compris pourquoi graphiquement on voit que pbch s'étale sur 1.5 symbole : il y a plusieurs users (donc 48 bits) ce qui fait que 
# tout ne passe pas sur un seul symbole ofdm.