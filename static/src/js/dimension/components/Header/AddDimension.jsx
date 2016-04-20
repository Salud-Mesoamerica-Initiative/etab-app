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
      tag: '',
      isProcessing: false

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
            value={this.state.name}
            label="Name"
            ref="name"
            onChange={(e) => this.onTextChange(e, 'name')}/>
          <Input
            type="text"
            value={this.state.code}
            label="Code"
            ref="code"
            onChange={(e) => this.onTextChange(e, 'code')}/>
          <Input
            type="select"
            value={this.state.tag}
            label="Tag"
            ref="tag"
            onChange={(e) => this.onTextChange(e, 'tag')}>
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
      tag: this.state.tag,
      parent_id: parentId
    };
    this.setState({isProcessing: true});
    $.post(url, params, (data)=> {
      this.props.onSuccess(data);
      this._closeModal();
      this.setState({isProcessing: false});
    });
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

  _closeModal() {
    this.setState({
      showModal: false,
      name: '',
      code: '',
      tag: ''
    });
  }
}

export default AddDimension;