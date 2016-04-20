'use strict';

import React from 'react';
import _ from 'lodash';


class LocationList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    let dom;
    if (this.props.items.length == 0) {
      dom = <h5 className="text-center">No locations found</h5>;
    } else {
      let rows = _.map(this.props.items, (item)=> {
        return (
          <Location
            key={item.id}
            {...item}
          />
        );
      });

      dom = (
        <table className="table">
          <thead>
          <tr>
            <th>Name</th>
            <th>Dimension</th>
          </tr>
          </thead>
          <tbody>
          {rows}
          </tbody>
        </table>
      );
    }

    return (
      <div className="c-location-list">
        {dom}
      </div>
    );
  }
}


const Location = ({id, name, parent}) => {
  let url = Urls['location_detail'](id);
  return (
    <tr>
      <td><a href={url}>{name}</a></td>
      <td>{parent}</td>
    </tr>
  );
};

export default LocationList;