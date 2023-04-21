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


"""
Fonction récursive pour calculer ERP
:param
A : séquence réalisée
B : séquence soumise
cpt : compteur d'opération de substitution ect...

:return
liste sous la forme : [ERBnorm,ERBe]
"""
def ERP(A, B):
    if len(A) == 0:
        return len(B)
    if len(B) == 0:
        return len(A)
    if A[0] == B[0]:
        return ERP(A[1:], B[1:])
    return min(ERP(A[1:], B) + 1, ERP(A, B[1:]) + 1, ERP(A[1:], B[1:])+ 1)

"""
calcule le score de la route proposé 
:param
A : séquence réalisée par amazon
B : séquence soumise

:return
erp
"""
def routeScore(A, B):
    #sd = SD(A, B)
    erp = ERP(A, B)
    return erp


