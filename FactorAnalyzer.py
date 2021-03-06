import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import prince
from sklearn.decomposition import PCA, SparsePCA
from sklearn.manifold import TSNE
from matplotlib.ticker import MaxNLocator
import seaborn as sns
from IPython.core.display import display
from sklearn.covariance import GraphicalLassoCV, LedoitWolf
import networkx as nx
from mpl_toolkits.mplot3d import Axes3D 
from sklearn import preprocessing

from Utility import Utility

import warnings
warnings.filterwarnings("ignore")

class FactorAnalyzer():

    def pca(self, n_comp, df, cols=None, excluded_cols = [], color_label = None, plot = True, plot_arrows = False):
        '''
        n_comp: n principal components
        cols: optional, specify which columns. Need to make sure they are numerical
        excluded_cols:  if some columns are to be excluded
        color_label: categorical data used to color the label. If given, will plot 2D visualization.
        plot: boolean, whether to plot
            
        Performs PCA with k=n_comp principal components on the dataframe df with given cols.
        Returns a dictionnary with:
        the transformed components, 
        the principal components,
        the variance explained per component,
        pca model
        '''
        new_df = Utility().normalize(df).dropna() # Remove NA, normalize
        
        if cols == None:
            cols = df._get_numeric_data().columns  # Takes only numeric columns
        cols = [c for c in cols if c not in excluded_cols and c != color_label]
        df_num = new_df[cols]
        
        pca = PCA(n_components=n_comp)
        
        pca_results = pca.fit_transform(df_num.values)
        explained_tot_variance = sum(pca.explained_variance_ratio_)
        
        new_df['PC1'] = pca_results[:, 0]
        new_df['PC2'] = pca_results[:, 1]
        if n_comp > 2:
            new_df['PC3'] = pca_results[:, 2]
        
        if plot:
            # Plot explained variance per component
            print('Explained variation per principal component: {}'.format(pca.explained_variance_ratio_))
            print('Explained total variation:', explained_tot_variance)
            ax = plt.figure().gca()
            ax.bar(np.arange(1,n_comp+1), np.cumsum(pca.explained_variance_ratio_), width=0.2, label = "cumulative")
            ax.bar(np.arange(1,n_comp+1), pca.explained_variance_ratio_, width=0.2, label = "single")
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            plt.xlabel('Principal components')
            plt.ylabel('Cumulative variance ratio explained')
            plt.legend()
            plt.show()

            # Show component heatmap
            index = ["PC{0:d}[{1:.2f}]".format(i+1,pca.explained_variance_ratio_[i]) for i in range(n_comp)]
            components = pd.DataFrame(pca.components_, columns = cols, index =index)
            fig, ax = plt.subplots(figsize = (10,8))
            sns.heatmap(components.T, annot = True, center = 0, fmt = '.2f', linewidth = 0.5)
            ax.set_title("Loading factors")
            plt.xticks(rotation = 45)
            ax.set_ylim(components.T.shape[0]-1e-9, -1e-9)
            ax.set_ylabel("Feature")
            ax.set_xlabel("Component[Explained inertia]")
            plt.show()
            
            
            new_df['PC1'] = (new_df['PC1'])/(new_df['PC1'].max()-new_df['PC1'].min())
            new_df['PC2'] = (new_df['PC2'])/(new_df['PC2'].max()-new_df['PC2'].min())
            new_df['PC3'] = (new_df['PC3'])/(new_df['PC3'].max()-new_df['PC3'].min())
            
            # Visualize over the 2 first components
            fig, ax = plt.subplots(figsize = (10,10))
            ax.set_xlim([-1,1])
            ax.set_ylim([-1,1])
            plt.grid(True)
            if color_label != None: 
                if not np.issubdtype(new_df[color_label].dtype, np.number): # If color label categorical, label with different colors 
                    palette = sns.color_palette("hls", len(new_df[color_label].unique()))
                    sns.scatterplot(
                        x='PC1', y='PC2',
                        hue=color_label,
                        palette=palette,
                        data=new_df,
                        legend="full",
                        alpha=0.8
                    )  
                else: # If color label is continuous, gives a colormap
                    cmap = sns.dark_palette("palegreen", as_cmap=True)
                    points = ax.scatter(pca_results[:, 0], pca_results[:, 1], c=new_df[color_label], cmap=cmap, alpha=0.8)
                    fig.colorbar(points)
            else: # Same color fo all points
                sns.scatterplot(
                        x='PC1', y='PC2',
                        data=new_df,
                    ) 
            if plot_arrows:
                for col in cols:
                    plt.arrow(0,0, components[col][0],components[col][1], length_includes_head = True, head_width = 0.03)
                    props = dict(boxstyle='round', facecolor='white', alpha=0.8)
                    plt.text(components[col][0]* 1.15, components[col][1] * 1.15, col, color = 'k', 
                             ha = 'center', va = 'center', fontsize = 10, bbox = props)
            plt.xlabel("PC1 ({:.2%} explained variance)".format(pca.explained_variance_ratio_[0]))    
            plt.ylabel("PC2 ({:.2%} explained variance)".format(pca.explained_variance_ratio_[1]))   
            plt.show()
   
            # OLDER VERSION
            if color_label != None:               
                if not np.issubdtype(new_df[color_label].dtype, np.number): # If color label categorical, label with different colors 
                    palette = sns.color_palette("hls", len(new_df[color_label].unique()))
                    plt.figure(figsize=(16, 10))
                    sns.scatterplot(
                        x='PC1', y='PC2',
                        hue=color_label,
                        palette=palette,
                        data=new_df,
                        legend="full",
                        alpha=0.8
                    )
                else:  # If color label is continuous, gives a colormap
                    f, ax = plt.subplots(figsize=(16, 10))
                    cmap = sns.dark_palette("palegreen", as_cmap=True)
                    points = ax.scatter(pca_results[:, 0], pca_results[:, 1], c=new_df[color_label], cmap=cmap, alpha=0.8)
                    f.colorbar(points)
                plt.xlabel("PC1 ({:.2%} explained variance)".format(pca.explained_variance_ratio_[0]))    
                plt.ylabel("PC2 ({:.2%} explained variance)".format(pca.explained_variance_ratio_[1]))   
                plt.show()
        
        return {"results": pd.DataFrame(pca_results, columns = np.arange(n_comp)),
                "components": pd.DataFrame(pca.components_, columns = cols), 
                "explained_variance": pca.explained_variance_ratio_,
                "model": pca}
            
    
    def tsne(self, df, cols = None, excluded_cols = [], color_label = None, plot = True):
        '''
        Returns a new dataframe with first and second component of t-SNE decomposition.
        '''
        new_df = df.dropna() # Remove NA
        
        if cols == None:
            cols = df._get_numeric_data().columns  # Takes only numeric columns
        cols = [c for c in cols if c not in excluded_cols and c != color_label]
        df_num = new_df[cols]
    
        tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=300)
        tsne_results = tsne.fit_transform(df_num.values)
       
        new_df['tsne_one'] = tsne_results[:, 0]
        new_df['tsne_two'] = tsne_results[:, 1]
        if color_label != None:
            if not np.issubdtype(new_df[color_label].dtype, np.number):
                 plt.figure(figsize=(16, 10))
                 sns.scatterplot(
                        x="tsne_one", y="tsne_two",
                        hue=color_label,
                        palette=sns.color_palette("hls", len(new_df[color_label].unique())),
                        data=new_df,
                        legend="full",
                        alpha=0.8
                        )
            else:
                f, ax = plt.subplots(figsize=(16, 10))
                cmap = sns.dark_palette("palegreen", as_cmap=True)
                points = ax.scatter(tsne_results[:, 0], tsne_results[:, 1], c=new_df[color_label], cmap=cmap, alpha=0.8)
                f.colorbar(points)
        return {"results": pd.DataFrame(tsne_results, columns = np.arange(2))}
    
        
    def pca_prince(self, df, cols, color_labels = None):
        """
        cols:  a list of numerical column names
        color_labels: categorical label column
        Prince's implementation of 2D pca with visualiztion
        """
        pca = prince.PCA(n_components=2,n_iter=3,rescale_with_mean=True, rescale_with_std=True,
                copy=True, check_input=True,engine='auto')
        pca = pca.fit(df[cols])
        fig, ax = plt.subplots(figsize = (10,10))
        pca.plot_row_coordinates(df[cols],ax = ax, x_component=0,y_component=1,
                labels=None,color_labels = df[color_labels],ellipse_outline=False,ellipse_fill=True,show_points=True)
        fig.show()
        return pca    
    
    def sparce_invcov(self, df, cols = None, style = "GraphLassoCV", param = 0.2, layout = "circular", 
                      center = None, figsize = (7,7)):
        """
        cols: columns to calculate. If None, takes all numerical columns
        style: GraphLassoCV or LedoitWolf
        param: Parameter to pass to fitting algorithm. If GraphLasso, =alpha; if LedoitWolf, =threshold
        layout: choose between "circular", "spring", "shell"
        center: Put a certain colname in the center of the graph
            
        Sparse covariance matrix estimation
        Plot the sparce precision matrix
        """
        new_df = Utility().normalize(df).dropna() # Remove NA, normalize
        if cols == None:
            cols = df._get_numeric_data().columns
        data = new_df[cols]
        if style == "GraphLassoCV":
            model = GraphicalLassoCV(alphas = [param,param], cv = 10, max_iter = 5000)
            model.fit(data)
            sparce_mat = np.zeros(np.shape(model.precision_))
            sparce_mat[model.precision_ != 0] = -1
            np.fill_diagonal(sparce_mat, 1)
        else: # Style == LedoitWolf
            model = LedoitWolf()
            model.fit(data)
            sparce_mat = np.zeros(np.shape(model.get_precision()))
            sparce_mat[np.abs(model.get_precision())>param] = -1
        np.fill_diagonal(sparce_mat, 1)
        sparce_mat = pd.DataFrame(sparce_mat, index = data.columns, columns = data.columns)
            
        # NetworkX Graph
        fig, ax = plt.subplots(figsize = figsize)
        G = nx.from_pandas_adjacency(sparce_mat)
   
        pos={"circular": nx.drawing.circular_layout,
             "shell": nx.drawing.shell_layout,
             "spring": nx.drawing.spring_layout,
             }[layout](G, scale = 2)
        pos[center] = np.array([0, 0])
        node_color = ['mintcream' if node==center else 'mintcream' for node in G.nodes]    
        node_size = [len(node) * 1500 if node==center else len(node)*500 for node in G.nodes()]        
        nodes = nx.draw_networkx_nodes(G, pos, node_shape = 'o', node_color = node_color, 
                                       node_size = node_size)
        nodes.set_edgecolor('k')
        nx.draw_networkx_edges(G, pos, edge_color = 'r', width = 2.0, alpha = 0.8)
        nx.draw_networkx_labels(G, pos, font_weight = 'bold', font_size = 10)
        plt.axis('off')
        plt.tight_layout()
          
        # Display precision matrix as heatmap
        fig, ax = plt.subplots(figsize=(5, 5))
        sns.heatmap(sparce_mat,
                   vmax=1, vmin=-1, linewidth = 0.1,
                   cmap=plt.cm.RdBu_r, cbar = False)
        ax.set_ylim(sparce_mat.T.shape[0]-1e-9, -1e-9)
        plt.title('Sparse Inverse Covariance')
        plt.show()
        
        return sparce_mat

            
    def ca(self, df, col1, col2):
        """
        col1, col2: categorical column names
        
        Do a correspondence analysis
        """
        X = pd.crosstab(df[col1], df[col2])
        ca = prince.CA(n_components=2, n_iter=3, copy=True, check_input=True, engine='auto')
        ca = ca.fit(X)
        fig, ax = plt.subplots(figsize = (10,10))
        ca.plot_coordinates(X=X,ax = ax, x_component=0,y_component=1,
                                 show_row_labels=True,show_col_labels=True)
        plt.show()
        print("Explained inertia:", ca.explained_inertia_)
        return ca
    
    def mca(self, df, cols):
        """
        cols: list of categorical column names
        
        Do a multiple correspondence analysis
        """
        mca = prince.MCA(n_components=2,n_iter=3,copy=True, check_input=True,engine='auto')
        mca.fit(df[cols])
        fig, ax = plt.subplots(figsize = (10,10))
        mca.plot_coordinates(X=df[cols],ax=ax,show_row_points=True,row_points_size=10, show_row_labels=False,
                             show_column_points=True,column_points_size=30,show_column_labels=False,
                             legend_n_cols=1)
        plt.show()
        print("Explained inertia:", mca.explained_inertia_)
        return mca
    
    
# =============================================================================
# Robust PCA
# =============================================================================
class R_pca:

    def __init__(self, D, mu=None, lmbda=None):
        self.D = D
        self.S = np.zeros(self.D.shape)
        self.Y = np.zeros(self.D.shape)

        if mu:
            self.mu = mu
        else:
            self.mu = np.prod(self.D.shape) / (4 * self.frobenius_norm(self.D))

        self.mu_inv = 1 / self.mu

        if lmbda:
            self.lmbda = lmbda
        else:
            self.lmbda = 1 / np.sqrt(np.max(self.D.shape))

    @staticmethod
    def frobenius_norm(M):
        return np.linalg.norm(M, ord='fro')

    @staticmethod
    def shrink(M, tau):
        return np.sign(M) * np.maximum((np.abs(M) - tau), np.zeros(M.shape))

    def svd_threshold(self, M, tau):
        U, S, V = np.linalg.svd(M, full_matrices=False)
        return np.dot(U, np.dot(np.diag(self.shrink(S, tau)), V))

    def fit(self, tol=None, max_iter=1000, iter_print=100):
        iter = 0
        err = np.Inf
        Sk = self.S
        Yk = self.Y
        Lk = np.zeros(self.D.shape)

        if tol:
            _tol = tol
        else:
            _tol = 1E-7 * self.frobenius_norm(self.D)

        while (err > _tol) and iter < max_iter:
            Lk = self.svd_threshold(
                self.D - Sk + self.mu_inv * Yk, self.mu_inv)
            Sk = self.shrink(
                self.D - Lk + (self.mu_inv * Yk), self.mu_inv * self.lmbda)
            Yk = Yk + self.mu * (self.D - Lk - Sk)
            err = self.frobenius_norm(self.D - Lk - Sk)
            iter += 1
            if (iter % iter_print) == 0 or iter == 1 or iter > max_iter or err <= _tol:
                print('iteration: {0}, error: {1}'.format(iter, err))

        self.L = Lk
        self.S = Sk
        return Lk, Sk

    def plot_fit(self, size=None, tol=0.1, axis_on=True):

        n, d = self.D.shape

        if size:
            nrows, ncols = size
        else:
            sq = np.ceil(np.sqrt(n))
            nrows = int(sq)
            ncols = int(sq)

        ymin = np.nanmin(self.D)
        ymax = np.nanmax(self.D)
        print('ymin: {0}, ymax: {1}'.format(ymin, ymax))

        numplots = np.min([n, nrows * ncols])
        plt.figure()

        for n in range(numplots):
            plt.subplot(nrows, ncols, n + 1)
            plt.ylim((ymin - tol, ymax + tol))
            plt.plot(self.L[n, :] + self.S[n, :], 'r')
            plt.plot(self.L[n, :], 'b')
            if not axis_on:
                plt.axis('off')