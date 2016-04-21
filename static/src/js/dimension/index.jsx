import './app.scss';

import React from 'react'
import {render} from 'react-dom'
import {Provider} from 'react-redux';
import configureStore from './store/index';
import App from './containers/App';


let data = window.__data;
let tree = {
  0: {
    id: 0,
    name: 'Locations',
    isFetching: false,
    isCompleted: true
  }
};
data.tree.children.forEach((item)=> {
  tree[item._id] = {
    id: item._id,
    name: item.module,
    dimension_tag: item.dimension_tag,
    code: item.code,
    module: item.module,
    isFetching: false,
    isCompleted: false
  }
});

let state = {
  tags: data.tags,
  treeUI: data.tree,
  tree: tree,
  activeNode: {_id: 0},
  childrenByNode: {0: []}
};

const store = configureStore(state);

render(
  <Provider store={store}>
    <App />
  </Provider>,
  document.getElementById('app')
);
