'use strict';

import React from 'react';
import {Tooltip, OverlayTrigger, Modal, Button, Input} from 'react-bootstrap';
import cx from "classnames";


class AddDimension extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showModal: false,
      name: '',
      code: '',
      dimension_tag: '',
      isProcessing: false,
      errors: {}

    };

    this.attrs = {
      'icon': 'fa-plus',
      'label': 'Create dimension',
      'id': 'ADD_DIMENSION',
      'title': 'Create Dimension',
      'validate': true
    };

    this.onShowModal = this.onShowModal.bind(this);
    this.onCloseModal = this.onCloseModal.bind(this);
    this.onSubmit = this.onSubmit.bind(this);
    this.onTextChange = this.onTextChange.bind(this);
    this._onSubmitError = this._onSubmitError.bind(this);
  }

  render() {
    const tooltip = (
      <Tooltip id={`${this.attrs.id}`}>{this.attrs.label}</Tooltip>
    );
    return (
      <li>
        <OverlayTrigger placement="top" overlay={tooltip}>
          <a href="#" onClick={this.onShowModal}>
            <i className={cx('fa', 'text-primary', this.attrs.icon)}></i>
          </a>
        </OverlayTrigger>
        {this.renderModal()}
      </li>
    );
  }

  renderModal() {
    if (this.state.showModal) {
      return (
        <Modal
          show={this.state.showModal}
          aria-labelledby="contained-modal-title-sm"
          onHide={this.onCloseModal}>
          {this.renderModalHeader()}
          {this.renderModalBody()}
          {this.renderModalFooter()}
        </Modal>
      );
    } else {
      return null;
    }
  }

  renderModalHeader() {
    const {title} = this.attrs;
    return (
      <Modal.Header closeButton>
        <Modal.Title>{`${title} - ${this.props.dimension.name}`}</Modal.Title>
      </Modal.Header>
    );
  }

  renderModalBody() {
    let tags = this.props.tags.map(tag => {
      return <option key={tag.id} value={tag.id}>{tag.name}</option>
    });
    tags.unshift(
      <option key="0" value="">----------</option>
    );
    return (
      <Modal.Body>
        <div>
          <Input
            type="text"
            bsStyle={this._validationState('name')}
            help={this._helpText('name')}
            value={this.state.name}
            label="Name"
            ref="name"
            onChange={(e) => this.onTextChange(e, 'name')}/>
          <Input
            type="text"
            bsStyle={this._validationState('code')}
            help={this._helpText('code')}
            value={this.state.code}
            label="Code"
            ref="code"
            onChange={(e) => this.onTextChange(e, 'code')}/>
          <Input
            type="select"
            bsStyle={this._validationState('dimension_tag')}
            help={this._helpText('dimension_tag')}
            value={this.state.dimension_tag}
            label="Tag"
            ref="dimension_tag"
            onChange={(e) => this.onTextChange(e, 'dimension_tag')}>
            {tags}
          </Input>

        </div>
      </Modal.Body>
    )
  }

  renderModalFooter() {
    const canSubmit = this.canSubmit();
    return (
      <Modal.Footer>
        <Button onClick={this.onCloseModal}>Close</Button>
        <Button
          bsStyle={this.attrs.submitBtnClassName || 'primary'}
          disabled={!canSubmit}
          onClick={this.onSubmit}>
          {this.attrs.submitBtnText || 'Save'}
        </Button>
      </Modal.Footer>
    );
  }

  canSubmit() {
    if (this.state.isProcessing) {
      return false;
    }

    if (this.attrs.validate) {
      return this.state.name.trim() != '';
    }
    return true;
  }

  onSubmit() {
    const {id} = this.props.dimension;
    let params;
    let url = Urls['dimension:create-ajax']();
    let parentId = null;
    if (id != 0) {
      parentId = id;
    }
    params = {
      name: this.state.name,
      code: this.state.code,
      dimension_tag: this.state.dimension_tag,
      parent_id: parentId,
      parent: parentId
    };
    this.setState({isProcessing: true});
    $.post(url, params, (data)=> {
      this.props.onSuccess(data);
      this._closeModal();
      this.setState({isProcessing: false});
    }).fail(this._onSubmitError);
  }

  onTextChange(e, key) {
    this.setState({
      [key]: e.target.value
    });
  }

  onShowModal(e) {
    e.preventDefault();
    this.setState({showModal: true});
  }

  onCloseModal() {
    if (!this.state.isProcessing) {
      this._closeModal();
    }
  }

  _onSubmitError(responseError) {
    if (responseError.status == 400) {
      let errors = responseError.responseJSON.errors;
      this.setState({
        isProcessing: false,
        errors
      })
    }
  }

  _closeModal() {
    this.setState({
      showModal: false,
      name: '',
      code: '',
      dimension_tag: '',
      errors: {}
    });
  }

  _validationState(field) {
    const errors = this.state.errors || {};
    if (errors[field]) {
      return 'error';
    }
    return null;
  }

  _helpText(field) {
    const errors = this.state.errors || {};
    if (errors[field]) {
      return errors[field];
    }
    return null;
  }
}

export default AddDimension;