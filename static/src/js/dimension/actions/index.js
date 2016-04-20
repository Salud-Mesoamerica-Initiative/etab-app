export const CLICK_NODE = 'CLICK_NODE';
export const CHANGE_TREE = 'CHANGE_TREE';
export const RECEIVE_DIMENSIONS = 'RECEIVE_DIMENSIONS';
export const ADD_DIMENSION = 'ADD_DIMENSION';
export const REMOVE_DIMENSION = 'REMOVE_DIMENSION';
export const UPDATE_DIMENSION = 'UPDATE_DIMENSION';
export const ADD_DIMENSION_TAG = 'ADD_DIMENSION_TAG';
export const REMOVE_DIMENSION_TAG = 'REMOVE_DIMENSION_TAG';
export const UPDATE_DIMENSION_TAG = 'UPDATE_DIMENSION_TAG';


import {
  RECEIVE_NODE_CHILDREN,
  requestNodeChildren,
  selectNode
} from '../../utils/treeAjax/actions/index';

export {
  REQUEST_NODE_CHILDREN,
  RECEIVE_NODE_CHILDREN,
  selectNode
} from '../../utils/treeAjax/actions/index';


export function clickNode(node) {
  return {
    type: CLICK_NODE,
    node
  }
}

export function changeTreeUI(treeUI) {
  return {
    type: CHANGE_TREE,
    treeUI
  }
}

export function receiveNodeChildren(nodeId, children = []) {
  return {
    type: RECEIVE_NODE_CHILDREN,
    nodeId,
    children
  };
}

export function receiveNodeChildrenDimension(nodeId, children = [], parentIds = []) {
  return {
    type: RECEIVE_DIMENSIONS,
    nodeId,
    children,
    parentIds
  };
}

function fetchChildren(nodeId) {
  return dispatch => {
    dispatch(requestNodeChildren(nodeId));
    var url = Urls['dimension:children-list-ajax'](nodeId);
    $.getJSON(url, function (result) {
      dispatch(receiveNodeChildren(nodeId, result.locations.items));
      dispatch(receiveNodeChildrenDimension(nodeId, result.items, result._parentIds));
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

export function createDimension(attrs){
  return {
    type: ADD_DIMENSION,
    parentIds: attrs._parentIds,
    ...attrs
  }
}

export function updateDimension(attrs){
  return {
    type: UPDATE_DIMENSION,
    ...attrs
  }
}

export function removeDimension(attrs){
  return {
    type: REMOVE_DIMENSION,
    ...attrs
  }
}

export function createDimensionTag(attrs){
  return {
    type: ADD_DIMENSION_TAG,
    ...attrs
  }
}

export function updateDimensionTag(attrs){
  return {
    type: UPDATE_DIMENSION_TAG,
    ...attrs
  }
}

export function removeDimensionTag(id){
  return {
    type: REMOVE_DIMENSION_TAG,
    id
  }
}
