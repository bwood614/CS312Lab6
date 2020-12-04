from TSPClasses import *

# unit test for BBState.reduceMatrix()
def reduceStateTest():
    expected_reducedState = BBState(15, [], [[np.inf, 4, 0, 8], [0, np.inf, 3, 10], [0, 3, np.inf, 0], [6, 0, 2, np.inf]])

    initial_state = BBState(0, [], [[np.inf, 7, 3, 12], [3, np.inf, 6, 14], [5, 8, np.inf, 6], [9, 3, 5, np.inf]])
    initial_state.reduceMatrix()

    try:
        assert initial_state.lower_bound == expected_reducedState.lower_bound
        assert initial_state.state_matrix == expected_reducedState.state_matrix
    except:
        print('reduceState algorithm did not work correctly')

def expandTest():
    expected_children = [
        BBState(24, [], [[np.inf, np.inf, np.inf, np.inf], [np.inf, np.inf, 0, 7], [0, np.inf, np.inf, 0], [4, np.inf, 0, np.inf]]),
        BBState(15, [], [[np.inf, np.inf, np.inf, np.inf], [0, np.inf, np.inf, 10], [np.inf, 3, np.inf, 0], [6, 0, np.inf, np.inf]]),
        BBState(25, [], [[np.inf, np.inf, np.inf, np.inf], [0, np.inf, 1, np.inf], [0, 3, np.inf, np.inf], [np.inf, 0, 0, np.inf]])
    ]

    initial_state = BBState(15, [], [[np.inf, 4, 0, 8], [0, np.inf, 3, 10], [0, 3, np.inf, 0], [6, 0, 2, np.inf]])
    actual_children = initial_state.expand()
    for i in range(3):
        try:
            assert actual_children[i].lower_bound == expected_children[i].lower_bound
            assert actual_children[i].state_matrix == expected_children[i].state_matrix
        except:
            print('expand algorithm did not work correctly')

if __name__ == '__main__':

    reduceStateTest()

    expandTest()
