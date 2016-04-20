'use strict';

import React from 'react';
import AddDimension from '../AddDimension';
import {Modal} from 'react-bootstrap';

class RemoveTag extends AddDimension {
  constructor(props) {
    super(props);
    this.state = {
      showModal: false,
      isProcessing: false,
      name: ''
    };

    this.attrs = {
      'icon': 'fa-trash-o',
      'label': 'Delete Tag',
      'id': 'REMOVE_DIMENSION_TAG',
      'title': 'Delete Tag',
      'submitBtnText': 'Delete',
      'submitBtnClassName': 'danger',
      'validate': false
    };
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
    const {name} = this.props.tag;
    return (
      <Modal.Body>
        <span>Are you sure you want to delete <strong>{name}</strong>?</span>
      </Modal.Body>
    )
  }

  onSubmit() {
    const {id} = this.props.tag;
    let params;
    let url = Urls['dimension:delete-tag-ajax']();
    params = {
      id
    };
    this.setState({isProcessing: true});
    $.post(url, params, (data)=> {
      this.setState({isProcessing: false});
      this._closeModal();
      this.props.onSuccess(data.id);
    });
  }

  _closeModal() {
    this.setState({
      showModal: false
    });
  }

}

export default RemoveTag
