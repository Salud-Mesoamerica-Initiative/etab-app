'use strict';

import React from 'react';
import UpdateTag from './UpdateTag';
import RemoveTag from './RemoveTag';
import AddTag from './AddTag';

const TagItem = ({tag, onRemoveDimensionTag, onUpdateDimensionTag}) => {
  return (
    <tr>
      <td>{tag.name}</td>
      <td>
        <div className="pull-right">
          <ul className="list-inline">
            <UpdateTag
              tag={tag}
              onSuccess={onUpdateDimensionTag}
            />
            <RemoveTag
              tag={tag}
              onSuccess={onRemoveDimensionTag}
            />
          </ul>
        </div>
      </td>
    </tr>
  );
};

const Tags = ({tags, onAddDimensionTag, onRemoveDimensionTag, onUpdateDimensionTag}) => {
  return (
    <div className="c-tags">
      <div>
        <AddTag onSuccess={onAddDimensionTag} />
      </div>
      <div className="table-content">
        <table className="table">
          <thead>
          <tr>
            <th>Name</th>
            <th></th>
          </tr>
          </thead>
          <tbody>
          {
            tags.map(tag => <TagItem
              key={tag.id}
              onRemoveDimensionTag={onRemoveDimensionTag}
              onUpdateDimensionTag={onUpdateDimensionTag}
              tag={tag}
            />)
          }
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Tags;