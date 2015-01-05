import numpy as np
from numpy import shape, sum, sqrt, argsort, newaxis
from numpy.linalg import eigh


def principal_coordinates_analysis(distance_matrix):
    E_matrix = make_E_matrix(distance_matrix)
    F_matrix = make_F_matrix(E_matrix)
    eigvals, eigvecs = run_eig(F_matrix)
    eigvals = eigvals.real
    eigvecs = eigvecs.real
    point_matrix = get_principal_coordinates(eigvals, eigvecs)
    return point_matrix, eigvals, eigvecs


def make_E_matrix(dist_matrix):
    return (dist_matrix * dist_matrix) / -2.0


def make_F_matrix(E_matrix):
    num_rows, num_cols = shape(E_matrix)
    column_means = np.mean(E_matrix, axis=0)
    row_sums = np.sum(E_matrix, axis=1)
    row_means = row_sums / num_cols
    matrix_mean = sum(row_sums) / (num_rows * num_cols)

    E_matrix -= row_means
    E_matrix -= column_means
    E_matrix += matrix_mean
    return E_matrix


def run_eig(F_matrix):
    eigvals, eigvecs = eigh(F_matrix)
    return eigvals, eigvecs.transpose()


def get_principal_coordinates(eigvals, eigvecs):
    return eigvecs * sqrt(abs(eigvals))[:, newaxis]



u = [[0, 0.1, 0.1, 0.4, 0.5],
     [0.1, 0, 0.3, 0.2, 0.5],
     [0.1, 0.3, 0, 0.3, 0.5],
     [0.4, 0.2, 0.3, 0, 0.5],
     [0.5, 0.5, 0.5, 0.5, 0]]

mtx = np.asmatrix(u)
point_matrix, eigvals, eigvecs = principal_coordinates_analysis(mtx)
print 'matrix\n', point_matrix
print 'eigvals\n', eigvals
print 'eigvecs\n', eigvecs