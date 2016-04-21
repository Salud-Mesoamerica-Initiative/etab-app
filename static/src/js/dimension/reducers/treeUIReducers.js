import * as actions from '../actions/index';
import _ from 'lodash';

const walk = (refTree, id) => {
  for (let i = 0; i < refTree.length; i++) {
    if (refTree[i]._id == id) {
      return refTree[i];
    }
  }
};

const _getNode = (treeUI, path) => {
  if (!path.length) {
    return treeUI;
  }

  let _tree = null;
  path.forEach((id, index)=> {
    if (index == 0) {
      _tree = walk(treeUI.children, id);
    } else {
      _tree = walk(_tree.children, id);
    }
  });
  return _tree;
};

// state = state.treeUI;
const updateTreeUI = (state = {}, action)=> {
  switch (action.type) {
    case actions.RECEIVE_DIMENSIONS:
      let targetNode;
      let targetChildren;
      let path = action.parentIds;
      let children = action.children;
      let treeUI = _.cloneDeep(state);
      targetNode = _getNode(treeUI, path);
      targetChildren = targetNode.children;
      children.forEach((el)=> {
        let newObj = {
          _id: el._id,
          module: el.name,
          collapsed: true,
          _has_children: el._has_children || false,
          children: [],
          ..._.omit(el, ['type', '_id', 'items'])
        };
        targetChildren.push(newObj);
      });

      return treeUI;
    case actions.CHANGE_TREE:
      return action.treeUI;
    case actions.ADD_DIMENSION:
    case actions.UPDATE_DIMENSION:
    case actions.REMOVE_DIMENSION:
      return updateDimension(state, action);
  }

  return state;
};

const updateDimension = (state = {}, action) => {
  switch (action.type) {
    case actions.ADD_DIMENSION:
      let targetNode;
      let targetChildren;
      let path = action.parentIds;
      let treeUI = _.cloneDeep(state);
      targetNode = _getNode(treeUI, path);
      targetChildren = targetNode.children;
      let newObj = _.omit(action, ['type', 'items', 'parentIds']);
      newObj = {
        ...newObj,
        module: action.name,
        collapsed: true,
        _has_children: action._has_children || false,
        children: []
      };
      targetChildren.push(newObj);
      return treeUI;
    case actions.UPDATE_DIMENSION:
      var treeUI = _.cloneDeep(state);
      var idToEdit = action._id;
      var f = (node)=> {
        if (node._id == idToEdit) {
          node.module = action.name;
        }
        return node;
      };
      var refTree = _getNode(treeUI, action._parentIds);
      refTree.children = refTree.children.map(f);
      return treeUI;
    case actions.REMOVE_DIMENSION:
      var treeUI = _.cloneDeep(state);
      var path = action._parentIds;
      var idToRemove = action._id;
      var f = (child) => child._id != idToRemove;
      var refTree = _getNode(treeUI, path);
      refTree.children = refTree.children.filter(f);
      return treeUI;
  }
  return state;
};

export default updateTreeUI;