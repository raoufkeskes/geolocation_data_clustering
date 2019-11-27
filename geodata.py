
# data processing
import numpy as np
import matplotlib.pyplot as plt

# models
from sklearn.cluster import KMeans , SpectralClustering , AgglomerativeClustering

# utils
import os
from matplotlib.colors import LinearSegmentedColormap


class geodata:
    '''
        a dedicated class to geolocation data ( longitude , latitude )
    '''
    def __init__(self, X, map_path=None):

        '''
        X : data array of shape ( N , 2 )  where columns are  :  ( longitude , latitude )
        map_path : file containing the map image on which we will scatter/plot  our geodata
        '''

        self.X = X
        self.map = plt.imread(map_path) if (map_path is not None) else None
        self.model = None
        self.n_clusters = 2
        # box frame for the map to fit the background correctly : ( left , right  , bottom , top )
        h = 0.005
        self.box = X[:, 0].min() - h , X[:, 0].max() + h , X[:, 1].min() - h , X[:, 1].max() + h

    # getters
    def getModel( self ) :
        return self.model

    def apply_clustering(self, model ="kmeans" , K=2 , random_seed=0 ):
        '''
        :param model: clustering model ( kmeans | spectral | agglo )   , agglo stands for agglomerative
        :param K: number of clusters
        :param random_seed: random seed for random numbers generations
        '''

        # Keep K between 1 and N ( number of examples )
        if (K > self.X.shape[0]):
            K = self.X.shape[0]
        elif (K < 1):
            K = 1

        self.n_clusters = K

        if (  model =="kmeans" ) :
            self.model = KMeans( n_clusters=K , random_state=random_seed ).fit(self.X)

        elif (  model == "spectral" ) :
            self.model = SpectralClustering( n_clusters=K , random_state=random_seed , affinity="laplacian" ).fit(self.X)

        elif ( model == "agglo" ) :
            self.model = AgglomerativeClustering( n_clusters=K , linkage='complete' ).fit(self.X)

        else  :  raise Exception ("the clustering model should be 'kmeans'|'spectral'|'agglo' or None for no clustering and nothing else ")


    def plot_data(self , plot_type="scatter", map_transparency=0.4 , figsize=(16, 10) , save=True , map_name="Brisbane" ):

        '''
        :param plot_type  : - will have no effect if clustering is None
                            - determines type of the clustering plot "scatter" | "regions" | "distances"
        :param map_transparency : float in range (0,1) , to determine the transparency
        :param figsize: the plot figure size , a tuple of int ( width , height ) proportion
        :param save: a boolean to choose to save the figures outputs on './outputs/specific_name.png'  or not
        :param map_name: tha name of the map appearing on the figures title

        it plots the geodata according to the previous params
        '''

        ###########      general plots configuration for all types of plots    ##############
        fig, ax = plt.subplots(figsize=figsize)
        # => customized title
        map_str = " "  if (map_name is None) else "on '" + map_name + "' map"
        plot_str = " simple plot " if ( self.model is None ) else " clustering plot "
        model_str = "" if ( self.model is None ) else " using "+self.model.__class__.__name__+" with n_clusters = "+str(self.n_clusters)
        title = 'Geolocation data' + plot_str + map_str + model_str

        ax.set_title(title)
        ax.set_ylabel('Latitude')
        ax.set_xlabel('Longitude')

        # =>  background Map
        if (map_transparency is not None and map_transparency > 0):
            # alpha for transparency
            ax.imshow(self.map, extent=self.box, alpha=map_transparency, aspect='auto')


        ######################  plot different types of visualizations ########################

        # simple scatter
        if ( self.model is None ):
            ax.scatter(self.X[:, 0], self.X[:, 1])
        else:

            # labels
            if hasattr( self.model , 'labels_'):
                labels = self.model.labels_.astype(np.int)
            else:
                labels = self.model.predict(self.X)

            # preparing colors etc ...
            if ( self.n_clusters <= 5):
                colors = ['#0000ff', '#ff3300', '#00cc66', '#cc0099', '#00ffcc']
            else:
                # generate random colors for n_clusters
                colors = np.random.rand( self.n_clusters , 3)

            if (plot_type == "scatter"):

                for cluster, color in zip(range( self.n_clusters ), colors):
                    ax.scatter(self.X[labels == cluster, 0], self.X[labels == cluster, 1], color=color)

                    if isinstance( self.model , KMeans )  :
                        centroids = self.model.cluster_centers_
                        ax.scatter( centroids [cluster, 0], centroids[cluster, 1], color=color, marker="o",
                               edgecolors="black" , s=300)

            elif (plot_type == "regions"):

                if not isinstance(self.model, KMeans ):
                    raise Exception("It is impossible to plot regions for this model , we cannot retrieve the cluster membership of new data ")

                #  PLOT REGIONS
                h = (self.box[1] - self.box[0]) / 100
                xx, yy = np.meshgrid(np.arange(self.box[0], self.box[1], h), np.arange(self.box[2], self.box[3], h))

                # Obtain labels for each point in mesh. Use last trained model.
                Z = self.model.predict(np.c_[xx.ravel(), yy.ravel()])

                Z = Z.reshape(xx.shape)

                my_color_map = LinearSegmentedColormap.from_list("my_color_map", colors)
                plt.imshow(Z, interpolation='nearest',
                           extent=self.box,
                           cmap=my_color_map,
                           aspect='auto', origin='lower', alpha=0.4)

                # scatter points
                for cluster, color in zip(range(self.n_clusters), colors):
                    ax.scatter(self.X[labels == cluster, 0], self.X[labels == cluster, 1], cmap=my_color_map)

                # scatter centroids if Kmeans
                if isinstance(self.model, KMeans):
                    centroids = self.model.cluster_centers_
                    plt.scatter(centroids[:, 0], centroids[:, 1],
                            marker='x', s=400, linewidths=5,
                            color='black', zorder=10)


            elif (  plot_type == "distances" ):

                if isinstance(self.model, KMeans):
                    centroids = self.model.cluster_centers_
                    for cluster, color in zip(range(len(centroids)), colors):
                        ax.scatter(self.X[labels == cluster, 0], self.X[labels == cluster, 1], color=color)
                        ax.scatter(centroids[cluster, 0], centroids[cluster, 1], color=color, marker="o",
                                   edgecolors="blue", s=300)

                        for x in self.X[labels == cluster]:
                            plt.plot([centroids[cluster, 0], x[0]], [centroids[cluster, 1], x[1]], color=color)
                else :
                    raise Exception (" distances plot requires clustering to be 'kmeans' to plot distances to centroids ")

        ################################  save figures  #######################################
        if (save == True):
            if (not os.path.isdir("./outputs")):
                os.makedirs("./outputs/")
            plt.savefig('outputs/'+title+'.png')

        plt.show()