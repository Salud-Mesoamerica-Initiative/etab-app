'use strict';

import React from 'react';
import {connect} from 'react-redux';
import cx from "classnames";
import Toolbar from './Toolbar';

import {
  createDimension,
  updateDimension,
  removeDimension
} from '../../actions/index';

import {Tooltip, OverlayTrigger} from 'react-bootstrap';

class Header extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    const {isFetching, id} = this.props.currentDimension;

    if (isFetching) {
      return null;
    }

    return (
      <div className="c-header">
        <div className="first-line">
          <div className="path pull-left">
            {this.renderPath()}
          </div>
          <div className="actions pull-right">
            <Toolbar
              dimension={this.props.currentDimension}
              onAddDimension={this.props.onAddDimension}
              onUpdateDimension={this.props.onUpdateDimension}
              onRemoveDimension={this.props.onRemoveDimension}
            />
          </div>
        </div>
        <div className="clearfix">
          <div className="pull-right text-muted locations-count">
            {
              (id == 0 || this.props.childrenCount == 0)
                ? null
                : <small>{this.props.childrenCount} locations</small>
            }
          </div>
        </div>
      </div>
    );
  }

  renderPath() {
    if (this.props.currentDimension.id != 0) {
      return <strong>{this.props.currentDimension.module}</strong>;
    }
    return null;
  }
}

const mapStateToProps = (state) => {
  const {currentNode, tree, childrenByNode} = state;
  return {
    currentDimension: tree[currentNode] || tree[0],
    childrenCount: (childrenByNode[currentNode] || []).length
  }
};

const mapDispatchToProps = (dispatch) => {
  return {
    onAddDimension: (attrs) => {
      dispatch(createDimension(attrs))
    },
    onUpdateDimension: (attrs) => {
      dispatch(updateDimension(attrs))
    },
    onRemoveDimension: (attrs) => {
      dispatch(removeDimension(attrs))
    }
  }
};

export default connect(mapStateToProps, mapDispatchToProps)(Header);