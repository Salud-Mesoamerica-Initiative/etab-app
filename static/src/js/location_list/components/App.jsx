import React from 'react';
import {connect} from 'react-redux';
import Table from './Table';

class App extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    const {isFetching, rows, currentNode} = this.props;
    const isEmpty = rows.length == 0;

    if (currentNode == null) {
      return <h5 className="text-center">Please select a dimension</h5>;
    }

    return (
      <div>
        {
          (isEmpty
              ? (isFetching ? <h5>...</h5> : <h5 className="text-center">No locations found</h5>)
              : this._renderContent(rows)
          )

        }
      </div>
    );
  }

  _renderContent(rows) {
    return (<div>
      <div className="pull-right text-muted" style={{height: 20}}>
        <small>{rows.length} locations</small>
      </div>
      <div className="table-responsive">
        <Table rows={rows}/>
      </div>
    </div>);
  }
}

function mapStateToProps(state) {
  const {currentNode, childrenByNode, children, tree} = state;
  let node = tree[currentNode] || {};
  node = {
    ...node,
    rows: (childrenByNode[currentNode] || []).map((id) => children[id])
  };

  return {
    ...node,
    currentNode
  };
}

export default connect(mapStateToProps)(App);