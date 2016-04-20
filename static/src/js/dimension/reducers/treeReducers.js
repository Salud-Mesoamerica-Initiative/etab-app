import * as actions from '../actions/index';
import _ from 'lodash';

const _updateNode = (state, action)=> {
  switch (action.type) {
    case actions.REQUEST_NODE_CHILDREN:
      return {
        ...state,
        isFetching: true,
        isCompleted: false
      };
    case actions.RECEIVE_NODE_CHILDREN:
      return {
        ...state,
        isFetching: false,
        isCompleted: true
      };
  }

  return state;
};

// state = state.tree;
const updateTree = (state = {}, action) => {
  switch (action.type) {
    case actions.ADD_DIMENSION:
      return {
        ...state,
        [action._id]: {
          id: action._id,
          module: action.name,
          isFetching: false,
          isCompleted: false,
          ..._.omit(action, ['type', '_id'])

        }
      };
    case actions.UPDATE_DIMENSION:
      return {
        ...state,
        [action._id]: {
          ...state[action._id], ..._.omit(action, ['type', '_id'])
        }
      };
    case actions.REMOVE_DIMENSION:
      var treeUI = _.cloneDeep(state);
      delete treeUI[action._id];
      return treeUI;
  }
  return state;
};

// state = state.tree;
const loadChildren = (state = {}, action) => {
  switch (action.type) {
    case actions.REQUEST_NODE_CHILDREN:
    case actions.RECEIVE_NODE_CHILDREN:
      return {
        ...state,
        [action.nodeId]: _updateNode(state[action.nodeId], action)
      };
    case actions.RECEIVE_DIMENSIONS:
      var tree = _.cloneDeep(state);
      action.children.forEach((obj)=>{
        tree[obj._id] = {
          ...tree[obj._id],
          module: obj.name,
          id: obj._id,
          ..._.omit(obj, ['_id'])
        }
      });
      return tree;
    case actions.ADD_DIMENSION:
    case actions.UPDATE_DIMENSION:
    case actions.REMOVE_DIMENSION:
      return updateTree(state, action);
  }

  return state;
};

export default loadChildren;