import argparse
import pandas as pd
from   geodata import geodata



def main (params) :

    print (params.path)


    # read the data
    try :
        data_df = pd.read_json(args.path)
    except ValueError  :
        print ("Value Error : json data file not found")
        exit(1)

    else :
        # create a geo_data object
        geo_data = geodata ( X = data_df.loc[:, ['longitude', 'latitude']].values ,  map_path=params.map_path )

        # apply a corresponding clustering if asked from the user
        if ( params.clustering is not None ) :
            geo_data.apply_clustering( model=params.clustering.lower()  , K = params.n_clusters , random_seed=params.random_seed )

        # plot the result
        geo_data.plot_data( params.plot_type , params.map_transparency , (16, 10) , params.save , params.map_name )

        # kmeans have centroids by definition
        clustering_model = geo_data.getModel()
        if ( params.clustering == "kmeans" and clustering_model is not None ) :
            print("Inertia : " , clustering_model.inertia_)
            print ( "centroids are : \n", geo_data.getModel().cluster_centers_ )


if __name__ == '__main__':

    """
    cmd parameters : a simple API 
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--path'          , default = "data/Brisbane_CityBike.json" , type=str, metavar='DIR', help='path to geodata JSON dataset')
    parser.add_argument('--clustering'    , default = None                          , type=str, metavar='CLUST', help='apply a clustering  or just plot the data')
    parser.add_argument('--n_clusters'    , default = 2                             , type=int, metavar='N',help='number of clusters')
    parser.add_argument('--plot_type'     , default = "scatter"                     , type=str, metavar='PLT_TYPE', help='3 clustering plot type("scatter"|"regions"|"distances")')
    parser.add_argument('--random_seed'   , default = 0                             , type=int, metavar='SEED', help='random seed for reproducibility ')
    parser.add_argument('--save'          , default = True                          , type=bool , metavar='SAVE', help='a boolean to determine if you want to save the figure on "outputs" directory ')
    parser.add_argument('--map_path'      , default = "images/map.png"              , type=str, metavar='DIR', help='path to background image map file ')
    parser.add_argument('--map_transparency', default=0.4 , type=float , metavar='TRS', help='float in range (0,1) , to determine the transparency')
    parser.add_argument('--map_name', default="Brisbane" , type=str , metavar='MAPNAME', help='tha name of the map appearing on the figures title')


    args = parser.parse_args()
    main(args)