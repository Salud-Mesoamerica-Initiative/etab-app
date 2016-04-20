"use strict";

import React from 'react';
import {connect} from 'react-redux';

import { clickNode, changeTreeUI, selectNode, fetchChildrenIfNeeded } from '../actions/index';
import Tree from '../components/Tree';
import Table from '../components/LocationList';
import Header from '../components/Header/index';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.onClickNode = this.onClickNode.bind(this);
    this.onTreeChange = this.onTreeChange.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.currentNode !== this.props.currentNode) {
      const {dispatch, currentNode} = nextProps;
      dispatch(fetchChildrenIfNeeded(currentNode));
    }
  }

  render() {
    return (
      <div className="app">
        <div className="page-sidebar">
          {
            <Tree
              tree={this.props.treeUI}
              activeNode={this.props.activeNode}
              onClickNode={this.onClickNode}
              onTreeChange={this.onTreeChange}
            />
          }
        </div>
        <div className="mask"></div>
        <div className="page-content">
          <div className="pc">
            <Header />
            {(!this.props.currentNode ? null: <Table items={this.props.locations} />)}
          </div>
        </div>
      </div>
    )
  }

  onClickNode(node) {
    this.props.dispatch(clickNode(node));
    this.props.dispatch(selectNode(node._id));
  }

  onTreeChange(tree) {
    this.props.dispatch(changeTreeUI(tree));
  }
}

function mapStateToProps(state) {
  const {currentNode, childrenByNode, children} = state;

  return {
    ...state,
    locations: (childrenByNode[currentNode] || []).map((id) => children[id])
  };
}

export default connect(mapStateToProps)(App);