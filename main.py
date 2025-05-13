from imports import *


my_data = np.genfromtxt(r"tfMatrix_3.csv", delimiter=';') #file load 
mat_complex = my_data[:,0::2] +1j*my_data[:,1::2] # complex matrix
#print(len(mat_complex[0]))
#print(len(mat_complex))

N_Re = 624 # number of subcarriers
N = len(mat_complex[0])


Dic_first_slot_PBCH = {} #dictionnary for PBCH 
#print("N = ", N)
truncated_mat1 = mat_complex[:,1:N_Re//2+1] 
truncated_mat2 = mat_complex[:,N-N_Re//2:N]
#print("taille matrice complexe", mat_complex.shape)


#print("taille demi_matrice 1 = ", truncated_mat1.shape)
#print(len(truncated_mat1[0]))
#print(len(truncated_mat1))

#print(len(truncated_mat2[0]))
#print(len(truncated_mat2))

tfMatrix_short = np.hstack((truncated_mat1,truncated_mat2)) #new matrix composed the 2 useful matrixs

#print("taille tf_matrix_short = ", tfMatrix_short.shape)

##print(tfMatrix_short)



def powerDistributionGraph(Z):
    """
    Draw the power distribution graph of T/F Matrix
    """
    fig, ax = plt.subplots()
    cs = ax.contourf(np.linspace(0, len(Z[0]), len(Z[0])), np.linspace(0,len(Z), len(Z)), np.abs(Z)**2)
    cbar = fig.colorbar(cs)
    ax.set_title('Power distribution graph') 
    ax.set_xlabel('Subcarrier') 
    ax.set_ylabel('OFDM Symbole') 
    plt.show()



#powerDistributionGraph(tfMatrix_short)

qamMatrix = tfMatrix_short[2:] #removing the 2 synchronized symbols

#print("QAM MATRIX SHAPE = ", qamMatrix.shape)

#powerDistributionGraph(qamMatrix)


# Proof that the first symbol is BPSK

"""
for j in range (2):
    print(f"Symbole {j+1}")
    for k in range (len(qamMatrix)):
       print(qamMatrix[j][k])
"""

def bpsk_demod(qamSeq):
    """
    Function to demodulate BPSK modulation sequence
    """
    seq_final = []
    for car in qamSeq:
        if np.real(car) < 0: # state = 0
            seq_final.append(0)
        else:   # state = 1
            seq_final.append(1)
    return seq_final


def hamming748_decode(seq):
    """
    Function to decode hamming748 encode
    """
    final_list = []
    for k in range(len(seq) // 8): # cut into seq of 8 bits
        seq_8_bits = seq[8*k:8*(k+1)]
        
        H = np.array([ #define H matrix
        [0, 0, 0, 1, 1, 1, 1],
        [0, 1, 1, 0, 0, 1, 1],
        [1, 0, 1, 0, 1, 0, 1]],dtype=int)

        y74 = np.array(seq_8_bits[:7],dtype=int) #y74 (7 first bits)

        syndrome = np.dot(H,y74) % 2 #multiplication of H and y74
        
        syndrome_index = 0
        for i in range(len(syndrome)):
            syndrome_index = syndrome_index + syndrome[-1 - i] * (2 ** i) # syndrom vector to int

        if syndrome_index != 0: # one or more error detected
            y74[syndrome_index-1] = (y74[syndrome_index-1]+1) %2 #bitflip on bit error

        parity = 0
        for i in range (len(y74)):
            parity = parity + y74[i] #parity calculous

        if parity % 2 == seq_8_bits[7] or syndrome_index == 0: #valid case
            final_list += (y74[:4].tolist()) #keep only the 4 first bits
        else  : #two errors
            raise("Two errors have been detected")
        
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
    """
    Fonction to recover Cell info and number of user
    """
    bpsk_decoded = bpsk_demod(matrix_first_48_bits)
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


def decode_pbchu():
    """
    Decode pbchu infos
    """
    global Dic_info_user
    Dic_info_user = {}
    info_cell_users(qamMatrix[0, :48]) 
    nb_user = Dic_first_slot_PBCH["number_user"]
    
    for k in range(nb_user-1): #for each user, decode user info
        qam_flat = qamMatrix.flatten() #flat matrix to solve overtaking the matrix size
        bpsk_decoded = bpsk_demod(qam_flat[48*(k+1):48*(k+2)])
        decoded_hamming = hamming748_decode(bpsk_decoded) 
        user_info(decoded_hamming)

def user_info(user_block):
    """
    Slice user info and store it in a dictionnary
    """
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


def qpsk_demod(qamSeq):
    """
    Function to demodulate QPSK sequence
    """
    seq_final = []
    for car in qamSeq: # each case depends on real and imaginary part, see doc
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
    """
    Function to decode PDCCHU sequence"""
    if Dic_info_user["user_ident", user_ident]["MCS_of_PDCCHU"] == 0: #BPSK
        return hamming748_decode(bpsk_demod(qam_seq))
        
    elif Dic_info_user["user_ident", user_ident]["MCS_of_PDCCHU"] == 2: #QPSK
        return hamming748_decode(qpsk_demod(qam_seq))
    else:
        print("Unknow MCS")
        raise ValueError("MCS non prit en charge")


def PDCCHU_decode_from_user(user_ident):
    symb_start = Dic_info_user["user_ident", user_ident]["Symb_start_of_PDCCHU"]
    RB_start = Dic_info_user["user_ident", user_ident]["RB_start_of_PDCCHU"]
    MCS = Dic_info_user["user_ident", user_ident]["MCS_of_PDCCHU"]
    #nb_symbols according to MCS (modulation and coding scheme)
    if MCS == 0: nb_symbols=72 #BPSK
    else: nb_symbols=36 #QPSK

    start_index = (symb_start - 1) * 624 + (RB_start - 1) * 12 #flatten the starting index to fit with the 1D matrix
    end_index = start_index + (nb_symbols) # flatten the ending index to fit with the 1D matrix

    qam_seq = tfMatrix_short.flatten('C')[start_index:end_index] #flatten the matrix to 1D
    return PDDCHU_decode_seq(qam_seq, user_ident)


#print(PDCCHU_decode_from_user(2))

def decode_PDDCHU_stream(pdcchu_stream):
    """
    Funciton to fill the dictionnary with PDCCHU infos
    """
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



def PDSCH_demod(qamSeq,mcs):
    """
    Function to demodulate PDSCH sequence
    """
    if mcs%5 == 0: #each case, depends on the MCS, see doc
        return bpsk_demod(qamSeq)
    elif mcs in [i for i in range (1,37,5)]:
        return qpsk_demod(qamSeq)
    elif mcs in [k for k in range (2,38,5)]:
        return qam16_demod(qamSeq)
    else :
        raise ValueError("Unknow MCS")
    
def PDSCH_fec(qamSeq,mcs):
    """
    Function to decode PDSCH sequence"""
    if mcs in [25,26,27]:
        return hamming748_decode(qamSeq) #hamming decoding
    elif mcs in [5,6,7]:
        return (fec.FECConv(('1011011','1111001'),6)).viterbi_decoder(np.array(qamSeq).astype(int),'hard').astype(int).tolist() #convolutional decoding, according to the doc
    else :
        raise ValueError("Unknow MCS")
    
def decode_PDSCHU(user_ident):
    """
    Function to decode PDSCHU for a user
    """

    #scraping the user info from the dictionnary
    user = Dic_info_user["user_ident", user_ident]
    symb_start = user["sym_start_PDSCHU"]
    rb_start = user["RB_start_PDSCHU"]
    rb_size = user["RB_size"]
    mcs = user["MCS_of_PDSCHU"]
    crc_size = user["CRC_flag"]

    start_index = (symb_start - 1) * 624 + (rb_start - 1) * 12 # flatten the starting index to fit with the 1D matrix
    end_index = start_index + (rb_size * 12) #flatten the ending index to fit with the 1D matrix
    qamSeq = tfMatrix_short.flatten('C')[start_index:end_index] #flatten the matrix to 1D

    demod = PDSCH_demod(qamSeq, mcs) #start demodulating the sequence
    fec = PDSCH_fec(demod, mcs) #start fec decoding
    if PDSCH_crc(fec, crc_size): #check if the crc is valid
        return fec
    else:
        raise ValueError("CRC error") 


def PDSCH_crc(qamSeq,crcSize):
    """
    Function to check the CRC of the PDSCH sequence"""
    crc_poly = get_crc_poly(8*(1+crcSize)) #create the CRC polynomial
    return crc_decode(qamSeq,crc_poly) #use the crc_decode function

def PDSCHU_to_string(user_ident):
    """
    Function to convert the PDSCHU sequence to a string
    """
    mess = bitToByte(decode_PDSCHU(user_ident)) #bit->byte
    real_mess = cesarDecode(user_ident,mess) #cesar decoding (doc)
    final_mess = "".join(toASCII(real_mess)) #ASCII conversion
    return final_mess

def extract_key():
    """
    Main function to extract the keys of all users
    """
    global Dic_key
    decode_pbchu() #decode the PBCHU, catch the user info for each user (pbchu only)
    Dic_key = {}
    for user_ident_tuple in Dic_info_user:
        user_ident = user_ident_tuple[1] #user is 2nd element
        try:
            pdcchu_stream = PDCCHU_decode_from_user(user_ident) #decode the PDCCHU stream for user
            decode_PDDCHU_stream(pdcchu_stream)  #decode the PDDCHU stream for user          
            message = PDSCHU_to_string(user_ident) #decode the PDSCHU stream for user
            print(message)
            key = message.split("key is ")[1].split()[0] #slice to extract the key
            Dic_key[user_ident] = key 
        except Exception as e:
            print(f"user error {user_ident} :", e)


extract_key()
print(Dic_key)