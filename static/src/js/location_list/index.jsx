import './main.css';

import React from 'react'
import { render } from 'react-dom'
import { Provider } from 'react-redux';
import configureStore from '../utils/treeAjax/store/configureStore';
import * as actions from '../utils/treeAjax/actions/index';
import App from './components/App';

let data = window.__data;


let tree = {};
data.forEach((item)=> {
  tree[item.id] = {
    ...item,
    isFetching: false,
    isCompleted: false
  }
});

let state = {
  tree: tree
};

const store = configureStore(state);

$('#tree')
  .on('changed.jstree', function (e, data) {
    if (data.action == 'select_node'){
      store.dispatch(actions.selectNode(data.node.id));
      store.dispatch(actions.fetchChildrenIfNeeded(data.node.id));
    }
  }).jstree({
  'core': {
    'data': data
  }
});

render(
  <Provider store={store}>
    <App />
  </Provider>,
  document.getElementById('section-')
);
