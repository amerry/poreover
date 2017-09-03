import numpy as np

# returns (padded_data, sizes)
def pad(data):
    sizes = [len(i) for i in data]
    rows = len(data)
    padded_data = np.zeros((rows,max(sizes)))
    for i, length in enumerate(sizes):
        assert(len(padded_data[i,:length]) == len(np.array(data[i])))
        padded_data[i,:length] = np.array(data[i])
    return((padded_data, sizes))

class data_helper:
    '''
    Simple class to hold data/labels and return consecutive minibatches
    small_batch=True returns the last batch even if it is smaller
    '''
    def __init__(self, X, y, small_batch=True):
        # core data structure
        self.X = np.array(X)
        self.y = np.array(y)

        # pointer to current minibatch
        self.batch_i = 0
        self.epoch = 0

        # fixed options
        self.LENGTH = len(self.X)
        self.SMALL_BATCH = small_batch

    # reset counter for testing purposes
    def reset(self):
        self.batch_i = 0

    # get next minibatch
    def next_batch(self,batch_size):
        if self.batch_i+batch_size < self.LENGTH:
            out_batch = self.batch_i
            self.batch_i += batch_size
            batch_X = self.X[out_batch:out_batch+batch_size]
            batch_y = self.y[out_batch:out_batch+batch_size]
        elif self.SMALL_BATCH:
            out_batch = self.batch_i
            self.batch_i = 0
            self.epoch += 1
            batch_X = self.X[out_batch:]
            batch_y = self.y[out_batch:]
        else:
            self.batch_i = 0
            self.epoch += 1
            batch_X = self.X[:batch_size]
            batch_y = self.y[:batch_size]
        return(batch_X, batch_y)

if __name__ == '__main__':

    def one_hot(n, depth=4):
        v = np.zeros(depth)
        if n > 0:
            v[int(n)-1] = 1
        return(v)

    def random_data(length):
        return [np.random.randint(low=1,high=5, size=np.random.randint(1,11)) for i in range(length) ]

    print("Testing package with random data!")

    # generate some sample data to play with
    data = random_data(100)
    labels = np.random.randint(low=0,high=1,size=100)
    rows = len(data)

    # Pad smaller sequences with 0
    (padded_data, sizes) = pad(data)
    print(padded_data)

    # encode data (pad with zero vector)
    encoded_padded_data = np.array([[one_hot(elem) for elem in row] for row in padded_data])

    print("size should be [length, max_batch_size, alphabet_length]")
    print("size is ", encoded_padded_data.shape)

    print("Testing minibatch iteration")
    dataset = data_helper(encoded_padded_data, labels, small_batch=False)

    # testing minibatch iteration
    BATCH_SIZE = 16
    for i in range(100):
        (X, y) = dataset.next_batch(BATCH_SIZE)
        print(X)
        print("iteration",i+1,"epoch",dataset.epoch, "batch is shape", X.shape, len(y))