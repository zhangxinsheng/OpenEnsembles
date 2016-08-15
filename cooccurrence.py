import matplotlib.pyplot as plt
import numpy as np
import pylab
import pandas as pd
import scipy.cluster.hierarchy as sch

class coMat:
    '''
        A class that allows you to create and operate on a
        co-occurrence matrix
     '''

    def __init__(self, cObj, data_source_name):
        self.cObj = cObj
        self.data_source_name = data_source_name
        parg = []
        for solution in cObj.labels:
            parg.append(cObj.labels[solution])
        self.parg = parg
        self.data = cObj.dataObj.D[data_source_name]
        self.N = self.data.shape[0]
        self.nEnsembles = len(self.parg)
        co_matrix = self.gather_partitions()
        self.co_matrix = co_matrix

    def gather_partitions(self):
         dim = self.N
         co_matrix = np.zeros(shape=(dim,dim))
         for solution in self.parg:
             co_bin = self.gather_single_partition(solution)
             co_matrix += co_bin
         co_matrixF = co_matrix/self.nEnsembles
         header = self.cObj.dataObj.df.index.get_values()
         co_matrix_df = pd.DataFrame(index=header, data=co_matrixF,
                 columns=header)
         return co_matrix_df

    def gather_single_partition(self, solution):
         dim = len(solution)
         co_matrix = np.zeros(shape=(dim,dim))
         clusterid_list = np.unique(solution)
         #print clusterid_list
         for clusterid in clusterid_list:
             itemindex = np.where(solution==clusterid)
             for i,x in enumerate(itemindex[0][0:]):
                co_matrix[x,x] += 1           
                for j,y in enumerate(itemindex[0][i+1:]):
                     co_matrix[x,y]+=1
                     co_matrix[y,x]+=1
         return co_matrix
    
    def pairwise_list(self):
        #return a new dataframe in list with index equal to the pairs being
        #considered 
        coMat = self.co_matrix
        df = pd.DataFrame(columns=['site_1', 'site_2', 'pairwise'])
        headerList = list(coMat)

        for i in range(0, len(headerList)-1):
            for x in range(i+1, len(headerList)):
                s = pd.Series()
                h = headerList[i]
                j = headerList[x]
                s['pairwise'] = coMat.loc[h,j]
                s['site_1'] = h
                s['site_2'] = j
                s.name = '%s; %s'%(h,j)
                df = df.append(s)
        return df


     
    def plot(self):
        fig = pylab.figure(figsize=(10,10))
        panel3 = fig.add_axes([0,0,1,1])
        panel3.axis('off')
        ax1 = add_subplot_axes(panel3,[0.0,0.3,0.10,.6])
        lnk1 = sch.linkage(self.co_matrix, method='ward',metric='euclidean')
        Z_pp = sch.dendrogram(lnk1, orientation='right')
        idx_pp = Z_pp['leaves']
        ax1 = add_subplot_axes(panel3,[0.0,0.3,0.10,.6])
        ax1.set_yticks([])
        fig.gca().invert_yaxis() # must couple with matshow origin='upper',
        ax1.set_xticks([])
        for side in ['top','right','bottom','left']:
            ax1.spines[side].set_visible(False)

         # plot heatmap
        axmatrix = add_subplot_axes(panel3,[0.28,0.3,0.7,.6])
        hm = self.co_matrix
        hm = hm.ix[idx_pp,idx_pp]
        im = axmatrix.matshow(hm, aspect='auto', origin='upper', cmap='afmhot')
        axmatrix.axis('off')
         # Plot colorbar indicating scale
        axcolor = add_subplot_axes(panel3,[0.28,0.2,0.7,.02]) # [xmin, ymin, dx, and dy]
        h=pylab.colorbar(im, cax=axcolor,orientation='horizontal')
        h.ax.tick_params(labelsize=10)
        h.set_ticks([0,.25,.50,.75,1])
        h.set_ticklabels(['0%','25%','50%','75%','100%'])

        plt.show()



def add_subplot_axes(ax,rect,axisbg='w'):
    fig = plt.gcf()
    box = ax.get_position()
    width = box.width
    height = box.height
    inax_position  = ax.transAxes.transform(rect[0:2])
    transFigure = fig.transFigure.inverted()
    infig_position = transFigure.transform(inax_position)    
    x = infig_position[0]
    y = infig_position[1]
    width *= rect[2]
    height *= rect[3]
    subax = fig.add_axes([x,y,width,height],axisbg=axisbg)

    return subax
