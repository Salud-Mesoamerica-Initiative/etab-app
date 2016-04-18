'use strict';

import React from 'react';
import ReactDom from 'react-dom';
import {Modal, Button} from 'react-bootstrap';

import Header from './components/Header.jsx';
import LocationList from './components/LocationList.jsx';
import DynamicModal from './components/DynamicModal.jsx';
import Tree from './components/Tree.jsx';
import {
  SHOW_MODAL, CLOSE_MODAL, CHANGE_TREE, CLICK_DIMENSION,
  ADD_PATH, REMOVE_PATH, JUMP_TO_PATH, UPDATE_LOCATION_LIST
} from './actionUI.jsx';

import {
  ADD_DIMENSION,
  REMOVE_DIMENSION,
  UPDATE_DIMENSION_NAME,
  RETRIEVE_CHILDREN
} from './actionToServer'


require('./app.scss');

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      activeNode: null,
      treeUI: props.treeUI,
      loaded: [0],
      modal: {
        show: false,
        action: null
      },
      locations: {
        itemsByDimension: {}
      },
      path: []
    };
    this.dispatch = this.dispatch.bind(this);
  }

  render() {
    let path = this.state.path;
    let locationList = [];
    if (this.state.activeNode) {
      locationList = this.state.locations.itemsByDimension[this.state.activeNode._id];
      if (locationList) {
        locationList = locationList.items;
      }else{
        locationList = [];
      }
    }
    let locationCount = locationList.length;
    return (
      <div className="app">
        <div className="page-sidebar">
          {
            <Tree
              tree={this.state.treeUI}
              activeNode={this.state.activeNode}
              dispatch={this.dispatch}
            />
          }
        </div>
        <div className="mask"></div>
        <div className="page-content">
          <div className="pc">
            <Header
              path={path}
              activeNode={this.state.activeNode}
              locationCount={locationCount}
              onClick={this.dispatch}
            />
            <LocationList
              items={locationList}
            />
          </div>
        </div>
        <DynamicModal
          obj={this.state.activeNode}
          dispatch={this.dispatch}
          {...this.state.modal}>
        </DynamicModal>
      </div>
    );
  }

  dispatch(action, value) {
    this.setState((oldState)=> {
      let state = _.cloneDeep(oldState);
      let newState = this._dispatch(state, {
        type: action,
        value: value
      });
      return Object.assign({}, newState);
    });
  }

  _dispatch(state, action) {
    switch (action.type) {
      case SHOW_MODAL:
        var modal = this.state.modal;
        modal.show = true;
        modal.action = action.type;
        state.modal = {
          ...this.state.modal,
          action: action.value,
          show: true
        };
        break;
      case CLOSE_MODAL:
        state.modal = {
          ...this.state.modal,
          action: null,
          show: false
        };
        break;
      case CHANGE_TREE:
      case CLICK_DIMENSION:
      case RETRIEVE_CHILDREN:
        state = this._dispatchTree(state, action);
        break;
      case ADD_PATH:
      case REMOVE_PATH:
        // state = this._dispatchPath(state, action);
        break;
      case ADD_DIMENSION:
      case UPDATE_DIMENSION_NAME:
      case REMOVE_DIMENSION:
        state = this._dispatchDimension(state, action);
        break;
      case UPDATE_LOCATION_LIST:
        state = this._dispatchLocation(state, action);
        break;
    }
    return state;
  }

  _dispatchDimension(state, action) {
    let path;
    let treeUI = state.treeUI;
    var refTree = null;
    var walk = (refTree, id) => {
      for (let i = 0; i < refTree.length; i++) {
        if (refTree[i]._id == id) {
          return refTree[i];
        }
      }
    };
    var getNode = (path) => {
      var _tree = null;
      if (!path.length) {
        return treeUI;
      }
      path.forEach((id, index)=> {
        if (index == 0) {
          _tree = walk(treeUI.children, id);
        } else {
          _tree = walk(_tree.children, id);
        }
      });
      return _tree;
    };
    if (action.type == ADD_DIMENSION) {
      let value = action.value;
      path = value._parentIds;
      let children;
      if (path.length) {
        refTree = getNode(path);
        children = refTree.children;
      } else {
        children = treeUI.children;
      }
      value.items.forEach((el)=> {
        let newObj = {
          _id: el._id,
          module: el.name,
          collapsed: true,
          _has_children: el._has_children || false,
          children: []
        };
        children.push(newObj);
      });
    } else if (action.type == REMOVE_DIMENSION) {
      path = action.value._parentIds;
      let idToRemove = action.value._id;
      let f = (child) => child._id != idToRemove;
      // if (path.length == 1) {
      //   treeUI.children = treeUI.children.filter(f);
      // } else {
      refTree = getNode(path);
      refTree.children = refTree.children.filter(f);
      // }
      state.activeNode = null;
    } else if (action.type == UPDATE_DIMENSION_NAME) {
      let idToEdit = action.value._id;
      let f = (node)=> {
        if (node._id == idToEdit) {
          node.module = action.value.name;
        }
        return node;
      };
      refTree = getNode(action.value._parentIds);
      refTree.children = refTree.children.map(f);
      state.activeNode.module = action.value.name;
    }
    state.treeUI = treeUI;

    return state;
  }

  _dispatchPath(state, {type, value}) {
    if (value._id == 0) {
      state.path = [];
      return state;
    }

    switch (type) {
      case ADD_PATH:
        state.path.push(value);
        break;
      case REMOVE_PATH:
        state.path.pop();
        break;
      case JUMP_TO_PATH:
        let index = state.path.filter(el => el._id == value._id);
        if (index.length) {
          state.path.splice(index[0]);
        }
        break;
    }

    return state;
  }

  _dispatchTree(state, action) {
    switch (action.type) {
      case CHANGE_TREE:
        state.treeUI = action.value;
        break;
      case CLICK_DIMENSION:
        state.activeNode = action.value;
        // if (action.value.collapsed) {
        //   state = this._dispatchPath(state, {...action, type: REMOVE_PATH});
        // } else {
        //   state = this._dispatchPath(state, {...action, type: ADD_PATH});
        // }
        this.dispatch(RETRIEVE_CHILDREN, action.value._id);
        break;
      case RETRIEVE_CHILDREN:
        if (action.value) {
          if (state.loaded.indexOf(action.value) == -1) {
            state.loaded.push(action.value);
            let url = Urls['dimension:children-list-ajax'](action.value);
            $.getJSON(url, (data)=> {
              this.dispatch(ADD_DIMENSION, data);
              this.dispatch(UPDATE_LOCATION_LIST, {
                _parentId: action.value,
                items: data.locations.items
              });
            });
          }
        }
        break;
    }

    return state;
  }

  _dispatchLocation(state, action) {
    const value = action.value;
    switch (action.type) {
      case UPDATE_LOCATION_LIST:
        state.locations.itemsByDimension[value._parentId] = {items: value.items};
        break;
    }

    return state;
  }
}

ReactDom.render(
  <App treeUI={window.__data.tree}/>,
  document.getElementById('app')
);