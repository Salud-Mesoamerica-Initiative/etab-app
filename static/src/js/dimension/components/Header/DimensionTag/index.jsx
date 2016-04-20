'use strict';

import React from 'react';
import {connect} from 'react-redux';
import cx from "classnames";
import {Tooltip, OverlayTrigger, Modal, Button, Input} from 'react-bootstrap';
import {
  createDimensionTag,
  updateDimensionTag,
  removeDimensionTag
} from '../../../actions/index';

import Tags from './Tags';


class DimensionTag extends React.Component {
  constructor(props) {
    super(props);
    this.attrs = {
      'icon': 'fa-tag',
      'label': 'Tags',
      'id': 'DIMENSION_TAG',
      'title': 'Tags'
    };
    this.state = {
      showModal: false
    };

    this.onShowModal = this.onShowModal.bind(this);
    this.onCloseModal = this.onCloseModal.bind(this);
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
        <Modal.Title>{`${title}`}</Modal.Title>
      </Modal.Header>
    );
  }

  renderModalBody() {
    return (
      <Modal.Body>
        <Tags
          tags={this.props.tags}
          onRemoveDimensionTag={this.props.onRemoveDimensionTag}
          onUpdateDimensionTag={this.props.onUpdateDimensionTag}
          onAddDimensionTag={this.props.onAddDimensionTag}
        />
      </Modal.Body>
    );
  }

  renderModalFooter() {
    return (
      <Modal.Footer>
        <Button onClick={this.onCloseModal}>Close</Button>
      </Modal.Footer>
    );
  }

  onShowModal(e) {
    e.preventDefault();
    this.setState({showModal: true});
  }

  onCloseModal() {
    this.setState({
      showModal: false
    });
  }
}

const mapStateToProps = (state) => {
  const {tags} = state;
  return {
    tags
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
    onAddDimensionTag: (attrs) => {
      dispatch(createDimensionTag(attrs))
    },
    onUpdateDimensionTag: (attrs) => {
      dispatch(updateDimensionTag(attrs))
    },
    onRemoveDimensionTag: (id) => {
      dispatch(removeDimensionTag(id))
    }

  }
};

export default connect(mapStateToProps, mapDispatchToProps)(DimensionTag);