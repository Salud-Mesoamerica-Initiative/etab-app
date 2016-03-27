'use strict';

import React from 'react';
import _ from 'lodash';


class LocationList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    let items = _.map(this.props.items, (item)=> {
      return (
        <Location
          key={item.id}
          {...item}
        />
      );
    });
    return (
      <div className="c-location-list">
        <ul className="location-list">{items}</ul>
      </div>
    );
  }
}


class Location extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    return (
      <li className="c-location">
        <div className="location-wrapper">
          <div className="prop name">
            <span>{this.props.name}</span>
          </div>
          <div className="prop parent">
            <span>{this.props.parent}</span>
          </div>
        </div>
      </li>
    );
  }
}

export default LocationList;