'use strict';

import React from 'react';
import AddDimension from '../AddDimension';
import {Modal, Input, InputBase} from 'react-bootstrap';
import cx from "classnames";


class CreateTag extends AddDimension {
  constructor(props) {
    super(props);
    this.state = {
      showModal: false,
      isProcessing: false,
      name: ''
    };

    this.attrs = {
      'icon': 'fa-plus',
      'label': 'Create Tag',
      'id': 'CREATE_DIMENSION_TAG',
      'title': 'Create Tag',
      'submitBtnText': 'Save',
      'validate': true
    };
  }


  render() {
    return (
      <div className="text-right">
        <button onClick={this.onShowModal} className="btn btn-default btn-sm">
          <i className={cx('fa', this.attrs.icon)}></i> Create
        </button>
        {this.renderModal()}
      </div>
    );
  }

  renderModalHeader() {
    const {title} = this.attrs;
    return (
      <Modal.Header closeButton>
        <Modal.Title>{`${title}`}</Modal.Title>
      </Modal.Header>
    );
  }

  renderModalBody() {
    return (
      <Modal.Body>
        <div>
          <Input
            type="text"
            value={this.state.name}
            label="Name"
            ref="name"
            groupClassName="group-class"
            labelClassName="label-class"
            onChange={(e) => this.onTextChange(e, 'name')}/>
        </div>
      </Modal.Body>
    )
  }

  onSubmit() {
    let params;
    let url = Urls['dimension:create-tag-ajax']();
    params = {
      name: this.state.name
    };
    this.setState({isProcessing: true});
    $.post(url, params, (data)=> {
      this.props.onSuccess(data);
      this._closeModal();
      this.setState({isProcessing: false});
    });
    console.log('Add Tag');
  }
}

export default CreateTag
