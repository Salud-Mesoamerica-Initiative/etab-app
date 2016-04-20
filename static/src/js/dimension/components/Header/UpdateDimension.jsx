'use strict';

import React from 'react';
import AddDimension from './AddDimension';


class UpdateDimension extends AddDimension {
  constructor(props) {
    super(props);
    this.attrs = {
      'icon': 'fa-pencil',
      'label': 'Edit dimension',
      'id': 'UPDATE_DIMENSION',
      'title': 'Edit Dimension',
      'validate': true
    };
  }

  componentDidMount() {
    const {name, code, tag} = this.props.dimension;
    this.setState({
      name: name,
      code: code,
      tag: tag
    });
  }

  componentWillReceiveProps(nextProps) {
    if (!this.state.showModal) {
      const {name, code, tag} = nextProps.dimension;
      this.setState({
        name: name,
        code: code,
        tag: tag
      });
    }
  }

  onSubmit() {
    const {id} = this.props.dimension;
    let params;
    let url = Urls['dimension:update-ajax']();
    params = {
      name: this.state.name,
      code: this.state.code,
      tag: this.state.tag,
      id
    };
    this.setState({isProcessing: true});
    $.post(url, params, (data)=> {
      this.props.onSuccess(data);
      this.setState({isProcessing: false});
      this._closeModal();
    });
  }

  _closeModal() {
    this.setState({
      showModal: false
    });
  }
}

export default UpdateDimension;