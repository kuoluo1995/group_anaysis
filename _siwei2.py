# from scipy import linalg
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib as mpl
# from matplotlib import colors

# from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
# from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

# # #############################################################################
# # Colormap
# cmap = colors.LinearSegmentedColormap(
#     'red_blue_classes',
#     {'red': [(0, 1, 1), (1, 0.7, 0.7)],
#      'green': [(0, 0.7, 0.7), (1, 0.7, 0.7)],
#      'blue': [(0, 0.7, 0.7), (1, 1, 1)]})
# plt.cm.register_cmap(cmap=cmap)


# # #############################################################################
# # Generate datasets
# def dataset_fixed_cov():
#     '''Generate 2 Gaussians samples with the same covariance matrix'''
#     n, dim = 300, 2
#     np.random.seed(0)
#     C = np.array([[0., -0.23], [0.83, .23]])
#     X = np.r_[np.dot(np.random.randn(n, dim), C),
#               np.dot(np.random.randn(n, dim), C) + np.array([1, 1])]
#     y = np.hstack((np.zeros(n), np.ones(n)))
#     return X, y


# def dataset_cov():
#     '''Generate 2 Gaussians samples with different covariance matrices'''
#     n, dim = 300, 2
#     np.random.seed(0)
#     C = np.array([[0., -1.], [2.5, .7]]) * 2.
#     X = np.r_[np.dot(np.random.randn(n, dim), C),
#               np.dot(np.random.randn(n, dim), C.T) + np.array([1, 4])]
#     y = np.hstack((np.zeros(n), np.ones(n)))
#     return X, y


# # #############################################################################
# # Plot functions
# def plot_data(lda, X, y, y_pred, fig_index):
#     splot = plt.subplot(2, 2, fig_index)
#     if fig_index == 1:
#         plt.title('Linear Discriminant Analysis')
#         plt.ylabel('Data with\n fixed covariance')
#     elif fig_index == 2:
#         plt.title('Quadratic Discriminant Analysis')
#     elif fig_index == 3:
#         plt.ylabel('Data with\n varying covariances')

#     tp = (y == y_pred)  # True Positive
#     tp0, tp1 = tp[y == 0], tp[y == 1]
#     X0, X1 = X[y == 0], X[y == 1]
#     X0_tp, X0_fp = X0[tp0], X0[~tp0]
#     X1_tp, X1_fp = X1[tp1], X1[~tp1]

#     # class 0: dots
#     plt.scatter(X0_tp[:, 0], X0_tp[:, 1], marker='.', color='red')
#     plt.scatter(X0_fp[:, 0], X0_fp[:, 1], marker='x',
#                 s=20, color='#990000')  # dark red

#     # class 1: dots
#     plt.scatter(X1_tp[:, 0], X1_tp[:, 1], marker='.', color='blue')
#     plt.scatter(X1_fp[:, 0], X1_fp[:, 1], marker='x',
#                 s=20, color='#000099')  # dark blue

#     # class 0 and 1 : areas
#     nx, ny = 200, 100
#     x_min, x_max = plt.xlim()
#     y_min, y_max = plt.ylim()
#     xx, yy = np.meshgrid(np.linspace(x_min, x_max, nx),
#                          np.linspace(y_min, y_max, ny))
#     Z = lda.predict_proba(np.c_[xx.ravel(), yy.ravel()])
#     Z = Z[:, 1].reshape(xx.shape)
#     plt.pcolormesh(xx, yy, Z, cmap='red_blue_classes',
#                    norm=colors.Normalize(0., 1.), zorder=0)
#     plt.contour(xx, yy, Z, [0.5], linewidths=2., colors='white')

#     # means
#     plt.plot(lda.means_[0][0], lda.means_[0][1],
#              '*', color='yellow', markersize=15, markeredgecolor='grey')
#     plt.plot(lda.means_[1][0], lda.means_[1][1],
#              '*', color='yellow', markersize=15, markeredgecolor='grey')

#     return splot


# def plot_ellipse(splot, mean, cov, color):
#     v, w = linalg.eigh(cov)
#     u = w[0] / linalg.norm(w[0])
#     angle = np.arctan(u[1] / u[0])
#     angle = 180 * angle / np.pi  # convert to degrees
#     # filled Gaussian at 2 standard deviation
#     ell = mpl.patches.Ellipse(mean, 2 * v[0] ** 0.5, 2 * v[1] ** 0.5,
#                               180 + angle, facecolor=color,
#                               edgecolor='black', linewidth=2)
#     ell.set_clip_box(splot.bbox)
#     ell.set_alpha(0.2)
#     splot.add_artist(ell)
#     splot.set_xticks(())
#     splot.set_yticks(())


# def plot_lda_cov(lda, splot):
#     plot_ellipse(splot, lda.means_[0], lda.covariance_, 'red')
#     plot_ellipse(splot, lda.means_[1], lda.covariance_, 'blue')


# def plot_qda_cov(qda, splot):
#     plot_ellipse(splot, qda.means_[0], qda.covariance_[0], 'red')
#     plot_ellipse(splot, qda.means_[1], qda.covariance_[1], 'blue')


# plt.figure(figsize=(10, 8), facecolor='white')
# plt.suptitle('Linear Discriminant Analysis vs Quadratic Discriminant Analysis',
#              y=0.98, fontsize=15)
# for i, (X, y) in enumerate([dataset_fixed_cov(), dataset_cov()]):
#     # Linear Discriminant Analysis
#     lda = LinearDiscriminantAnalysis(solver="svd", store_covariance=True)
#     y_pred = lda.fit(X, y).predict(X)
#     splot = plot_data(lda, X, y, y_pred, fig_index=2 * i + 1)
#     plot_lda_cov(lda, splot)
#     plt.axis('tight')

#     # Quadratic Discriminant Analysis
#     qda = QuadraticDiscriminantAnalysis(store_covariance=True)
#     y_pred = qda.fit(X, y).predict(X)
#     splot = plot_data(qda, X, y, y_pred, fig_index=2 * i + 2)
#     plot_qda_cov(qda, splot)
#     plt.axis('tight')
# plt.tight_layout()
# plt.subplots_adjust(top=0.92)
# plt.show()


# import numpy as np
# from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
# X = np.array([[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]])
# y = np.array([1, 1, 1, 2, 2, 2])
# clf = LinearDiscriminantAnalysis()
# clf.fit(X, y)
# LinearDiscriminantAnalysis()
# print(clf.predict([[-0.8, -1]]))
# print(clf.get_params())


# import numpy as np
# import matplotlib.pyplot as plt
from sklearn.datasets.samples_generator import make_classification
# from mpl_toolkits.mplot3d import Axes3D
 
# def average(dataset):
#     ave = []
#     a, b = np.shape(dataset)
#     for i in range(b):
#         n = np.sum(dataset[:,i]) / a
#         ave.append(n)
#     return np.array(ave)

# def compute_sw(dataset, ave):
#     sw = 0
#     a, b = np.shape(dataset)
#     for i in range(a - 1):
#         sw += np.dot(dataset[i,:] - ave, (dataset[i,:] - ave).T)
#         print(sw, np.dot(dataset[i,:] - ave, (dataset[i,:] - ave).T))
#     return np.array(sw)

# def compute_w(x1_x, x2_x):
#     x1_x_ave = average(x1_x)
#     x2_x_ave = average(x2_x)

#     x1_sw = compute_sw(x1_x, x1_x_ave)
#     x2_sw = compute_sw(x2_x, x2_x_ave)
#     Sw = x1_sw + x2_sw
    
#     print(Sw)
#     #求广义逆
#     pinv = np.linalg.pinv(Sw)
#     w = np.multiply(x1_x_ave - x2_x_ave, pinv)[0,:]
#     return w

# def LDA(X, y):
#     X1 = np.array([X[i] for i in range(len(X)) if y[i] == 0])
#     X2 = np.array([X[i] for i in range(len(X)) if y[i] == 1])

#     w = compute_w(X1, X2)
#     # len1 = len(X1)
#     # len2 = len(X2)

#     # mju1 = np.mean(X1, axis=0)#求中心点
#     # mju2 = np.mean(X2, axis=0)

#     # cov1 = np.dot((X1 - mju1).T, (X1 - mju1))
#     # cov2 = np.dot((X2 - mju2).T, (X2 - mju2))
#     # Sw = cov1 + cov2

#     # w = np.dot(np.mat(Sw).I, (mju1 - mju2).reshape((len(mju1), 1)))
#     # print(w)
#     # 计算w
#     X1_new = project(X1, w)
#     X2_new = project(X2, w)
#     y1_new = [1 for i in range(len1)]
#     y2_new = [2 for i in range(len2)]
#     return X1_new, X2_new, y1_new, y2_new, w
 
 
# def project(x, w):
#     return np.dot((x), w)
 
 
# if '__main__' == __name__:
#     X, y = make_classification(n_samples=500, n_features=2, n_redundant=0, n_classes=2,
#                                n_informative=1, n_clusters_per_class=1, class_sep=0.5, random_state=10)
#     # print(X)
#     X1_new, X2_new, y1_new, y2_new, w = LDA(X, y)
    
#     # w是1到n的顺序
#     k = float(w[1][0]/w[0][0])
#     print(k)
#     xs = np.arange(-1, 1, 0.1)
#     # np.array(list(range(min(X), max(X))))
#     # print(k, xs)
#     ys = xs * k

#     # plt.scatter(X[:, 0], X[:, 1], marker='o', c=y)
#     # plt.plot(xs, ys)
#     # plt.show()
 
#     plt.plot(X1_new, y1_new, 'b*')
#     plt.plot(X2_new, y2_new, 'ro')
#     plt.show()

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.datasets import load_iris
import matplotlib.pyplot as plt

def lda(data, target, n_dim):
    '''
    :param data: (n_samples, n_features)
    :param target: data class
    :param n_dim: target dimension
    :return: (n_samples, n_dims)
    '''

    clusters = np.unique(target)

    if n_dim > len(clusters)-1:
        print("K is too much")
        print("please input again")
        exit(0)

    #within_class scatter matrix
    Sw = np.zeros((data.shape[1],data.shape[1]))
    for i in clusters:
        datai = data[target == i]
        datai = datai-datai.mean(0)
        Swi = np.mat(datai).T*np.mat(datai)
        Sw += Swi

    #between_class scatter matrix
    SB = np.zeros((data.shape[1],data.shape[1]))
    u = data.mean(0)  #所有样本的平均值
    for i in clusters:
        Ni = data[target == i].shape[0]
        ui = data[target == i].mean(0)  #某个类别的平均值
        SBi = Ni*np.mat(ui - u).T*np.mat(ui - u)
        SB += SBi
    S = np.linalg.inv(Sw)*SB
    eigVals,eigVects = np.linalg.eig(S)  #求特征值，特征向量
    eigValInd = np.argsort(eigVals)
    eigValInd = eigValInd[:(-n_dim-1):-1]
    w = eigVects[:,eigValInd]
    # print(eigVects, eigValInd)
    data_ndim = np.dot(data, w)

    return data_ndim, w

if __name__ == '__main__':
    X, Y = make_classification(n_samples=500, n_features=3, n_redundant=0, n_classes=2,
                               n_informative=3, n_clusters_per_class=1, class_sep=0.5, random_state=10)
    # iris = load_iris()
    # X = iris.data
    # Y = iris.target
    data_1, w = lda(X, Y, 1)
    print(w)
    lda_m = LinearDiscriminantAnalysis(n_components=1)
    lda_m.fit(X, Y)
    data_2 = lda_m.fit_transform(X, Y)
    print(lda_m.coef_)
    # w = X[0]/Y[0]
    # print(np.dot(np.linalg.inv(X), data_2))

    # plt.figure(figsize=(8,4))
    # plt.subplot(121)
    # plt.title("LDA")
    # plt.scatter(data_1[:, 0], data_1[:, 1], c = Y)

    # plt.subplot(122)
    # plt.title("sklearn_LDA")
    # plt.scatter(data_2[:, 0], data_2[:, 1], c = Y)
    # plt.savefig("LDA.png",dpi=600)
    # plt.show()
