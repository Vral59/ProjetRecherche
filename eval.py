import numpy as np

"""
Evaluation de SD

:param
A : séquence réalisée
B : séquence soumise
supposons que se seront des listes d'indice dans l'ordre de parcours
"""
def SD(A,B):
    n = len(B)
    # Les élements de la liste sont normalement unique donc le .index ne pose pas de soucs
    a = [A.index(B[i]) for i in range(n)]
    sd = 0
    for i in range(n):
        sd += n*abs(a[i]-a[i-1]) - 1

    return (2/(n*(n-1)))*sd

# Cette fonction revoie toujours 0 pour ERPe a corriger
"""
Fonction récursive pour calculer ERP
:param
A : séquence réalisée
B : séquence soumise
cpt : compteur d'opération de substitution ect...

:return
liste sous la forme : [ERBnorm,ERBe]
"""
def ERP(A, B, cpt):
    if len(A) == 0:
        return len(B), cpt + len(B)
    if len(B) == 0:
        return len(A), cpt + len(A)
    if A[0] == B[0]:
        return ERP(A[1:], B[1:], cpt)
    return min(ERP(A[1:], B, cpt+1)[0] + 1, ERP(A, B[1:], cpt+1)[0] + 1, ERP(A[1:], B[1:], cpt+1)[0] + 1), cpt

# Vérifier les valeurs
"""
Fonction récursive pour calculer ERP
:param
A : séquence réalisée
B : séquence soumise

:return
tuple sous la forme : [ERBnorm,ERBe]
"""
def LevenshteinDistance(A, B):
    m, n = len(A), len(B)
    D = [[0] * (n + 1) for _ in range(m + 1)]

    # initialisation de la première colonne et première ligne
    for i in range(m + 1):
        D[i][0] = i
    for j in range(n + 1):
        D[0][j] = j

    # calcul de la matrice de distance
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if A[i - 1] == B[j - 1] else 1
            D[i][j] = min(D[i - 1][j] + 1, D[i][j - 1] + 1, D[i - 1][j - 1] + cost)

    # renvoi de la distance d'édition et du nombre d'opérations d'édition
    return D[m][n], D[m][n] + m + n - 2 * D[m][n]

"""
calcule le score de la route proposé 
:param
A : séquence réalisée
B : séquence soumise

:return
SD * ERPnorm / ERPe
"""
def routeScore(A, B):
    sd = SD(A, B)
    #erp = ERP(A, B, 0)
    norm,e = LevenshteinDistance(A,B)
    print("sd = ", sd)
    print("ERPnorm = ", norm)
    print("ERPe = ", e)
    return (sd*norm)/e


A = ["A", "B", "C", "D", "E"]
B = ["C", "B", "E", "A", "D"]

print(routeScore(A, B))
