import numpy as np

# Dimensions de la matrice
nb_symbols = 12
nb_subcarriers = 624

# Création de la matrice qamMatrix initialisée à 0
qamMatrix = np.zeros((nb_symbols, nb_subcarriers), dtype=complex)

# Remplissage des positions spécifiques avec des valeurs connues
# Par exemple, pour RB_start = 25 et symb_start = 4
RB_start = 25
symb_start = 4

# Remplir les sous-porteuses de l'indice 288 (25 * 12) à 300 (26 * 12) du symbole 4 avec des valeurs alternées (0 et 1)
for i in range(12):  # 12 sous-porteuses par RB
    qamMatrix[symb_start, RB_start * 12 + i] = complex(1, 0)  # Valeurs alternées 0 et 1


qam_seq = qamMatrix[symb_start, RB_start * 12:(RB_start + 1) * 12]


print(qam_seq)