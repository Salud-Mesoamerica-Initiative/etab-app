export const REQUEST_NODE_CHILDREN = 'REQUEST_NODE_CHILDREN';
export const RECEIVE_NODE_CHILDREN = 'RECEIVE_NODE_CHILDREN';
export const SELECT_NODE = 'SELECT_NODE';

export function requestNodeChildren(nodeId) {
  return {
    type: REQUEST_NODE_CHILDREN,
    nodeId
  };
}

export function selectNode(nodeId) {
  return {
    type: SELECT_NODE,
    nodeId
  };
}

export function receiveNodeChildren(nodeId, children = []) {
  return {
    type: RECEIVE_NODE_CHILDREN,
    nodeId,
    children
  };
}

function fetchChildren(nodeId) {
  return dispatch => {
    dispatch(requestNodeChildren(nodeId));
    var url = Urls['dimension:location-list-ajax'](nodeId);
    $.getJSON(url, function (result) {
      dispatch(receiveNodeChildren(nodeId, result.items))
    });
  }
}

function shouldFetchChildren(state, nodeId) {
  const node = state.tree[nodeId];
  if (!node) {
    return true
  } else if (node.isFetching) {
    return false
  } else {
    return !node.isCompleted
  }
}

export function fetchChildrenIfNeeded(nodeId) {
  return (dispatch, getState) => {
    if (shouldFetchChildren(getState(), nodeId)) {
      return dispatch(fetchChildren(nodeId));
    }
  }
}