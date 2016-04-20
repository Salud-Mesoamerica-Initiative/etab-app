'use strict';

import React from 'react';
import AddDimension from './AddDimension';
import UpdateDimension from './UpdateDimension';
import RemoveDimension from './RemoveDimension';
import DimensionTag from './DimensionTag/index';


class Toolbar extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    let actions = [
      <AddDimension
        key={`add-dimension`}
        onSuccess={this.props.onAddDimension}
        dimension={this.props.dimension}/>
    ];

    if (this.props.dimension.id){
      actions.push(
        <UpdateDimension
        key={`update-dimension`}
        onSuccess={this.props.onUpdateDimension}
        dimension={this.props.dimension}/>
      );
      actions.push(
        <RemoveDimension
        key={`remove-dimension`}
        onSuccess={this.props.onRemoveDimension}
        dimension={this.props.dimension}/>
      );
    }
    actions.push(
      <DimensionTag key={`dimension-tag`}/>
    );

    return (
      <ul className="list-inline">
        {actions}
      </ul>
    );
  }
}

export default Toolbar;