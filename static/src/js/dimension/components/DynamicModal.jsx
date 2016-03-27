'use strict';

import React from 'react';
import _ from 'lodash';
import {Modal, Button, Input} from 'react-bootstrap';
import {CLOSE_MODAL} from '../actionUI.jsx';
import {
  ADD_DIMENSION,
  REMOVE_DIMENSION,
  REMOVE_LOCATION,
  UPDATE_DIMENSION_NAME
} from '../actionToServer';


class DynamicModal extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      value: '',
      update: false
    };
    this.label = {};
    this.label[`${UPDATE_DIMENSION_NAME}`] = 'Edit';
    this.label[`${ADD_DIMENSION}`] = 'Create';
    this.label[`${REMOVE_DIMENSION}`] = 'Delete';
    this.simpleInput = [ADD_DIMENSION, UPDATE_DIMENSION_NAME];
    this.confirmation = [REMOVE_DIMENSION];
    this.onClose = this.onClose.bind(this);
  }

  componentWillReceiveProps(nextProps){
    if(nextProps.action == UPDATE_DIMENSION_NAME && this.state.value=='' && !this.state.update){
      this.setState({value: nextProps.obj.module});
    }

    if(nextProps.show && !this.state.update){
      this.setState({update: true});
    }
  }

  render() {
    let {obj, show, action} = this.props;
    let title;
    if (!obj || obj._id == 0) {
      title = 'Create dimension'
    } else {
      title = [this.label[action], 'dimension'].join(" ");
    }
    return (
      <Modal
        show={show}
        bsSize="small"
        aria-labelledby="contained-modal-title-sm"
        onHide={this.onClose}>
        <Modal.Header closeButton>
          <Modal.Title>{title}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {this.renderBody(action, obj)}
        </Modal.Body>
        <Modal.Footer>
          {this.renderFooter(action, obj)}
        </Modal.Footer>
      </Modal>
    );
  }

  _in(array, key) {
    return _.indexOf(array, key) != -1;
  }

  renderBody(action, obj) {
    if (this._in(this.simpleInput, action)) {
      let text = [this.label[action], 'dimension'].join(" ");
      let subtitle;
      if (!obj || obj._id == 0) {
        subtitle = "";
      } else {
        subtitle = obj.module;
      }
      return (
        <div>
          <small className="text-muted">{subtitle}</small>
          <Input
            type="text"
            value={this.state.value}
            label={text}
            ref="input"
            groupClassName="group-class"
            labelClassName="label-class"
            onChange={this.handleChange.bind(this)}/>
        </div>
      );
    } else if (this._in(this.confirmation, action)) {
      return (
        <span>Are you sure you want to delete <strong>{obj.module}</strong>?</span>
      );
    }
    return null;
  }

  renderFooter(action, obj) {
    let footer;
    const closeBtn = <Button onClick={this.onClose}>Close</Button>;
    if (this._in(this.simpleInput, action)) {
      let value;
      try {
        value = this.refs.input.getValue().trim();
      } catch (e) {
        value = "";
      }
      footer = (
        <Button
          bsStyle="primary"
          disabled={value==''}
          onClick={this.onOkClick.bind(this)}>
          {this.getButtonText(action)}
        </Button>
      );
    } else {
      footer = (
        <Button
          bsStyle="primary"
          onClick={this.onOkClick.bind(this)}>
          {this.getButtonText(action)}
        </Button>
      );
    }
    return (
      <div>
        {closeBtn}
        {footer}
      </div>
    );
  }

  getButtonText(action) {
    let text;
    const deleteAction = [REMOVE_DIMENSION, REMOVE_LOCATION];

    if (this._in(deleteAction, action)) {
      text = 'Delete';
    } else {
      text = 'Save'
    }

    return text;

  }

  onClose() {
    this.setState({
      update: false,
      value: ''
    });
    this.props.dispatch(CLOSE_MODAL, null);
  }

  handleChange() {
    this.setState({
      value: this.refs.input.getValue()
    });
  }

  onOkClick() {
    let params = {};
    let url = '';
    if (this.props.action == ADD_DIMENSION) {
      url = Urls['dimension:create-ajax']();
      let parentId = null;
      if (this.props.obj) {
        parentId = this.props.obj._id;
      }
      params = {
        name: this.refs.input.getValue(),
        parent_id: parentId
      };
    } else if (this.props.action == UPDATE_DIMENSION_NAME) {
      url = Urls['dimension:update-ajax']();
      params = {
        name: this.refs.input.getValue(),
        id: this.props.obj._id,
        type: 'NAME'
      };
    } else if (this.props.action == REMOVE_DIMENSION) {
      url = Urls['dimension:delete-ajax']();
      params = {
        id: this.props.obj._id
      };
    }

    $.post(url, params, (data)=> {
      this._action(data, this.props.action);
    });
  }

  _action(data, action) {
    this.onClose();
    this.props.dispatch(action, data);
  }
}

export default DynamicModal;