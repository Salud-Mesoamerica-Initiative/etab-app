'use strict';

import React from 'react';
import {Modal, Button} from 'react-bootstrap';
import AddDimension from './AddDimension';


class RemoveDimension extends AddDimension {
  constructor(props) {
    super(props);
    this.state = {
      showModal: false,
      isProcessing: false

    };

    this.attrs = {
      'icon': 'fa-trash-o',
      'label': 'Delete dimension',
      'id': 'REMOVE_DIMENSION',
      'title': 'Delete Dimension',
      'submitBtnText': 'Delete',
      'submitBtnClassName': 'danger',
      'validate': false
    };
  }

  renderModalBody() {
    const {name} = this.props.dimension;
    return (
      <Modal.Body>
        <span>Are you sure you want to delete <strong>{name}</strong>?</span>
      </Modal.Body>
    )
  }

  onSubmit() {
    const {id} = this.props.dimension;
    if (id != 0) {
      let params;
      let url = Urls['dimension:delete-ajax']();
      params = {
        id
      };
      this.setState({isProcessing: true});
      $.post(url, params, (data)=> {
        this.setState({isProcessing: false});
        this._closeModal();
        this.props.onSuccess(data);
      });
    }
  }
}

export default RemoveDimension;