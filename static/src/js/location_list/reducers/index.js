import {combineReducers} from 'redux';

import * as actions from "../actions/index";

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
const loadChildren = (state = {}, action) => {
  switch (action.type) {
    case actions.REQUEST_NODE_CHILDREN:
    case actions.RECEIVE_NODE_CHILDREN:
      return {
        ...state,
        [action.nodeId]: _updateNode(state[action.nodeId], action)
      }
  }

  return state;
};

// state = state.childrenByNode
const childrenByNode = (state = {}, action)=> {
  switch (action.type) {
    case actions.RECEIVE_NODE_CHILDREN:
      return {
        ...state,
        [action.nodeId]: action.children.map((child) => child.id)
      }
  }
  return state;
};


// state = state.currentNode
const currentNode = (state = null, action)=> {
  switch (action.type) {
    case actions.SELECT_NODE:
      return action.nodeId;
  }

  return state;
};

// state = state.children
const updateChildren = (state = {}, action)=> {
  switch (action.type) {
    case actions.RECEIVE_NODE_CHILDREN:
      let children = {};
      action.children.forEach((child)=> children[child.id] = child);
      return {
        ...state,
        ...children
      }
  }

  return state;
};


const rootReducer = combineReducers({
  tree: loadChildren,
  childrenByNode,
  currentNode,
  children: updateChildren
});

export default rootReducer