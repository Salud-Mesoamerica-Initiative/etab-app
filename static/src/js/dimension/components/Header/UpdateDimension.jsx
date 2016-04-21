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


  setTagAttrs(props) {
    const {name, code, dimension_tag} = this.props.dimension;
    this.setState({
      name: name,
      code: code,
      dimension_tag: dimension_tag
    });
  }

  componentDidMount() {
    this.setTagAttrs(this.props);
  }

  componentDidUpdate(prevProps, prevState) {
    if (prevState.showModal != this.state.showModal && !prevState.showModal) {
      this.setTagAttrs(this.props);
    }
  }

  onSubmit() {
    const {id} = this.props.dimension;
    let params;
    let url = Urls['dimension:update-ajax']();
    params = {
      name: this.state.name,
      code: this.state.code,
      dimension_tag: this.state.dimension_tag,
      id
    };
    this.setState({isProcessing: true});
    $.post(url, params, (data)=> {
      this.props.onSuccess(data);
      this.setState({isProcessing: false});
      this._closeModal();
    }).fail(this._onSubmitError);
  }

  _closeModal() {
    this.setState({
      showModal: false,
      errors: {}
    });
  }
}

export default UpdateDimension;