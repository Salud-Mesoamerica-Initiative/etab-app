'use strict';

import React from 'react';
import {connect} from 'react-redux';
import cx from "classnames";
import TreeUI from '../../lib/react-ui-tree/react-ui-dimension';

class Tree extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div className="tree c-tree">
        <TreeUI
          paddingLeft={10}
          tree={this.props.tree}
          onChange={this.props.onTreeChange}
          onClickNode={this.props.onClickNode}
          isNodeCollapsed={this.isNodeCollapsed}
          renderNode={this.renderNode.bind(this)}
        />
      </div>
    );
  }

  renderNode(node) {
    let id = null;
    if (this.props.activeNode) {
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
}

export default Tree