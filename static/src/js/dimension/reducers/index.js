import {combineReducers} from 'redux';

import treeReducers from '../../utils/treeAjax/reducers/reducers';
import reducers from "./reducers";

const rootReducer = combineReducers({
  ...treeReducers,
  ...reducers
});

export default rootReducer