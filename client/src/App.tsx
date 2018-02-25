import * as React from 'react';
import './App.css';

import AppHeader from './AppHeader';

export default class App extends React.Component {
  render() {
    return (
      <AppHeader>
        <nav className="NavSidebar">
          <p>blah</p>
        </nav>
      </AppHeader>  
    );
  }
}

