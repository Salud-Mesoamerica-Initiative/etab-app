'use strict';

import React from 'react';
import AddDimension from '../AddDimension';
import {Modal, Input} from 'react-bootstrap';


class UpdateTag extends AddDimension {
  constructor(props) {
    super(props);
    this.state = {
      showModal: false,
      isProcessing: false,
      name: ''
    };

    this.attrs = {
      'icon': 'fa-edit',
      'label': 'Edit Tag',
      'id': 'EDIT_DIMENSION_TAG',
      'title': 'Edit Tag',
      'submitBtnText': 'Save',
      'validate': true
    };
  }


  setTagAttrs(props) {
    const {name} = props.tag;
    this.setState({
      name: name
    });
  }

  componentDidMount() {
    this.setTagAttrs(this.props);
  }

  componentWillReceiveProps(nextProps) {
    if (!this.state.showModal) {
      this.setTagAttrs(nextProps);
    }
  }

  renderModalHeader() {
    const {title} = this.attrs;
    return (
      <Modal.Header closeButton>
        <Modal.Title>{`${title} - ${this.props.tag.name}`}</Modal.Title>
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
    let url = Urls['dimension:update-tag-ajax']();
    params = {
      name: this.state.name,
      id: this.props.tag.id
    };
    this.setState({isProcessing: true});
    $.post(url, params, (data)=> {
      this.props.onSuccess(data);
      this._closeModal();
      this.setState({isProcessing: false});
    });
  }

  _closeModal() {
    this.setState({
      showModal: false
    });
  }

}

export default UpdateTag
