import React from 'react';

const TRow = ({id, name, parent}) => {
  let url = Urls['location_detail'](id);
  return (
    <tr>
      <td><a href={url}>{name}</a></td>
      <td>{parent}</td>
    </tr>
  )
};

const Table = ({rows}) => (
  <table className="table">
    <thead>
    <tr>
      <th>Name</th>
      <th>Dimension</th>
    </tr>
    </thead>
    <tbody>
    {rows.map((item) => <TRow key={item.id} {...item}/>)}
    </tbody>
  </table>
);

export default Table;