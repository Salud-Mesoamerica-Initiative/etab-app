import * as actions from '../actions/index';
import _ from 'lodash';
import tree from './treeReducers';
import treeUI from './treeUIReducers';

const activeNode = (state = {_id: 0}, action) => {
  switch (action.type) {
    case actions.CLICK_NODE:
      return action.node;
  }
  return state;
};

const tags = (state = [], action) => {
  switch (action.type){
    case actions.ADD_DIMENSION_TAG:
      return [
        ...state,
        _.omit(action, ['type'])
      ];
    case actions.UPDATE_DIMENSION_TAG:
      return state.map((tag) => {
        if (tag.id == action.id){
          tag = {
            ...tag,
            ..._.omit(action, ['type', 'id'])
          }
        }
        return tag;
      });
    case actions.REMOVE_DIMENSION_TAG:
      return state.filter(tag => tag.id != action.id);

  }
  return state;
};

export default {
  treeUI,
  tree,
  activeNode,
  tags
}