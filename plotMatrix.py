import matplotlib.pylab as plt

def plotMatrix(data):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.set_aspect('equal')
    plt.imshow(data, interpolation='nearest', cmap=plt.cm.ocean)
    plt.colorbar()
    plt.show()

def plotLine(line1, line2):
    x = range(len(line1))
    plt.plot(x, line1)
    plt.plot(x, line2, marker='o', linestyle='--', color='r')
    plt.show()
