'use strict';

import React from 'react';
import cx from "classnames";
import uuid from 'node-uuid';

import {Tooltip, OverlayTrigger} from 'react-bootstrap';
import {ADD_DIMENSION, REMOVE_DIMENSION, UPDATE_DIMENSION_NAME} from '../actionToServer';
import {SHOW_MODAL} from '../actionUI.jsx';

class Header extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.actions = [{
      'icon': 'fa-plus',
      'label': 'Add dimension',
      'action': ADD_DIMENSION,
      'nodeRequired': false
    }, {
      'icon': 'fa-pencil',
      'label': 'Edit dimension',
      'action': UPDATE_DIMENSION_NAME,
      'nodeRequired': true
    }, {
      'icon': 'fa-trash-o',
      'label': 'Remove dimension',
      'action': REMOVE_DIMENSION,
      'nodeRequired': true
    }]
  }

  render() {
    return (
      <div className="c-header">
        <div className="first-line">
          <div className="path pull-left">
            {this.renderPath()}
          </div>
          <div className="actions pull-right">
            {this.renderActions()}
          </div>
        </div>
        <div className="clearfix">
          <div className="pull-right text-muted locations-count">
            <small>{this.props.locationCount} locations</small>
          </div>
        </div>
        <div className="list-header">
          <div className="prop name">
            <span>Name</span>
          </div>
          <div className="prop parent">
            <span>Dimension</span>
          </div>
        </div>
      </div>
    );
  }

  renderPath() {
    if (this.props.activeNode) {
      return <strong>{this.props.activeNode.module}</strong>;
    }
    return null;
    // let path = this.props.path;
    // let defaultPath = {module: 'Locations', root: true};
    // if (!path.length) {
    //   path = [defaultPath];
    // }else{
    //   path = [
    //     defaultPath, ...path
    //   ];
    // }
    //
    // return path.map((el, index, list)=> {
    //     let c;
    //     if (index == list.length - 1) {
    //       c = <span>{el.module}</span>
    //     } else {
    //       c = [<a href="#" key={uuid.v1()}>{el.module}</a>,
    //         <i className="fa fa-angle-right" key={uuid.v1()}></i>];
    //     }
    //     return <span key={uuid.v1()}>{c}</span>
    //   });
  }

  renderActions() {
    let actionsList = this.actions.filter((a)=> {
      if (a.nodeRequired) {
        if (!this.props.activeNode || this.props.activeNode._id == 0) {
          return false;
        }
        return true;
      } else {
        return true;
      }
    });
    const actions = actionsList.map((el)=> {
      const tooltip = (
        <Tooltip id={`${el.action}`}>{el.label}</Tooltip>
      );
      return (
        <li key={`${el.action}`}>
          <OverlayTrigger placement="top" overlay={tooltip}>
            <a href="#" onClick={
                        ()=> this.props.onClick(SHOW_MODAL, el.action)
                        }>
              <i className={cx('fa', 'text-primary', el.icon)}></i>
            </a>
          </OverlayTrigger>
        </li>
      );
    });
    return (<ul className="list-inline">{actions}</ul>);
  }
}

export default Header;