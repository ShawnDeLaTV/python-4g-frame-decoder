import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib import ticker, cm
import pytest
from qam16_demod import qam16_demod
import sk_dsp_comm.fec_conv as fec
from crc import get_crc_poly, crc_decode
from binary_transformation import bitToByte, cesarDecode, toASCII



my_data = np.genfromtxt(r"tfMatrix.csv", delimiter=';')
mat_complex = my_data[:,0::2] +1j*my_data[:,1::2] #Complex Matrice

#print(len(mat_complex[0]))
#print(len(mat_complex))

N_Re = 624 # Nombre de sous_porteuses utiles
N = len(mat_complex[0])
Dic_first_slot_PBCH = {}
#print("N = ", N)
truncated_mat1 = mat_complex[:,1:N_Re//2+1]
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



#powerDistributionGraph(tfMatrix_short)

qamMatrix = tfMatrix_short[2:]

#print("QAM MATRIX SHAPE = ", qamMatrix.shape)

#powerDistributionGraph(qamMatrix)


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

def bpsk_demod(qamSeq):
    seq_final = []
    for car in qamSeq:
        if np.real(car) < 0:
            seq_final.append(0)
        else:
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
        #print(seq_8_bits)
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
        #print("indice syndrome" , indice_syndrome)
        if indice_syndrome != 0:
            y74[indice_syndrome-1] = (y74[indice_syndrome-1]+1) %2 #bitflip
        parity = 0
        for i in range (len(y74)):
            parity = parity + y74[i]
        #print("parity", parity)
        if parity % 2 == seq_8_bits[7] or indice_syndrome == 0:
            final_list += (y74[:4].tolist()) # d'apres la doc c'est les 4 premiers bits les "data bits"
        else  :
            print("Deux erreurs ont ete detectees") # le mieux c'est de remplacer par un raise
    return final_list


def bin2dec(nb):
    """
    Transform a binary list to an integer
    """
    n = "0b"
    for b in nb:
        n = n + str(b)
    return int(n, 2)

    
def info_cell_users(matrix_first_48_bits):
    global Dic_first_slot_PBCH

    bpsk_decoded = bpsk_demod(matrix_first_48_bits) #Matrice de 0 et de 1 sans la partie de synchronisation (48 premiers bits)
    decoded_hamming = hamming748_decode(bpsk_decoded) 
    cell_user = bin2dec(decoded_hamming[:18])
    number_user = bin2dec(decoded_hamming[18:])
    Dic_first_slot_PBCH["cell_user"] = cell_user
    Dic_first_slot_PBCH["number_user"] = number_user
    return cell_user, number_user


#print(info_cell_users(qamMatrix[0, :48])) # résultat : cell user = 12345, nb user = 18
# la taille du pbch sera donc de 1*48 + 18*48 (users * 48 bits + le premier bloc d'init) = 912

# j'ai compris pourquoi graphiquement on voit que pbch s'étale sur 1.5 symbole : il y a plusieurs users (donc 48 bits) ce qui fait que 
# tout ne passe pas sur un seul symbole ofdm.


def pbchu():
    global Dic_info_user
    Dic_info_user = {}
    info_cell_users(qamMatrix[0, :48])
    nb_user =Dic_first_slot_PBCH["number_user"]
    
    for k in range(nb_user-1):
        qam_flat = qamMatrix.flatten()  # Met toute la matrice en un seul vecteur 1D
        bpsk_decoded = bpsk_demod(qam_flat[48*(k+1):48*(k+2)])
        decoded_hamming = hamming748_decode(bpsk_decoded) 
        user_info(decoded_hamming)

def user_info(user_block):
    user_ident = bin2dec(user_block[:8])
    MCS_of_PDCCHU = bin2dec(user_block[8:10])
    Symb_start_of_PDCCHU = bin2dec(user_block[10:14])
    RB_start_of_PDCCHU = bin2dec(user_block[14:20])
    HARQ_of_PDCCHU = bin2dec(user_block[20:24])

    Dic_info_user["user_ident", user_ident] = {
        "MCS_of_PDCCHU" : MCS_of_PDCCHU,
        "Symb_start_of_PDCCHU" : Symb_start_of_PDCCHU,
        "RB_start_of_PDCCHU" : RB_start_of_PDCCHU,
        "HARQ_of_PDCCHU" : HARQ_of_PDCCHU}


#print(Dic_info_user["user_ident",7])

def qpsk_demod(qamSeq): # dans la matrice le premier caractere de la 1ère et deuxieme ligne (PBCH) est un 0j, ici on l'ignore
    seq_final = []
    for car in qamSeq:
        if np.real(car) < 0 and (np.imag(car) > 0):
            seq_final.append(0)
            seq_final.append(1)
        elif np.real(car) < 0 and np.imag(car) < 0: 
            seq_final.append(0)
            seq_final.append(0)
        elif np.real(car) > 0 and np.imag(car) < 0: 
            seq_final.append(1)
            seq_final.append(0)
        elif np.real(car) > 0 and np.imag(car) > 0: 
            seq_final.append(1)
            seq_final.append(1)
    return seq_final


def PDDCHU_decode_seq(qam_seq, user_ident):
    if Dic_info_user["user_ident", user_ident]["MCS_of_PDCCHU"] == 0: #BPSK7
        bpsk_decoded = bpsk_demod(qam_seq)
        #print("Séquence BPSK décodée :", bpsk_decoded)
        return hamming748_decode(bpsk_demod(qam_seq))
        
    elif Dic_info_user["user_ident", user_ident]["MCS_of_PDCCHU"] == 2: #QPSK
        return hamming748_decode(qpsk_demod(qam_seq))
    else:
        print("La fec n'est pas reconnue") 


def PDCCHU_decode_from_user(user_ident):
    symb_start = Dic_info_user["user_ident", user_ident]["Symb_start_of_PDCCHU"]
    RB_start = Dic_info_user["user_ident", user_ident]["RB_start_of_PDCCHU"]
    MCS = Dic_info_user["user_ident", user_ident]["MCS_of_PDCCHU"]
    if MCS == 0: nb_symbols=72 
    else: nb_symbols=36

    start_index = (symb_start - 1) * 624 + (RB_start - 1) * 12 #décale en 1D le départ
    end_index = start_index + (nb_symbols) # décale en 1D l'arrivée

    qam_seq = tfMatrix_short.flatten('C')[start_index:end_index] #matrice de T/F en 1D (flatten)
    return PDDCHU_decode_seq(qam_seq, user_ident)


#print(PDCCHU_decode_from_user(2))

def decode_PDDCHU_stream(pdcchu_stream):
    user_ident = pdcchu_stream[:8]
    MCS_of_PDSCHU = pdcchu_stream[8:14]
    sym_start_PDSCHU = pdcchu_stream[14:18]
    RB_start_PDSCHU = pdcchu_stream[18:24]
    RB_size = pdcchu_stream[24:34]
    CRC_flag = pdcchu_stream[34:36]

    Dic_info_user["user_ident", bin2dec(user_ident)].update({
        "MCS_of_PDSCHU": bin2dec(MCS_of_PDSCHU),
        "sym_start_PDSCHU": bin2dec(sym_start_PDSCHU),
        "RB_start_PDSCHU": bin2dec(RB_start_PDSCHU),
        "RB_size": bin2dec(RB_size),
        "CRC_flag": bin2dec(CRC_flag)
    })

    return bin2dec(user_ident),bin2dec(MCS_of_PDSCHU),bin2dec(sym_start_PDSCHU), bin2dec(RB_start_PDSCHU), bin2dec(RB_size), bin2dec(CRC_flag)


#print(Dic_info_user["user_ident", 2])

def PDSCH_demod(qamSeq,mcs):
    # je ne comprend pas le truc avec le rate mais dans le code de noan ça a pas l'air important
    if mcs%5 == 0:
        return bpsk_demod(qamSeq)
    elif mcs in [i for i in range (1,37,5)]:
        return qpsk_demod(qamSeq)
    elif mcs in [k for k in range (2,38,5)]:
        return qam16_demod(qamSeq)
    else :
        raise "MCS non prit en charge"
    
def PDSCH_fec(qamSeq,mcs):
    if mcs in [25,26,27]:
        return hamming748_decode(qamSeq)
    elif mcs in [5,6,7]:
        return (fec.FECConv(('1011011','1111001'),6)).viterbi_decoder(np.array(qamSeq).astype(int),'hard').astype(int).tolist()
    else :
        raise "MCS non prit en charge"
    
def decode_PDSCHU(user_ident):
    user = Dic_info_user["user_ident", user_ident]
    symb_start = user["sym_start_PDSCHU"]
    rb_start = user["RB_start_PDSCHU"]
    rb_size = user["RB_size"]
    mcs = user["MCS_of_PDSCHU"]
    crc_size = user["CRC_flag"]

    start_index = (symb_start - 1) * 624 + (rb_start - 1) * 12 #décale en 1D le départ
    end_index = start_index + (rb_size * 12) # décale en 1D l'arrivée
    qamSeq = tfMatrix_short.flatten('C')[start_index:end_index] #matrice de T/F en 1D (flatten)

    demod = PDSCH_demod(qamSeq, mcs)
    fec = PDSCH_fec(demod, mcs)
    if PDSCH_crc(fec, crc_size):
        return fec
    else:
        raise ValueError("CRC invalide")



def PDSCH_crc(qamSeq,crcSize):
    crc_poly = get_crc_poly(8*(1+crcSize))
    return crc_decode(qamSeq,crc_poly)

def PDSCHU_to_string(user_ident):
    mess = bitToByte(decode_PDSCHU(user_ident))
    real_mess = cesarDecode(user_ident,mess)
    final_mess = "".join(toASCII(real_mess))
    return final_mess

def extract_key():
    global Dic_key
    pbchu()
    Dic_key = {}
    for user_ident_tuple in Dic_info_user:
        user_ident = user_ident_tuple[1]
        try:
            pdcchu_stream = PDCCHU_decode_from_user(user_ident)
            decode_PDDCHU_stream(pdcchu_stream)            
            message = PDSCHU_to_string(user_ident)
            print(message)
            key = message.split("key is ")[1].split()[0]
            Dic_key[user_ident] = key 
        except Exception as e:
            print(f"erreur utilisateur {user_ident} :", e) #il y a un probleme de l'user 11


extract_key()
#pdcchu_stream = PDCCHU_decode_from_user(11)
#decode_PDDCHU_stream(pdcchu_stream)            
#message = PDSCHU_to_string(11)

print(Dic_key)