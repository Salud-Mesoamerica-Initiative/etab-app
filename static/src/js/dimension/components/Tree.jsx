'use strict';

import React from 'react';
import cx from "classnames";
var Tree = require('../../lib/react-ui-tree/react-ui-dimension');
import {CLICK_DIMENSION, CHANGE_TREE} from '../actionUI.jsx';

class Tree1 extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      active: null
    };
  }

  render() {
    return (
      <div className="tree c-tree">
        <Tree
          paddingLeft={10}
          tree={this.props.tree}
          onChange={this.handleChange.bind(this)}
          onClickNode={this.onClickNode.bind(this)}
          isNodeCollapsed={this.isNodeCollapsed}
          renderNode={this.renderNode.bind(this)}
        />
      </div>
    );
  }

  renderNode(node) {
    let id = null;
    if (this.props.activeNode){
      id = this.props.activeNode._id;
    }
    return (
      <span
        className={cx('node', {
                'is-active': node._id === id})}>
        {node.module}
      </span>
    );
  }

  onClickNode(node) {
    this.setState({
      active: node
    });
    this.props.dispatch(CLICK_DIMENSION, node);
  }


  handleChange(tree) {
    this.props.dispatch(CHANGE_TREE, tree);
  }
}

export default Tree1;